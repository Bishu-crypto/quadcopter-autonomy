#pragma once
#include "State.hpp"
#include "RigidBody.hpp"
#include <array>
#include <random>

namespace voyager {
namespace sim {

// Data Structures for Sensor Outputs

struct IMUMeasurement {
    // Specific force in body frame (m/s^2), which includes gravity
    double ax = 0.0;
    double ay = 0.0;
    double az = 0.0;

    // Angular rate in body frame (rad/s)
    double p = 0.0;
    double q = 0.0;
    double r = 0.0;
};

struct BaroMeasurement {
    double pressure = 101325.0; // static pressure (Pascals)
    double temperature = 15.0;   // temperature (Celsius)
    double altitude = 0.0;       // barometric altitude (meters)
};

struct GPSMeasurement {
    // Global positions (can be represented as latitude/longitude relative to origin)
    double latitude = 0.0;       // degrees
    double longitude = 0.0;      // degrees
    double altitude = 0.0;       // height above ellipsoid (meters)

    // Velocity in NED frame (m/s)
    double vel_n = 0.0;
    double vel_e = 0.0;
    double vel_d = 0.0;
};

struct MagMeasurement {
    // Magnetic field vector in body frame (micro-Teslas, uT)
    double mx = 0.0;
    double my = 0.0;
    double mz = 0.0;
};

// Reusable noise generator using Gaussian and random walk formulations
class NoiseGenerator {
private:
    mutable std::mt19937 generator;
public:
    NoiseGenerator(unsigned int seed = 1337);
    double getGaussian(double mean, double stddev) const;
};

// 1. Inertial Measurement Unit (IMU) Model
class IMUSensor {
private:
    NoiseGenerator noise_gen;
    
    // Standard deviations of white noise
    double accel_noise_std;
    double gyro_noise_std;

    // Random walk standard deviations (bias instability)
    double accel_walk_std;
    double gyro_walk_std;

    // Sensor biases (slowly drift via random walk)
    double accel_bias_x = 0.0;
    double accel_bias_y = 0.0;
    double accel_bias_z = 0.0;

    double gyro_bias_p = 0.0;
    double gyro_bias_q = 0.0;
    double gyro_bias_r = 0.0;

public:
    IMUSensor(unsigned int seed = 1001,
              double accel_noise_std = 0.1, double gyro_noise_std = 0.005,
              double accel_walk_std = 0.002, double gyro_walk_std = 0.0001);

    IMUMeasurement update(const State& state, const RigidBody& rb, const Inputs& inputs, double dt);
    void reset();
};

// 2. Barometer Model
class BaroSensor {
private:
    NoiseGenerator noise_gen;
    double noise_std; // standard deviation of pressure noise in Pa

    // Atmosphere constants
    static constexpr double P0 = 101325.0; // Sea level standard pressure (Pa)
    static constexpr double T0 = 288.15;   // Sea level standard temperature (Kelvin)
    static constexpr double L  = 0.0065;   // Temperature lapse rate (K/m)
    static constexpr double g_const = 9.80665;
    static constexpr double M  = 0.0289644; // Molar mass of dry air (kg/mol)
    static constexpr double R_gas  = 8.31447;  // Universal gas constant (J/(mol*K))

public:
    BaroSensor(unsigned int seed = 1002, double noise_std = 1.5);

    BaroMeasurement update(const State& state, double dt);
};

// 3. GPS Model (Lower frequency update rates)
class GPSSensor {
private:
    NoiseGenerator noise_gen;
    double update_frequency; // Hz
    double time_since_last_update = 0.0;

    // Noise parameters
    double pos_noise_horiz;
    double pos_noise_vert;
    double vel_noise;

    GPSMeasurement last_measurement;
    bool new_data_available = false;

    // Local coordinates origin (reference lat/lon)
    static constexpr double LAT_ORIGIN = 47.397742; // standard SITL latitude
    static constexpr double LON_ORIGIN = 8.545594;  // standard SITL longitude
    static constexpr double EARTH_RADIUS = 6378137.0; // meters

public:
    GPSSensor(unsigned int seed = 1003, double update_frequency = 10.0,
              double pos_noise_horiz = 0.5, double pos_noise_vert = 1.0,
              double vel_noise = 0.05);

    GPSMeasurement update(const State& state, double dt);
    bool isNewDataAvailable() const { return new_data_available; }
};

// 4. Magnetometer Model
class MagSensor {
private:
    NoiseGenerator noise_gen;
    double noise_std;

    // Earth local magnetic field vector (NED) in micro-Teslas (uT)
    std::array<double, 3> B_earth;

    // Hard-iron bias offset
    std::array<double, 3> hard_iron;

    // Soft-iron distortion matrix (3x3 row-major)
    std::array<double, 9> soft_iron;

public:
    MagSensor(unsigned int seed = 1004, double noise_std = 0.5);

    MagMeasurement update(const State& state, double dt);
};

} // namespace sim
} // namespace voyager
