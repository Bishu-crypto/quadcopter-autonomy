#include "voyager/sim/State.hpp"
#include "voyager/sim/RigidBody.hpp"
#include "voyager/sim/SensorModels.hpp"
#include <iostream>
#include <cassert>
#include <cmath>

using namespace voyager::sim;

// Simple helper to check equality within a tolerance
bool near(double val, double target, double epsilon = 1e-4) {
    return std::abs(val - target) < epsilon;
}

void testAtRestDerivatives() {
    std::cout << "[TEST] Running testAtRestDerivatives..." << std::endl;
    RigidBody rb;
    State state; // at origin, zero velocity, identity orientation, zero rates
    Inputs inputs; // zero thrust, zero torque

    auto deriv = rb.computeDerivatives(state, inputs);

    // Position derivatives = velocity = 0
    assert(near(deriv[0], 0.0));
    assert(near(deriv[1], 0.0));
    assert(near(deriv[2], 0.0));

    // Linear accelerations: ax=0, ay=0, az = -g
    assert(near(deriv[3], 0.0));
    assert(near(deriv[4], 0.0));
    assert(near(deriv[5], -9.81));

    // Quaternion derivative = 0 (since rates = 0)
    assert(near(deriv[6], 0.0));
    assert(near(deriv[7], 0.0));
    assert(near(deriv[8], 0.0));
    assert(near(deriv[9], 0.0));

    // Angular accelerations = 0 (since torques = 0 and rates = 0)
    assert(near(deriv[10], 0.0));
    assert(near(deriv[11], 0.0));
    assert(near(deriv[12], 0.0));

    std::cout << "  -> PASSED: At-rest derivatives verify gravity is -9.81 m/s^2." << std::endl;
}

void testHover() {
    std::cout << "[TEST] Running testHover..." << std::endl;
    RigidBody rb;
    State state;
    state.z = 10.0; // Start at 10m height

    Inputs inputs;
    inputs.total_thrust = rb.mass * rb.g; // Hover thrust = mg

    // Simulate 2 seconds of hover
    double dt = 0.004; // 250 Hz
    int steps = static_cast<int>(2.0 / dt);
    for (int i = 0; i < steps; ++i) {
        rb.stepRK4(state, inputs, dt);
    }

    // Position and velocity should remain near initial values
    assert(near(state.z, 10.0));
    assert(near(state.vz, 0.0));
    assert(near(state.x, 0.0));
    assert(near(state.vx, 0.0));

    std::cout << "  -> PASSED: Quadcopter hovers stably when thrust = mg." << std::endl;
}

void testFreeFall() {
    std::cout << "[TEST] Running testFreeFall..." << std::endl;
    RigidBody rb;
    State state;
    state.z = 100.0; // Start high at 100m to avoid ground effects

    Inputs inputs; // Zero thrust (free fall)

    // Simulate 1.0 second of free fall
    double dt = 0.004;
    double t_total = 1.0;
    int steps = static_cast<int>(t_total / dt);
    for (int i = 0; i < steps; ++i) {
        rb.stepRK4(state, inputs, dt);
    }

    // Analytical solution:
    // With drag included, let's verify acceleration is downwards.
    // If there were no drag, z(t) = z0 - 0.5 * g * t^2 = 100 - 0.5 * 9.81 * 1.0 = 95.095m.
    // With drag: F_drag = -C_drag_z * vz.
    // Let's print out the simulated final height.
    std::cout << "  Simulated height after 1s free fall: " << state.z << " m (Velocity: " << state.vz << " m/s)" << std::endl;
    
    // Check that altitude decreased and velocity is negative
    assert(state.z < 100.0);
    assert(state.vz < 0.0);
    
    // Let's do a simple comparison: height should be close to the drag-affected value
    // (slightly higher than the drag-free analytical 95.095m because drag opposes gravity)
    assert(state.z > 95.0);
    assert(state.z < 96.0);

    std::cout << "  -> PASSED: Free fall matches flight physics constraints." << std::endl;
}

