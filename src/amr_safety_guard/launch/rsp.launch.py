import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

import xacro

def generate_launch_description():

    #Use sim time
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')

    #Robot description
    robot_file = os.path.join(get_package_share_directory('amr_safety_guard'), 'urdf', 'amr_robot.urdf.xacro')
    robot_description = xacro.process_file(robot_file).toxml()

    #Robot state publisher
    rsp = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        parameters=[{'robot_description': robot_description, 'use_sim_time': use_sim_time}],
        output='screen',
    )

    return LaunchDescription([
        rsp,
    ])

