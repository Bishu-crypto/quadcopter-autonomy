#pragma once
#include <array>
#include <cmath>

namespace voyager {
namespace sim {

struct State {
    // Position (meters) in Inertial NED Frame
    double x = 0.0;
    double y = 0.0;
    double z = 0.0;

    // Velocity (meters/second) in Inertial NED Frame
    double vx = 0.0;
    double vy = 0.0;
    double vz = 0.0;

    // Orientation Quaternion (w, x, y, z)
    double qw = 1.0;
    double qx = 0.0;
    double qy = 0.0;
    double qz = 0.0;

    // Body Angular Rates (radians/second) in FRD Frame (p: roll rate, q: pitch rate, r: yaw rate)
    double p = 0.0;
    double q = 0.0;
    double r = 0.0;

    // Convert state struct to a standard 13-element array
    std::array<double, 13> toArray() const {
        return {x, y, z, vx, vy, vz, qw, qx, qy, qz, p, q, r};
    }

    // Load state from a 13-element array
    void fromArray(const std::array<double, 13>& arr) {
        x = arr[0];  y = arr[1];  z = arr[2];
        vx = arr[3]; vy = arr[4]; vz = arr[5];
        qw = arr[6]; qx = arr[7]; qy = arr[8]; qz = arr[9];
        p = arr[10]; q = arr[11]; r = arr[12];
    }

    // Normalize the quaternion representation to avoid numerical drift
    void normalizeQuaternion() {
        double norm = std::sqrt(qw*qw + qx*qx + qy*qy + qz*qz);
        if (norm > 1e-9) {
            qw /= norm;
            qx /= norm;
            qy /= norm;
            qz /= norm;
        } else {
            qw = 1.0;
            qx = 0.0;
            qy = 0.0;
            qz = 0.0;
        }
    }
};

struct Inputs {
    double total_thrust = 0.0; // Total thrust force in body -Z direction (N)
    double tau_x = 0.0;        // Roll torque about body X-axis (N*m)
    double tau_y = 0.0;        // Pitch torque about body Y-axis (N*m)
    double tau_z = 0.0;        // Yaw torque about body Z-axis (N*m)
};

} // namespace sim
} // namespace voyager