void testTorqueResponse() {
    std::cout << "[TEST] Running testTorqueResponse..." << std::endl;
    RigidBody rb;
    State state;

    Inputs inputs;
    inputs.tau_x = 0.1; // Roll torque

    // Step a few times and verify roll rate (p) increases
    double dt = 0.01;
    for (int i = 0; i < 10; ++i) {
        rb.stepRK4(state, inputs, dt);
    }

    std::cout << "  Roll rate after 0.1s roll torque: " << state.p << " rad/s" << std::endl;
    assert(state.p > 0.0);
    // Pitch and Yaw rates should remain 0
    assert(near(state.q, 0.0));
    assert(near(state.r, 0.0));

    std::cout << "  -> PASSED: Roll rate increases in response to roll torque." << std::endl;
}

void testSensorModels() {
    std::cout << "[TEST] Running testSensorModels..." << std::endl;
    RigidBody rb;
    State state;
    state.z = 100.0;  // 100m altitude
    state.vx = 10.0; // 10 m/s moving North

    Inputs inputs;
    inputs.total_thrust = rb.mass * rb.g; // Hover

    IMUSensor imu;
    BaroSensor baro;
    GPSSensor gps(10.0); // 10 Hz
    MagSensor mag;

    // Run one update step
    double dt = 0.01;
    IMUMeasurement imu_meas = imu.update(state, rb, inputs, dt);
    BaroMeasurement baro_meas = baro.update(state, dt);
    GPSMeasurement gps_meas = gps.update(state, dt);
    MagMeasurement mag_meas = mag.update(state, dt);

    // 1. Verify IMU specific force
    // In hover, specific force in body Z-axis should be close to 1g (9.81 m/s^2) upwards
    std::cout << "  IMU Acceleration (specific force) body Z: " << imu_meas.az << " m/s^2 (nominal ~9.81)" << std::endl;
    assert(near(imu_meas.az, 9.81, 0.5)); // Tolerance allows for white noise

    // 2. Verify Barometer pressure and altitude
    // At 100m, standard pressure should be lower than sea level (101325 Pa)
    std::cout << "  Baro Pressure: " << baro_meas.pressure << " Pa, Altitude: " << baro_meas.altitude << " m" << std::endl;
    assert(baro_meas.pressure < 101325.0);
    assert(near(baro_meas.altitude, 100.0, 10.0)); // Tolerance allows noise

    // 3. Verify GPS update
    // The first update at t = 0.01s should trigger GPS measurement
    assert(gps.isNewDataAvailable());
    std::cout << "  GPS Lat: " << gps_meas.latitude << ", Lon: " << gps_meas.longitude << ", Alt: " << gps_meas.altitude << std::endl;
    std::cout << "  GPS Velocity N: " << gps_meas.vel_n << " m/s (true: 10.0)" << std::endl;
    assert(near(gps_meas.altitude, 100.0, 5.0));
    assert(near(gps_meas.vel_n, 10.0, 0.2)); // Velocity noise standard deviation is 0.05

    // 4. Verify Mag measurements are loaded
    std::cout << "  Magnetometer body field: [" << mag_meas.mx << ", " << mag_meas.my << ", " << mag_meas.mz << "] uT" << std::endl;
    assert(std::abs(mag_meas.mx) > 1.0);

    std::cout << "  -> PASSED: Sensor measurements report correct physical values under noise." << std::endl;
}

int main() {
    std::cout << "===========================================" << std::endl;
    std::cout << "Starting Voyager Sim Rigid Body Test Suite" << std::endl;
    std::cout << "===========================================" << std::endl;

    testAtRestDerivatives();
    testHover();
    testFreeFall();
    testTorqueResponse();
    testSensorModels();

    std::cout << "===========================================" << std::endl;
    std::cout << "ALL TESTS PASSED SUCCESSFULLY!" << std::endl;
    std::cout << "===========================================" << std::endl;
    return 0;
}
