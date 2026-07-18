#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import os
import json
import queue
import threading
import http.server
import socketserver
import numpy as np

from geometry_msgs.msg import PoseStamped, Wrench
from nav_msgs.msg import Odometry
from std_msgs.msg import Float64MultiArray, Bool

# Global clients list for SSE streaming
active_clients = []
gcs_path = ""

class GCSRequestHandler(http.server.BaseHTTPRequestHandler):
    node = None  # Reference to the ROS 2 node

    def log_message(self, format, *args):
        # Prevent default logging to stdout to keep terminal clean
        pass

    def do_GET(self):
        global active_clients, gcs_path
        
        if self.path == '/stream':
            # Server-Sent Events connection
            self.send_response(200)
            self.send_header('Content-Type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Connection', 'keep-alive')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            q = queue.Queue(maxsize=100)
            active_clients.append(q)
            
            try:
                while rclpy.ok():
                    try:
                        # Wait for data with timeout to keep thread responsive
                        data = q.get(timeout=0.1)
                        self.wfile.write(f"data: {data}\n\n".encode('utf-8'))
                        self.wfile.flush()
                    except queue.Empty:
                        # Keep-alive frame
                        self.wfile.write(b": keep-alive\n\n")
                        self.wfile.flush()
            except Exception as e:
                pass
            finally:
                if q in active_clients:
                    active_clients.remove(q)
                    
        else:
            # Serve static files
            file_path = self.path.lstrip('/')
            if not file_path or file_path == '/':
                file_path = 'index.html'
                
            full_path = os.path.join(gcs_path, file_path)
            
            if os.path.exists(full_path) and os.path.isfile(full_path):
                self.send_response(200)
                if file_path.endswith('.html'):
                    self.send_header('Content-Type', 'text/html')
                elif file_path.endswith('.js'):
                    self.send_header('Content-Type', 'application/javascript')
                elif file_path.endswith('.css'):
                    self.send_header('Content-Type', 'text/css')
                elif file_path.endswith('.png'):
                    self.send_header('Content-Type', 'image/png')
                elif file_path.endswith('.svg'):
                    self.send_header('Content-Type', 'image/svg+xml')
                self.end_headers()
                
                with open(full_path, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File Not Found")

    def do_POST(self):
        if self.node is None:
            self.send_response(500)
            self.end_headers()
            return
            
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        try:
            payload = json.loads(post_data)
        except json.JSONDecodeError:
            self.send_response(400)
            self.end_headers()
            return
            
        success = False
        
        if self.path == '/api/arm':
            arm_val = bool(payload.get('arm', False))
            msg = Bool()
            msg.data = arm_val
            self.node.arm_pub.publish(msg)
            success = True
            
        elif self.path == '/api/setpoint':
            # Target position and yaw
            x = float(payload.get('x', 0.0))
            y = float(payload.get('y', 0.0))
            z = float(payload.get('z', 0.0))
            yaw_deg = float(payload.get('yaw', 0.0))
            yaw_rad = np.radians(yaw_deg)
            
            msg = PoseStamped()
            msg.header.stamp = self.node.get_clock().now().to_msg()
            msg.header.frame_id = 'odom'
            
            msg.pose.position.x = x
            msg.pose.position.y = y
            msg.pose.position.z = z
            
            # Yaw representation in quaternion
            msg.pose.orientation.w = np.cos(yaw_rad / 2.0)
            msg.pose.orientation.x = 0.0
            msg.pose.orientation.y = 0.0
            msg.pose.orientation.z = np.sin(yaw_rad / 2.0)
            
            self.node.setpoint_pub.publish(msg)
            success = True
            
        elif self.path == '/api/pid':
            # Tuning values
            gains = payload.get('gains', [])
            if len(gains) == 13:
                msg = Float64MultiArray()
                msg.data = [float(g) for g in gains]
                self.node.pid_pub.publish(msg)
                success = True
                
        elif self.path == '/api/disturbance':
            # Disturbance wrench
            fx = float(payload.get('fx', 0.0))
            fy = float(payload.get('fy', 0.0))
            fz = float(payload.get('fz', 0.0))
            tx = float(payload.get('tx', 0.0))
            ty = float(payload.get('ty', 0.0))
            tz = float(payload.get('tz', 0.0))
            
            msg = Wrench()
            msg.force.x = fx
            msg.force.y = fy
            msg.force.z = fz
            msg.torque.x = tx
            msg.torque.y = ty
            msg.torque.z = tz
            
            self.node.dist_pub.publish(msg)
            success = True
            
        elif self.path == '/api/reset':
            msg = Bool()
            msg.data = True
            self.node.reset_pub.publish(msg)
            success = True
            
        if success:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "success"}).encode('utf-8'))
        else:
            self.send_response(400)
            self.end_headers()

