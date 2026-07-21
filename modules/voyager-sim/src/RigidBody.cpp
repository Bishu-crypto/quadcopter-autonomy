#include "voyager/sim/RigidBody.hpp"
#include <cmath>

namespace voyager {
namespace sim {

RigidBody::RigidBody(double mass, double Ixx, double Iyy, double Izz)
    : mass(mass), Ixx(Ixx), Iyy(Iyy), Izz(Izz) {}

std::array<double, 9> RigidBody::getRotationMatrix(double qw, double qx, double qy, double qz) {
    double norm = std::sqrt(qw*qw + qx*qx + qy*qy + qz*qz);
    if (norm > 1e-9) {
        qw /= norm;
        qx /= norm;
        qy /= norm;
        qz /= norm;
    }
    return {
        1.0 - 2.0*(qy*qy + qz*qz), 2.0*(qx*qy - qw*qz), 2.0*(qx*qz + qw*qy),
        2.0*(qx*qy + qw*qz), 1.0 - 2.0*(qx*qx + qz*qz), 2.0*(qy*qz - qw*qx),
        2.0*(qx*qz - qw*qy), 2.0*(qy*qz + qw*qx), 1.0 - 2.0*(qx*qx + qy*qy)
    };
}

std::array<double, 4> RigidBody::getQuaternionDerivative(double qw, double qx, double qy, double qz, double p, double q, double r) {
    return {
        0.5 * (-qx*p - qy*q - qz*r),
        0.5 * ( qw*p + qy*r - qz*q),
        0.5 * ( qw*q - qx*r + qz*p),
        0.5 * ( qw*r + qx*q - qy*p)
    };
}

std::array<double, 13> RigidBody::computeDerivatives(const State& state, const Inputs& inputs) const {
    // Rotation matrix from quaternion
    std::array<double, 9> R = getRotationMatrix(state.qw, state.qx, state.qy, state.qz);

    // Thrust in body frame (acts in positive Z in the prototype's coordinate system)
    double thrust_body_x = 0.0;
    double thrust_body_y = 0.0;
    double thrust_body_z = inputs.total_thrust;

    // Rotate thrust to world frame: thrust_world = R * thrust_body
    double thrust_world_x = R[0]*thrust_body_x + R[1]*thrust_body_y + R[2]*thrust_body_z;
    double thrust_world_y = R[3]*thrust_body_x + R[4]*thrust_body_y + R[5]*thrust_body_z;
    double thrust_world_z = R[6]*thrust_body_x + R[7]*thrust_body_y + R[8]*thrust_body_z;

    // Drag in world frame
    double drag_world_x = -C_drag_xy * state.vx;
    double drag_world_y = -C_drag_xy * state.vy;
    double drag_world_z = -C_drag_z * state.vz;

    // Linear accelerations in world frame (positive Z is UP, gravity pulls down: -g)
    double ax = (thrust_world_x + drag_world_x) / mass;
    double ay = (thrust_world_y + drag_world_y) / mass;
    double az = (thrust_world_z + drag_world_z) / mass - g;

    // Rotational dynamics in body frame (torque inputs and rotational drag/damping)
    double mx = inputs.tau_x - C_rot * state.p;
    double my = inputs.tau_y - C_rot * state.q;
    double mz = inputs.tau_z - C_rot * state.r;

    // Euler's equations for rigid body angular acceleration: w_dot = J_inv * (moments - w x (J * w))
    double w_cross_Jw_x = state.q * state.r * (Izz - Iyy);
    double w_cross_Jw_y = state.p * state.r * (Ixx - Izz);
    double w_cross_Jw_z = state.p * state.q * (Iyy - Ixx);

    double p_dot = (mx - w_cross_Jw_x) / Ixx;
    double q_dot = (my - w_cross_Jw_y) / Iyy;
    double r_dot = (mz - w_cross_Jw_z) / Izz;

    // Quaternion attitude derivative
    std::array<double, 4> dq = getQuaternionDerivative(state.qw, state.qx, state.qy, state.qz, state.p, state.q, state.r);

    // Return the 13-state derivatives
    return {
        state.vx, state.vy, state.vz, // dx/dt, dy/dt, dz/dt
        ax, ay, az,                   // dvx/dt, dvy/dt, dvz/dt
        dq[0], dq[1], dq[2], dq[3],   // dqw/dt, dqx/dt, dqy/dt, dqz/dt
        p_dot, q_dot, r_dot           // dp/dt, dq/dt, dr/dt
    };
}

void RigidBody::stepEuler(State& state, const Inputs& inputs, double dt) {
    if (dt <= 0.0) return;
    std::array<double, 13> deriv = computeDerivatives(state, inputs);
    std::array<double, 13> s_arr = state.toArray();
    for (size_t i = 0; i < 13; ++i) {
        s_arr[i] += deriv[i] * dt;
    }
    state.fromArray(s_arr);
    state.normalizeQuaternion();
}

void RigidBody::stepRK4(State& state, const Inputs& inputs, double dt) {
    if (dt <= 0.0) return;
    const std::array<double, 13> s_init = state.toArray();

    // k1
    State s1 = state;
    std::array<double, 13> k1 = computeDerivatives(s1, inputs);

    // k2
    State s2;
    std::array<double, 13> s_arr;
    for (size_t i = 0; i < 13; ++i) {
        s_arr[i] = s_init[i] + 0.5 * dt * k1[i];
    }
    s2.fromArray(s_arr);
    s2.normalizeQuaternion();
    std::array<double, 13> k2 = computeDerivatives(s2, inputs);

    // k3
    State s3;
    for (size_t i = 0; i < 13; ++i) {
        s_arr[i] = s_init[i] + 0.5 * dt * k2[i];
    }
    s3.fromArray(s_arr);
    s3.normalizeQuaternion();
    std::array<double, 13> k3 = computeDerivatives(s3, inputs);

    // k4
    State s4;
    for (size_t i = 0; i < 13; ++i) {
        s_arr[i] = s_init[i] + dt * k3[i];
    }
    s4.fromArray(s_arr);
    s4.normalizeQuaternion();
    std::array<double, 13> k4 = computeDerivatives(s4, inputs);

    // Combine
    std::array<double, 13> next_state;
    for (size_t i = 0; i < 13; ++i) {
        next_state[i] = s_init[i] + (dt / 6.0) * (k1[i] + 2.0 * k2[i] + 2.0 * k3[i] + k4[i]);
    }
    state.fromArray(next_state);
    state.normalizeQuaternion();
}

} // namespace sim
} // namespace voyager
