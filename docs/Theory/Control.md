# Voyager Theory — Control Systems

This document explains the control architecture of Voyager, specifically the cascaded PID loops used for attitude and position tracking, and the mathematical mixer that translates control commands into motor speeds.

---

## 1. Cascaded Control Architecture

Multirotor dynamics are non-linear, underactuated, and tightly coupled. To control them, we exploit **timescale separation**: attitude dynamics (angular acceleration) occur much faster than translational dynamics (linear acceleration).

We implement a cascaded control structure consisting of four loops, running at different frequencies:

```
 Outer Loops (Slower: 50 Hz)                      Inner Loops (Faster: 400 - 1000 Hz)
┌──────────┐  Pos Error  ┌──────────┐  Vel Error  ┌──────────┐  Rate Error  ┌──────────┐  PWM
│ Position │ ──────────► │ Velocity │ ──────────► │ Attitude │ ───────────► │ Attitude │ ────► Mixer
│ (PosPID) │             │ (VelPID) │             │ (AttPID) │              │ (RatePID)│
└──────────┘             └──────────┘             └──────────┘              └──────────┘
     ▲                        ▲                        ▲                         ▲
     │                        │                        │                         │
  Position                 Velocity                 Attitude                 Body Rates
```

1. **Position Controller (Outer-Outer)**: Runs at 50 Hz. Computes desired velocity vector from position error.
2. **Velocity Controller (Outer-Inner)**: Runs at 50 Hz. Computes desired linear acceleration vector from velocity error, which is then mapped to a desired total thrust and attitude (Roll/Pitch).
3. **Attitude Controller (Inner-Outer)**: Runs at 250 - 400 Hz. Computes desired body angular rates ($p_d, q_d, r_d$) from attitude error.
4. **Attitude Rate Controller (Inner-Inner)**: Runs at 400 - 1000 Hz. Computes desired torques ($\tau_x, \tau_y, \tau_z$) from angular rate error.

---

## 2. PID Controller Formulation

Each individual controller in the cascade is based on a Proportional-Integral-Derivative (PID) algorithm.

### Continuous Time Definition
$$u(t) = K_p e(t) + K_i \int_{0}^{t} e(\tau) d\tau + K_d \frac{de(t)}{dt}$$
where $e(t) = r(t) - y(t)$ is the error (setpoint $r$ minus measured process variable $y$).

### Discrete Time Implementation
In firmware, we run the loops at a sample time $\Delta t$. The discrete PID equations are:
$$u_k = P_k + I_k + D_k$$
$$P_k = K_p e_k$$
$$I_k = I_{k-1} + K_i e_k \Delta t$$
$$D_k = K_d \frac{e_k - e_{k-1}}{\Delta t}$$

### I. Derivative Low-Pass Filter
Direct numerical differentiation amplification of high-frequency sensor noise. To mitigate this, we apply a first-order low-pass filter to the derivative term:
$$D_k = \alpha \left( K_d \frac{e_k - e_{k-1}}{\Delta t} \right) + (1 - \alpha) D_{k-1}$$
where $\alpha \in (0, 1]$ is the smoothing factor. The smoothing factor is calculated from the cut-off frequency $f_c$ (Hz):
$$\alpha = \frac{\Delta t}{\tau_c + \Delta t} = \frac{2\pi f_c \Delta t}{1 + 2\pi f_c \Delta t}$$

### II. Integral Anti-Windup
If the actuators saturate (e.g., motors reach maximum throttle), the error cannot be reduced quickly, causing the integral term to grow unbounded. This is called **integral windup**. We use two methods to prevent it:

1. **Integral Clamping**: Constrain the integrator value to a maximum limit:
   $$I_k = \text{clamp}(I_k, -I_{\max}, I_{\max})$$
2. **Conditional Integration**: Disable integration if the controller output $u_k$ is saturated AND the error $e_k$ has the same sign as $u_k$ (indicating the error is continuing to drive the output into saturation).

---

## 3. Position to Attitude Translation

The velocity loop outputs a desired 3D acceleration vector $a_d = [a_{x,d}, a_{y,d}, a_{z,d}]^T$ (in the inertial frame). We must convert this into a desired total thrust magnitude $T$ and attitude angles $(\phi_d, \theta_d)$.

