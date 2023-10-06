import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    use_sim_time = LaunchConfiguration("use_sim_time", default="false")

    urdf_file_name = "thorsen_fort_rd25_remote.urdf"
    urdf = os.path.join(os.path.dirname(os.path.abspath(__file__)), urdf_file_name)

    with open(urdf, "r") as infp:
        robot_desc = infp.read()

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "use_sim_time",
                default_value="false",
                description="Use /clock if true",
            ),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                name="robot_state_publisher",
                namespace="tractor/description",
                output="screen",
                parameters=[
                    {"use_sim_time": use_sim_time, "robot_description": robot_desc}
                ],
                arguments=[urdf],
            ),
            Node(
                package="joint_state_publisher",
                executable="joint_state_publisher",
                name="joint_state_publisher",
                namespace="tractor/description",
                parameters=[
                    {
                        "use_sim_time": use_sim_time,
                        "source_list": ["/hitch_joint_state"],
                    }
                ],
                arguments=["--ros-args", "--log-level", "ERROR"],
            ),
        ]
    )
