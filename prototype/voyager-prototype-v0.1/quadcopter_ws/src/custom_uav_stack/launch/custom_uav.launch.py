from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='custom_uav_stack',
            executable='simulator_node',
            name='simulator_node',
            output='screen'
        ),
        Node(
            package='custom_uav_stack',
            executable='controller_node',
            name='controller_node',
            output='screen'
        ),
        Node(
            package='custom_uav_stack',
            executable='gcs_bridge_node',
            name='gcs_bridge_node',
            output='screen'
        )
    ])
