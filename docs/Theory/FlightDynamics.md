# Voyager Theory — Flight Dynamics & Kinematics

This document details the mathematical and physical foundations of 6-DOF (Degrees of Freedom) quadcopter flight dynamics.

---

## 1. Coordinate Frames

To model the motion of a quadcopter, we define two primary right-handed coordinate frames:

1. **Inertial Frame ($F^n$)**: The North-East-Down (NED) frame.
   - $X^n$: Points North
   - $Y^n$: Points East
   - $Z^n$: Points Down (aligned with gravity)
2. **Body Frame ($F^b$)**: The Forward-Right-Down (FRD) frame, centered at the vehicle's center of gravity.
   - $X^b$: Points Forward (towards the front arm or intermediate nose)
   - $Y^b$: Points Right
   - $Z^b$: Points Down (normal to the vehicle plane, pointing out the bottom)

```
       Inertial (NED)                     Body (FRD)
             X (North)                      X (Forward)
             ▲                              ▲
             │                              │
             ├───► Y (East)                 ├───► Y (Right)
            /                              /
           ▼                              ▼
           Z (Down)                       Z (Down)
```

---

## 2. Kinematics

Kinematics describes the geometry of motion (position, velocity, attitude) without considering the forces causing it.

### Position and Linear Velocity
The vehicle position in the inertial frame is:
$$p^n = \begin{bmatrix} x \\ y \\ z \end{bmatrix}$$

The linear velocity in the body frame is $v^b = [u, v, w]^T$, where $u$ is surge, $v$ is sway, and $w$ is heave. The linear velocity in the inertial frame is $v^n = [\dot{x}, \dot{y}, \dot{z}]^T$. These are related by the rotation matrix $R_b^n$:
$$v^n = R_b^n v^b$$

### Attitude Representation (Euler Angles)
We represent attitude using Tait-Bryan angles $\eta = [\phi, \theta, \psi]^T$ (Roll, Pitch, Yaw) in the $Z$-$Y$-$X$ (Yaw-Pitch-Roll) rotation sequence:
1. Rotate about $Z^n$ by Yaw $\psi$.
2. Rotate about the intermediate $Y$-axis by Pitch $\theta$.
3. Rotate about the intermediate $X$-axis by Roll $\phi$.

The resulting rotation matrix $R_b^n$ mapping body coordinates to inertial coordinates is:
$$R_b^n = \begin{bmatrix} 
\cos\theta\cos\psi & \sin\phi\sin\theta\cos\psi - \cos\phi\sin\psi & \cos\phi\sin\theta\cos\psi + \sin\phi\sin\psi \\
\cos\theta\sin\psi & \sin\phi\sin\theta\sin\psi + \cos\phi\cos\psi & \cos\phi\sin\theta\sin\psi - \sin\phi\cos\psi \\
-\sin\theta & \sin\phi\cos\theta & \cos\phi\cos\theta 
\end{bmatrix}$$

The inverse mapping is the transpose $R_n^b = (R_b^n)^T$.

### Angular Velocity Kinematics
Let the angular velocity of the body frame relative to the inertial frame, expressed in the body frame, be:
$$\omega^b = \begin{bmatrix} p \\ q \\ r \end{bmatrix}$$
where $p$, $q$, and $r$ represent the body-fixed roll, pitch, and yaw rates, respectively.

The time derivative of the Euler angles $\dot{\eta} = [\dot{\phi}, \dot{\theta}, \dot{\psi}]^T$ is related to $\omega^b$ via:
$$\dot{\eta} = W(\eta) \omega^b$$

Where the kinematic transformation matrix $W(\eta)$ is:
$$W(\eta) = \begin{bmatrix}
1 & \sin\phi\tan\theta & \cos\phi\tan\theta \\
0 & \cos\phi & -\sin\phi \\
0 & \sin\phi\sec\theta & \cos\phi\sec\theta
\end{bmatrix}$$

> [!WARNING]
> Note that $W(\eta)$ becomes singular when $\theta = \pm 90^\circ$ (Pitch = $\pm 90^\circ$). This is known as **gimbal lock**. Future iterations of Voyager FC will transition to quaternions ($q = [q_0, q_1, q_2, q_3]^T$) to avoid this singularity.

---

## 3. Rigid Body Dynamics

Applying the Newton-Euler equations for a rigid body in a rotating frame:

