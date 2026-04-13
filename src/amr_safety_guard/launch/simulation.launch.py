from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
import os
from launch.actions import TimerAction

def generate_launch_description():


    #rsp
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('amr_safety_guard'), 'launch', 'rsp.launch.py')
        ),
        launch_arguments = {'use_sim_time': 'true'}.items()
    )


    #World
    world_file = os.path.join(get_package_share_directory('amr_safety_guard'), 'worlds', 'industrial_world.sdf')


    #Start Gazebo
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments = {'gz_args': f'-r {world_file}', 'on_exit_shutdown': 'true'}.items()
    )

    #Spawn the robot
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=['-topic', 'robot_description', '-name', 'amr_robot', 'x', '0.0', 'y', '0.0', '-z', '0.1'],
        output='screen',
    )

    #bridge
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[ #/topic@ros_msg_type[gz_msg_type []->means direction form ros to gz or gz to ros
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock', #clock
            '/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V', #tf
            '/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist', #cmd_vel
            '/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry', #odom
            '/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan', #scan
            '/camera/image_raw@sensor_msgs/msg/Image[gz.msgs.Image', #camera/image_raw
            '/joint_states@sensor_msgs/msg/JointState[gz.msgs.Model',
        ],
        output='screen',
    )
    


    #Launch description
    return LaunchDescription([
        rsp,
        gz_sim,
        TimerAction(period=5.0, actions=[spawn_robot]),
        bridge,
    ])