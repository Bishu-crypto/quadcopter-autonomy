# Voyager Theory — State Estimation & Sensor Fusion

This document details the mathematical models of onboard sensors and the sensor fusion algorithms (Complementary and Kalman filters) used to estimate the 3D state of the vehicle.

---

## 1. Sensor Modeling and Error Characteristics

To estimate vehicle states, we must model the imperfections of real physical sensors.

### I. Accelerometers
An accelerometer measures specific force (acceleration minus gravity) in the body frame:
$$a_m^b = a^b - R_n^b g^n + b_a + n_a$$
where:
- $a^b$ is the true linear acceleration.
- $g^n = [0, 0, g]^T$ is the gravity vector in the inertial frame.
- $b_a$ is the accelerometer bias (slowly varying offset).
- $n_a$ is high-frequency Gaussian white noise: $n_a \sim \mathcal{N}(0, \sigma_a^2)$.

### II. Gyroscopes
A gyroscope measures body angular rates:
$$\omega_m^b = \omega^b + b_g + n_g$$
where $b_g$ is the gyroscope bias, and $n_g$ is Gaussian white noise: $n_g \sim \mathcal{N}(0, \sigma_g^2)$. The bias drifts over time, modeled as a random walk driven by white noise:
$$\dot{b}_g = n_{bg}, \quad n_{bg} \sim \mathcal{N}(0, \sigma_{bg}^2)$$

### III. Magnetometers
A magnetometer measures the ambient magnetic field vector:
$$m_m^b = \mathbf{M}_{si} R_n^b m^n + b_{hi} + n_m$$
where:
- $m^n$ is the local Earth magnetic field in the NED frame.
- $b_{hi}$ is the **hard iron** distortion (constant offset from nearby magnets/currents).
- $\mathbf{M}_{si}$ is the $3 \times 3$ **soft iron** distortion matrix (stretching/distortion of the magnetic field sphere).

---

## 2. Attitude Estimation

To estimate Roll ($\phi$) and Pitch ($\theta$), we fuse accelerometer and gyroscope measurements. Gyro integration is accurate in the short term but drifts; accelerometer gravity vectors are noisy in the short term due to vibrations but stable in the long term.

### I. Standard Complementary Filter
For a single axis, the complementary filter is:
$$\theta_{\text{est}, k} = \alpha (\theta_{\text{est}, k-1} + q_m \Delta t) + (1 - \alpha) \theta_{\text{acc}, k}$$
where:
- $\theta_{\text{acc}} = \arctan2(a_{y,m}, a_{z,m})$ is the angle derived from gravity.
- $\alpha = \frac{\tau_f}{\tau_f + \Delta t}$ is a weighting coefficient ($\tau_f$ is the filter time constant).

### II. Madgwick Complementary Filter
To estimate full 3D attitude without Euler singularities, Voyager uses the **Madgwick Filter** in quaternion form ($q = [q_1, q_2, q_3, q_4]^T$).

1. **Orientation from Gyro Integration**:
   The quaternion derivative from gyro measurements $\omega = [0, p_m, q_m, r_m]^T$ is:
   $$\dot{q}_{\omega, k} = \frac{1}{2} q_{k-1} \otimes \omega_k$$

2. **Orientation from Accelerometer/Magnetometer**:
   We define a cost function $f$ that measures the alignment between the measured gravity/magnetic vectors and their known values in the inertial frame. We find the optimal quaternion by taking a single gradient descent step:
   $$q_{\nabla, k} = q_{k-1} - \mu_k \frac{\nabla f}{\|\nabla f\|}$$

3. **Flipped Fusion Step**:
   The Madgwick filter fuses the gyro integration and the gradient descent step using a filter gain $\beta$:
   $$q_k = q_{k-1} + \left( \dot{q}_{\omega, k} - \beta \frac{\nabla f}{\|\nabla f\|} \right) \Delta t$$
   where $\beta = \sqrt{3/4} \tilde{\omega}_{\max}$ (representing gyro measurement noise). The resulting quaternion $q_k$ is then normalized.

