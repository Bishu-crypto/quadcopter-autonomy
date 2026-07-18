# Voyager Theory — Sensor Physics & Noise Modeling

This document is a placeholder for the physical mechanics and numerical models of sensors in the Voyager UAV ecosystem.

---

## Scope of Sensor Modeling

Accurate state estimation requires a deep understanding of the noise, latency, and physical principles of sensors. Key topics to be detailed here include:

1. **Inertial Measurement Units (IMUs)**:
   - **Accelerometers**: Piezoelectric, capacitive, and MEMS architectures. Modeling gravitational vectors, specific forces, white noise, bias stability, thermal drifts, and vibration susceptibility.
   - **Gyroscopes**: MEMS vibratory ring physics. Modeling angular rate inputs, bias walk (random walk), scale-factor errors, and cross-axis sensitivity.
2. **Magnetometers**: Giant Magnetoresistive (GMR) or Hall-effect physics. Detailed mathematical formulations of hard-iron offsets (additive biases) and soft-iron distortions (ellipsoid deformation matrix).
3. **Barometers (Pressure Sensors)**: Piezoresistive pressure cell physics. Modeling the barometric formula to map static pressure to geopotential altitude. Modeling dynamic pressure disturbances (propeller downwash).
4. **Global Positioning System (GPS)**: Satellite triangulation principles. Modeling dilution of precision (DOP), multipath interference, satellite clock errors, ionospheric delays, and low-frequency update latencies (5–10 Hz).
5. **Optical Flow & Rangefinders**: Visual odometer physics, optical flow velocity equations, and distance-sensor physics (Ultrasonic, Infrared, or LiDAR time-of-flight).
6. **Noise Injection (Sim Engine)**: Mathematical algorithms (e.g., Box-Muller transform) to inject realistic Gaussian white noise and random walk drifts into simulator state variables.
