#include "voyager/sim/SensorModels.hpp"
#include <cmath>

namespace voyager {
namespace sim {

// --- NoiseGenerator ---

NoiseGenerator::NoiseGenerator(unsigned int seed) : generator(seed) {}

double NoiseGenerator::getGaussian(double mean, double stddev) const {
    std::normal_distribution<double> dist(mean, stddev);
    return dist(generator);
}

// --- IMUSensor ---

IMUSensor::IMUSensor(unsigned int seed,
                     double accel_noise_std, double gyro_noise_std,
                     double accel_walk_std, double gyro_walk_std)
    : noise_gen(seed),
      accel_noise_std(accel_noise_std), gyro_noise_std(gyro_noise_std),
      accel_walk_std(accel_walk_std), gyro_walk_std(gyro_walk_std) {
    reset();
}

void IMUSensor::reset() {
    accel_bias_x = 0.0;
    accel_bias_y = 0.0;
    accel_bias_z = 0.0;
    gyro_bias_p = 0.0;
    gyro_bias_q = 0.0;
    gyro_bias_r = 0.0;
}

IMUMeasurement IMUSensor::update(const State& state, const RigidBody& rb, const Inputs& inputs, double dt) {
    // 1. Update random walk biases
    if (dt > 0.0) {
        double dt_sqrt = std::sqrt(dt);
        accel_bias_x += noise_gen.getGaussian(0.0, accel_walk_std) * dt_sqrt;
        accel_bias_y += noise_gen.getGaussian(0.0, accel_walk_std) * dt_sqrt;
        accel_bias_z += noise_gen.getGaussian(0.0, accel_walk_std) * dt_sqrt;

        gyro_bias_p += noise_gen.getGaussian(0.0, gyro_walk_std) * dt_sqrt;
        gyro_bias_q += noise_gen.getGaussian(0.0, gyro_walk_std) * dt_sqrt;
        gyro_bias_r += noise_gen.getGaussian(0.0, gyro_walk_std) * dt_sqrt;
    }

    // 2. Calculate specific force in world frame: a_world - g_world
    // Since positive Z is UP in simulator, gravity vector g_world is [0, 0, -g]^T.
    // Specific force in world frame = [ax_world, ay_world, az_world - (-g)]^T = [ax, ay, az + g]^T.
    auto deriv = rb.computeDerivatives(state, inputs);
    double sf_world_x = deriv[3];
    double sf_world_y = deriv[4];
    double sf_world_z = deriv[5] + rb.g;

    // 3. Rotate specific force to body frame using R^T (transpose of R)
    std::array<double, 9> R = RigidBody::getRotationMatrix(state.qw, state.qx, state.qy, state.qz);
    double sf_body_x = R[0]*sf_world_x + R[3]*sf_world_y + R[6]*sf_world_z;
    double sf_body_y = R[1]*sf_world_x + R[4]*sf_world_y + R[7]*sf_world_z;
    double sf_body_z = R[2]*sf_world_x + R[5]*sf_world_y + R[8]*sf_world_z;

    // 4. Inject noise and bias
    IMUMeasurement meas;
    meas.ax = sf_body_x + accel_bias_x + noise_gen.getGaussian(0.0, accel_noise_std);
    meas.ay = sf_body_y + accel_bias_y + noise_gen.getGaussian(0.0, accel_noise_std);
    meas.az = sf_body_z + accel_bias_z + noise_gen.getGaussian(0.0, accel_noise_std);

    meas.p = state.p + gyro_bias_p + noise_gen.getGaussian(0.0, gyro_noise_std);
    meas.q = state.q + gyro_bias_q + noise_gen.getGaussian(0.0, gyro_noise_std);
    meas.r = state.r + gyro_bias_r + noise_gen.getGaussian(0.0, gyro_noise_std);

    return meas;
}

// --- BaroSensor ---

BaroSensor::BaroSensor(unsigned int seed, double noise_std)
    : noise_gen(seed), noise_std(noise_std) {}

BaroMeasurement BaroSensor::update(const State& state, double /*dt*/) {
    BaroMeasurement meas;
    
    // Altitude z is height above ground (meters)
    double z = state.z;

    // Standard barometric formula: P = P0 * (1 - L * z / T0)^(g * M / (R * L))
    double temp_lapse = 1.0 - (L * z) / T0;
    if (temp_lapse < 0.1) temp_lapse = 0.1; // prevent invalid pressure at extreme altitudes

    double exponent = (g_const * M) / (R_gas * L);
    double true_pressure = P0 * std::pow(temp_lapse, exponent);

    // Add noise to pressure reading
    meas.pressure = true_pressure + noise_gen.getGaussian(0.0, noise_std);

    // Temperature in Celsius: standard temp lapse
    meas.temperature = (T0 - L * z) - 273.15;

    // Barometric altitude reconstructed from the noisy pressure measurement
    meas.altitude = (T0 / L) * (1.0 - std::pow(meas.pressure / P0, 1.0 / exponent));

    return meas;
}

// --- GPSSensor ---

GPSSensor::GPSSensor(unsigned int seed, double update_frequency,
                     double pos_noise_horiz, double pos_noise_vert,
                     double vel_noise)
    : noise_gen(seed), update_frequency(update_frequency),
      pos_noise_horiz(pos_noise_horiz), pos_noise_vert(pos_noise_vert),
      vel_noise(vel_noise) {
    time_since_last_update = 1.0 / update_frequency; // Force initial update on first step
}

GPSMeasurement GPSSensor::update(const State& state, double dt) {
    time_since_last_update += dt;
    double period = 1.0 / update_frequency;

    if (time_since_last_update >= period) {
        time_since_last_update = 0.0;
        new_data_available = true;

        // Flat-Earth geodetic projection model
        double lat_rad = LAT_ORIGIN * M_PI / 180.0;

        double d_lat = (state.x + noise_gen.getGaussian(0.0, pos_noise_horiz)) / EARTH_RADIUS;
        double d_lon = (state.y + noise_gen.getGaussian(0.0, pos_noise_horiz)) / (EARTH_RADIUS * std::cos(lat_rad));

        last_measurement.latitude = LAT_ORIGIN + d_lat * 180.0 / M_PI;
        last_measurement.longitude = LON_ORIGIN + d_lon * 180.0 / M_PI;
        last_measurement.altitude = state.z + noise_gen.getGaussian(0.0, pos_noise_vert);

        // Velocities in NED frame:
        // vx points North (N), vy points East (E), vz points UP (so -vz points Down / D)
        last_measurement.vel_n = state.vx + noise_gen.getGaussian(0.0, vel_noise);
        last_measurement.vel_e = state.vy + noise_gen.getGaussian(0.0, vel_noise);
        last_measurement.vel_d = -state.vz + noise_gen.getGaussian(0.0, vel_noise);
    } else {
        new_data_available = false;
    }

    return last_measurement;
}

// --- MagSensor ---

MagSensor::MagSensor(unsigned int seed, double noise_std)
    : noise_gen(seed), noise_std(noise_std) {
    
    // Representative local magnetic field (micro-Teslas): North, East, Down
    B_earth = {22.0, 5.0, 42.0};

    // Constant hard-iron sensor offsets (uT)
    hard_iron = {1.5, -2.0, 3.0};

    // Soft-iron distortion matrix (close to identity)
    soft_iron = {
        0.98, 0.02, 0.01,
        0.02, 1.01, -0.01,
        0.01, -0.01, 0.99
    };
}

MagMeasurement MagSensor::update(const State& state, double /*dt*/) {
    // Earth's magnetic field vector rotated to world frame (Z points UP in world, but Down in NED)
    double B_world_x = B_earth[0]; // North
    double B_world_y = B_earth[1]; // East
    double B_world_z = -B_earth[2]; // UP is negative Down

    // Rotate field to body frame: B_body = R^T * B_world
    std::array<double, 9> R = RigidBody::getRotationMatrix(state.qw, state.qx, state.qy, state.qz);
    double B_body_x = R[0]*B_world_x + R[3]*B_world_y + R[6]*B_world_z;
    double B_body_y = R[1]*B_world_x + R[4]*B_world_y + R[7]*B_world_z;
    double B_body_z = R[2]*B_world_x + R[5]*B_world_y + R[8]*B_world_z;

    // Apply hard-iron offset in body frame
    double h_x = B_body_x + hard_iron[0];
    double h_y = B_body_y + hard_iron[1];
    double h_z = B_body_z + hard_iron[2];

    // Apply soft-iron transformation matrix
    double m_x = soft_iron[0]*h_x + soft_iron[1]*h_y + soft_iron[2]*h_z;
    double m_y = soft_iron[3]*h_x + soft_iron[4]*h_y + soft_iron[5]*h_z;
    double m_z = soft_iron[6]*h_x + soft_iron[7]*h_y + soft_iron[8]*h_z;

    // Add sensor noise
    MagMeasurement meas;
    meas.mx = m_x + noise_gen.getGaussian(0.0, noise_std);
    meas.my = m_y + noise_gen.getGaussian(0.0, noise_std);
    meas.mz = m_z + noise_gen.getGaussian(0.0, noise_std);

    return meas;
}

} // namespace sim
} // namespace voyager