class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    # Enable quick socket address reuse (avoids "address already in use" errors on restarts)
    allow_reuse_address = True

class GCSBridgeNode(Node):
    def __init__(self):
        super().__init__('gcs_bridge_node')
        
        global gcs_path
        # Locate static files directory
        gcs_path = os.path.join(os.path.dirname(__file__), 'gcs')
        if not os.path.exists(gcs_path):
            # Try to resolve via share directory
            try:
                from ament_index_python.packages import get_package_share_directory
                gcs_path = os.path.join(get_package_share_directory('custom_uav_stack'), 'gcs')
            except Exception:
                pass
                
        self.get_logger().info(f"Serving GCS frontend from: {gcs_path}")
        
        # Link ROS node reference to RequestHandler
        GCSRequestHandler.node = self
        
        # --- Publishers ---
        self.arm_pub = self.create_publisher(Bool, '/controller/arm_disarm', 10)
        self.setpoint_pub = self.create_publisher(PoseStamped, '/controller/setpoint', 10)
        self.pid_pub = self.create_publisher(Float64MultiArray, '/controller/pid_tuning', 10)
        self.dist_pub = self.create_publisher(Wrench, '/sim/disturbance', 10)
        self.reset_pub = self.create_publisher(Bool, '/sim/reset', 10)
        
        # --- Subscribers ---
        self.odom_sub = self.create_subscription(
            Odometry, '/sim/odom', self.odom_callback, 10)
        self.telem_sub = self.create_subscription(
            Float64MultiArray, '/controller/telemetry', self.telemetry_callback, 10)
            
        # Internal cache of latest telemetry data
        self.latest_odom = None
        self.latest_telem = None
        
        # Start HTTP server in a separate background thread
        self.server = ThreadedHTTPServer(('0.0.0.0', 8000), GCSRequestHandler)
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
        
        self.get_logger().info("GCS HTTP & SSE server running on http://localhost:8000")

    def odom_callback(self, msg: Odometry):
        self.latest_odom = msg
        self.stream_telemetry()

    def telemetry_callback(self, msg: Float64MultiArray):
        self.latest_telem = msg
        self.stream_telemetry()

    def stream_telemetry(self):
        global active_clients
        if len(active_clients) == 0:
            return
            
        # Package and serialize all state data to JSON
        # Telemetry layout:
        # [px, py, pz, roll, pitch, yaw, target_x, target_y, target_z, target_roll, target_pitch, target_yaw, m1, m2, m3, m4, armed]
        data = {}
        
        if self.latest_telem is not None:
            t = self.latest_telem.data
            if len(t) >= 17:
                data = {
                    "pos": [t[0], t[1], t[2]],
                    "euler": [t[3], t[4], t[5]],
                    "target_pos": [t[6], t[7], t[8]],
                    "target_euler": [t[9], t[10], t[11]],
                    "motors": [t[12], t[13], t[14], t[15]],
                    "armed": bool(t[16] > 0.5)
                }
        elif self.latest_odom is not None:
            # Fallback to odom if telemetry node isn't active
            o = self.latest_odom
            data = {
                "pos": [o.pose.pose.position.x, o.pose.pose.position.y, o.pose.pose.position.z],
                "euler": [0.0, 0.0, 0.0],  # simplified
                "target_pos": [0.0, 0.0, 0.0],
                "target_euler": [0.0, 0.0, 0.0],
                "motors": [0.0, 0.0, 0.0, 0.0],
                "armed": False
            }
            
        if data:
            json_str = json.dumps(data)
            # Push JSON string to all active clients' queues
            for q in list(active_clients):
                try:
                    if q.full():
                        q.get_nowait() # drop oldest frame if client queue is full
                    q.put_nowait(json_str)
                except Exception:
                    pass

    def destroy_node(self):
        # Shutdown server
        self.get_logger().info("Stopping GCS server...")
        self.server.shutdown()
        self.server.server_close()
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = GCSBridgeNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
