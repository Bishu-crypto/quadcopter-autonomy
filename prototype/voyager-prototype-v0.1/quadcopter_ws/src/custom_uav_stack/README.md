# Custom UAV Stack (Prototype Proof of Concept)

> [!NOTE]
> **Status: Frozen Prototype**  
> This project has successfully served its purpose as an initial proof of concept for our autonomous UAV stack. It is now frozen and preserved here for historical reference and educational purposes. Active development has shifted to the **Voyager** architecture.

## Overview

This repository contains the `custom_uav_stack` ROS 2 package, which was built to demonstrate a complete, closed-loop autonomous flight control and simulation loop from first principles. It includes:

* **6-DOF Quadcopter Physics Simulator**: A custom rigid-body dynamics model of a multirotor simulating translation, rotation, gravity, thrust, and aerodynamical drag/moments.
* **Flight Controller Node**: A cascaded PID controller handling target attitudes, rates, and position-hold/waypoint tracking.
* **Ground Control Station (GCS) Bridge**: A telemetry bridge linking the ROS 2 network with an external Python/Qt-based Ground Control Station.
* **ROS 2 Integration**: Topics, messages, and nodes communicating via ROS 2 Humble.

## Key Nodes

1. **`simulator_node.py`**: Runs the 6-DOF physics equations at a fixed step rate, publishing IMU, Odometry, and sensor measurements.
2. **`controller_node.py`**: Computes motor thrust commands based on the error between desired setpoints (waypoints) and current state estimates.
3. **`gcs_bridge_node.py`**: Encapsulates and serializes telemetry packets, routing them to the GCS and receiving control overrides and waypoint commands.

## Running the Prototype

To launch the prototype stack, run:

```bash
colcon build --packages-select custom_uav_stack
source install/setup.bash
ros2 launch custom_uav_stack bringup.launch.py
```
