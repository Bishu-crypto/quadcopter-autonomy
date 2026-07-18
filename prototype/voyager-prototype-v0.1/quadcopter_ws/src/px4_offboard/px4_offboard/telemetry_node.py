#!/usr/bin/env python3
"""
Telemetry Node — Phase 0
Subscribes to PX4 vehicle odometry and prints live drone state.
Author: Vaibhav | IIT Madras
Repo: github.com/Bishu-crypto/quadcopter-autonomy
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from px4_msgs.msg import VehicleOdometry, VehicleStatus


class TelemetryNode(Node):

    def __init__(self):
        super().__init__('telemetry_node')

        # PX4 requires BEST_EFFORT QoS
        qos = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            history=HistoryPolicy.KEEP_LAST,
            depth=1
        )

        self.odom_sub = self.create_subscription(
            VehicleOdometry,
            '/fmu/out/vehicle_odometry',
            self.odom_callback,
            qos
        )

        self.status_sub = self.create_subscription(
            VehicleStatus,
            '/fmu/out/vehicle_status_v3',
            self.status_callback,
            qos
        )

        self.armed = False
        self.flight_mode = "UNKNOWN"
        self.get_logger().info("Telemetry node started — listening to PX4...")

    def odom_callback(self, msg):
        x, y, z = msg.position
        vx, vy, vz = msg.velocity
        # z is negative upward in NED frame
        alt = -z
        speed = (vx**2 + vy**2 + vz**2) ** 0.5

        self.get_logger().info(
            f"[POS] x:{x:+.2f} y:{y:+.2f} alt:{alt:.2f}m | "
            f"[SPD] {speed:.2f}m/s | "
            f"[ARM] {'YES' if self.armed else 'NO'} | "
            f"[MODE] {self.flight_mode}"
        )

    def status_callback(self, msg):
        self.armed = msg.arming_state == 2  # ARMING_STATE_ARMED = 2
        nav_states = {
            0: "MANUAL", 1: "ALTCTL", 2: "POSCTL",
            3: "AUTO.MISSION", 4: "AUTO.LOITER", 5: "AUTO.RTL",
            14: "OFFBOARD", 17: "STABILIZED"
        }
        self.flight_mode = nav_states.get(msg.nav_state, f"STATE_{msg.nav_state}")


def main(args=None):
    rclpy.init(args=args)
    node = TelemetryNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