### Desired Thrust Magnitude
First, we offset the desired acceleration by gravity:
$$a_{\text{net}} = a_d - \begin{bmatrix} 0 \\ 0 \\ -g \end{bmatrix} = \begin{bmatrix} a_{x,d} \\ a_{y,d} \\ a_{z,d} + g \end{bmatrix}$$
The total thrust $T$ in Newtons required is:
$$T = m \| a_{\text{net}} \|$$

### Desired Roll & Pitch
To extract the target roll ($\phi_d$) and pitch ($\theta_d$) angles, we project $a_{\text{net}}$ onto the yaw-rotated intermediate frame. Given a target yaw heading $\psi_d$, the target acceleration vector in the yaw-rotated frame is:
$$\begin{bmatrix} a_x^\psi \\ a_y^\psi \\ a_z^\psi \end{bmatrix} = \begin{bmatrix} \cos\psi_d & \sin\psi_d & 0 \\ -\sin\psi_d & \cos\psi_d & 0 \\ 0 & 0 & 1 \end{bmatrix} a_{\text{net}}$$

From this, the desired attitude angles are:
$$\theta_d = \arctan2\left( a_x^\psi, a_z^\psi \right)$$
$$\phi_d = \arctan2\left( -a_y^\psi, \sqrt{(a_x^\psi)^2 + (a_z^\psi)^2} \right)$$

---

## 4. Motor Mixer Mathematics

The attitude rate controller outputs desired roll torque ($\tau_x$), pitch torque ($\tau_y$), yaw torque ($\tau_z$), and the velocity controller outputs vertical thrust ($T$). The motor mixer maps these virtual control inputs $\mathbf{u} = [T, \tau_x, \tau_y, \tau_z]^T$ to the 4 individual rotor forces $\mathbf{f} = [f_1, f_2, f_3, f_4]^T$.

From the aerodynamic moment definitions (in X-configuration with arm length $L$ and drag-to-thrust ratio $c = k_m / k_f$):
$$\begin{bmatrix} T \\ \tau_x \\ \tau_y \\ \tau_z \end{bmatrix} = \begin{bmatrix} 
1 & 1 & 1 & 1 \\
\frac{\sqrt{2}}{2} L & -\frac{\sqrt{2}}{2} L & -\frac{\sqrt{2}}{2} L & \frac{\sqrt{2}}{2} L \\
\frac{\sqrt{2}}{2} L & \frac{\sqrt{2}}{2} L & -\frac{\sqrt{2}}{2} L & -\frac{\sqrt{2}}{2} L \\
c & -c & c & -c
\end{bmatrix} \begin{bmatrix} f_1 \\ f_2 \\ f_3 \\ f_4 \end{bmatrix}$$

We can represent this as a linear system:
$$\mathbf{u} = \mathbf{M} \mathbf{f}$$

The mixer in firmware solves this for $\mathbf{f}$ by inverting the matrix $\mathbf{M}$ ($\mathbf{f} = \mathbf{M}^{-1} \mathbf{u}$):
$$\mathbf{M}^{-1} = \begin{bmatrix}
0.25 & \frac{\sqrt{2}}{4L} & \frac{\sqrt{2}}{4L} & \frac{1}{4c} \\
0.25 & -\frac{\sqrt{2}}{4L} & \frac{\sqrt{2}}{4L} & -\frac{1}{4c} \\
0.25 & -\frac{\sqrt{2}}{4L} & -\frac{\sqrt{2}}{4L} & \frac{1}{4c} \\
0.25 & \frac{\sqrt{2}}{4L} & -\frac{\sqrt{2}}{4L} & -\frac{1}{4c}
\end{bmatrix}$$

Expanding the matrix multiplication gives the mixer equations for each motor:
$$\begin{aligned}
f_1 &= 0.25 T + \frac{\sqrt{2}}{4L} \tau_x + \frac{\sqrt{2}}{4L} \tau_y + \frac{1}{4c} \tau_z \\
f_2 &= 0.25 T - \frac{\sqrt{2}}{4L} \tau_x + \frac{\sqrt{2}}{4L} \tau_y - \frac{1}{4c} \tau_z \\
f_3 &= 0.25 T - \frac{\sqrt{2}}{4L} \tau_x - \frac{\sqrt{2}}{4L} \tau_y + \frac{1}{4c} \tau_z \\
f_4 &= 0.25 T + \frac{\sqrt{2}}{4L} \tau_x - \frac{\sqrt{2}}{4L} \tau_y - \frac{1}{4c} \tau_z
\end{aligned}$$

The target force $f_i$ is then mapped to motor command values (PWM/DShot) using the rotor static calibration curve.