### I. Linear Dynamics
The translational equations of motion in the body frame are:
$$m (\dot{v}^b + \omega^b \times v^b) = F^b$$
where $m$ is the vehicle mass, and $F^b$ is the sum of external forces acting on the vehicle, expressed in the body frame. Expanding this yields:
$$\begin{aligned}
m(\dot{u} + qw - rv) &= F_x^b \\
m(\dot{v} + ru - pw) &= F_y^b \\
m(\dot{w} + pv - qu) &= F_z^b
\end{aligned}$$

### II. Angular Dynamics
The rotational equations of motion in the body frame are:
$$J \dot{\omega}^b + \omega^b \times (J \omega^b) = M^b$$
where $J$ is the $3 \times 3$ rigid-body inertia tensor, and $M^b = [\tau_x, \tau_y, \tau_z]^T$ represents external moments (torques) in the body frame. Assuming the quadcopter is symmetric about its principal axes, the inertia tensor is diagonal:
$$J = \begin{bmatrix}
I_{xx} & 0 & 0 \\
0 & I_{yy} & 0 \\
0 & 0 & I_{zz}
\end{bmatrix}$$

Expanding the angular equations:
$$\begin{aligned}
I_{xx} \dot{p} + (I_{zz} - I_{yy}) qr &= \tau_x \quad (\text{Roll Moment}) \\
I_{yy} \dot{q} + (I_{xx} - I_{zz}) pr &= \tau_y \quad (\text{Pitch Moment}) \\
I_{zz} \dot{r} + (I_{yy} - I_{xx}) pq &= \tau_z \quad (\text{Yaw Moment})
\end{aligned}$$

---

## 4. Forces and Moments (Aerodynamics & Actuation)

The external forces $F^b$ and moments $M^b$ consist of gravity, rotor aerodynamical forces, and aerodynamic drag.

### Gravity
Gravity acts in the positive $Z^n$ direction. Transforming this force into the body frame:
$$F_g^b = R_n^b \begin{bmatrix} 0 \\ 0 \\ mg \end{bmatrix} = \begin{bmatrix} -mg \sin\theta \\ mg \cos\theta \sin\phi \\ mg \cos\theta \cos\phi \end{bmatrix}$$

### Rotor Aerodynamics (X-Configuration)
A quadcopter has 4 rotors spinning at angular velocities $\Omega_i$ (rad/s) where $i \in \{1, 2, 3, 4\}$.
- Rotors 1 and 3 rotate counter-clockwise (CCW).
- Rotors 2 and 4 rotate clockwise (CW).

Each rotor produces a thrust force $f_i$ and drag torque $\tau_{d, i}$ normal to the rotor plane:
$$f_i = k_f \Omega_i^2$$
$$\tau_{d, i} = k_m \Omega_i^2$$
where $k_f$ is the thrust coefficient and $k_m$ is the drag moment coefficient.

For an **X-Configuration** with arm length $L$ (distance from center of gravity to rotor center):

```
       Front
    (4)     (1)  [CW: 2 & 4]
       \   /
        \ /
         X
        / \
       /   \
    (3)     (2)  [CCW: 1 & 3]
```

- **Total Thrust Force**:
  $$F_t^b = \begin{bmatrix} 0 \\ 0 \\ -T \end{bmatrix} = \begin{bmatrix} 0 \\ 0 \\ -\sum_{i=1}^4 f_i \end{bmatrix}$$
- **Rotor Moments**:
  - **Roll torque ($\tau_x$)**: Roll motion is generated by increasing thrust on one side and decreasing it on the other:
    $$\tau_x = \frac{\sqrt{2}}{2} L (f_1 - f_2 - f_3 + f_4)$$
  - **Pitch torque ($\tau_y$)**: Pitch motion is generated by increasing thrust on the rear and decreasing it on the front:
    $$\tau_y = \frac{\sqrt{2}}{2} L (f_1 + f_2 - f_3 - f_4)$$
  - **Yaw torque ($\tau_z$)**: Yaw motion is generated by the mismatch of reactive torques from clockwise and counter-clockwise spinning rotors:
    $$\tau_z = k_m (\Omega_1^2 - \Omega_2^2 + \Omega_3^2 - \Omega_4^2) = \frac{k_m}{k_f} (f_1 - f_2 + f_3 - f_4)$$

### Parasitic Drag
At higher speeds, atmospheric drag opposes translation. We model this as a linear and quadratic drag term:
$$F_{\text{drag}}^b = -\begin{bmatrix} C_{Dx} u |u| \\ C_{Dy} v |v| \\ C_{Dz} w |w| \end{bmatrix}$$
where $C_{Di}$ are the translational drag coefficients.