---

## 3. Position and Velocity Estimation (EKF)

For full 3D translation estimation (Position $p^n$ and Velocity $v^n$), we implement an **Extended Kalman Filter (EKF)**. The EKF fuses double-integrated accelerometer readings with absolute measurements from GPS and a barometer.

```
       ┌──────────────────┐
       │   Accelerometer  │──┐
       │     & Gyro       │  │ (High rate: 1000 Hz)
       └──────────────────┘  ▼
                           ┌──────────────────┐  State Estimate
                           │  EKF Predict Step│────────────────► [x, y, z, vx, vy, vz]
                           └────────▲─────────┘
                                    │ (Low rate: 5 - 10 Hz)
       ┌──────────────────┐         │
       │   Barometer      │─────────┤
       │     & GPS        │         │
       └──────────────────┘         ▼
                           ┌──────────────────┐
                           │   EKF Update Step│
                           └──────────────────┘
```

### State Vector
The EKF tracks a 15-element state vector:
$$x = \begin{bmatrix} p^n \\ v^n \\ \theta_{err} \\ b_a \\ b_g \end{bmatrix}_{15 \times 1}$$
where $p^n$ is 3D position, $v^n$ is 3D velocity, $\theta_{err}$ is the attitude error vector, $b_a$ is accelerometer bias, and $b_g$ is gyro bias.

### EKF Cycle

#### Phase 1: Prediction (Propagation)
At the high IMU rate (e.g., 400Hz), we integrate the state equations forward:
$$\hat{x}_{k|k-1} = f(\hat{x}_{k-1|k-1}, u_k)$$
where $u_k = [a_m^b, \omega_m^b]^T$. We propagate the state covariance matrix $P$:
$$P_{k|k-1} = F_k P_{k-1|k-1} F_k^T + Q_k$$
where:
- $F_k = \left. \frac{\partial f}{\partial x} \right|_{\hat{x}_{k-1}}$ is the state transition Jacobian.
- $Q_k$ is the process noise covariance matrix.

#### Phase 2: Correction (Measurement Update)
When a slow measurement $z_k$ arrives (e.g., GPS at 10Hz, Barometer at 50Hz):
1. **Compute Kalman Gain**:
   $$K_k = P_{k|k-1} H_k^T \left( H_k P_{k|k-1} H_k^T + R_k \right)^{-1}$$
   where $H_k = \left. \frac{\partial h}{\partial x} \right|_{\hat{x}_{k|k-1}}$ is the measurement model Jacobian, and $R_k$ is the measurement noise covariance.
2. **Update State Estimate**:
   $$\hat{x}_{k|k} = \hat{x}_{k|k-1} + K_k \left( z_k - h(\hat{x}_{k|k-1}) \right)$$
3. **Update Covariance Matrix**:
   $$P_{k|k} = (I - K_k H_k) P_{k|k-1}$$

---

## 4. Calibration Algorithms

Filters assume calibrated inputs. Voyager performs two calibration steps:

### I. Accelerometer 6-Point Calibration
We place the vehicle static on 6 orthogonal orientations ($X, -X, Y, -Y, Z, -Z$ facing up). The measured force should equal $1g$ ($9.81 \text{ m/s}^2$). We fit scale factor $S_a$ and bias $b_a$ using a least-squares solver:
$$a_{\text{calibrated}} = S_a (a_{\text{raw}} - b_a)$$

### II. Magnetometer Ellipsoid Fitting
Rotating the quadcopter through all axes mapping magnetic readings creates an ellipsoid. An ideal magnetometer maps to a perfect sphere of radius equal to local magnetic field strength. We calculate the hard-iron offset $b_{hi}$ and soft-iron matrix $\mathbf{M}_{si}$ by fitting the ellipsoid to a sphere:
$$m_{\text{calibrated}} = \mathbf{M}_{si} (m_{\text{raw}} - b_{hi})$$
