#pragma once
#include "State.hpp"
#include <array>

namespace voyager {
namespace sim {

class RigidBody {
public:
    // Physical parameters (matching prototype v0.1 parameters by default)
    double mass = 1.5;             // Vehicle mass (kg)
    double g = 9.81;               // Gravity (m/s^2)
    double Ixx = 0.015;            // Moment of inertia about X-axis (kg*m^2)
    double Iyy = 0.015;            // Moment of inertia about Y-axis (kg*m^2)
    double Izz = 0.025;            // Moment of inertia about Z-axis (kg*m^2)
    
    // Aerodynamic coefficients
    double C_drag_xy = 0.15;       // Drag coefficient for XY translation
    double C_drag_z = 0.30;        // Drag coefficient for Z translation
    double C_rot = 0.05;           // Rotational damping coefficient

    RigidBody() = default;
    RigidBody(double mass, double Ixx, double Iyy, double Izz);

    // Compute derivatives of the 13-state vector
    std::array<double, 13> computeDerivatives(const State& state, const Inputs& inputs) const;

    // Single step integration using Euler's method
    void stepEuler(State& state, const Inputs& inputs, double dt);

    // Single step integration using 4th Order Runge-Kutta (RK4) method
    void stepRK4(State& state, const Inputs& inputs, double dt);

    // Helper functions
    static std::array<double, 9> getRotationMatrix(double qw, double qx, double qy, double qz);
    static std::array<double, 4> getQuaternionDerivative(double qw, double qx, double qy, double qz, double p, double q, double r);
};

} // namespace sim
} // namespace voyager
