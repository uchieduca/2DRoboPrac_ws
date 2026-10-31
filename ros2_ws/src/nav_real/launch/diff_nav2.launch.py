import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node

def generate_launch_description():
    nav_dev_dir = get_package_share_directory('nav_dev')
    
    #joint_state_pubの起動
    states_pub_node = Node(
                package='nav_real',
                executable='states_pub_node',
                parameters=[{
                    'qos_overrides./odom.publisher.durability': 'transient_local'
                }],
                output='screen'
                )
    
    #RViz表示用URDFを読み込む
    urdf = os.path.join(
        get_package_share_directory('nav_dev'),
        'models', 'LidarRobo', 'robot.urdf')
    with open(urdf, encoding='utf-8') as urdf_file:
        robot_description = urdf_file.read()

    #robot_state_publsherの起動設定
    robot_state_publisher = Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='both',
                parameters=[{'robot_description': robot_description}])
    
    #nav2の地図のパスを取得
    map_dir = LaunchConfiguration(
        'map',
        default=os.path.join(
            get_package_share_directory('nav_dev'),
            'maps','test_map2',
            'test_map2.yaml'))

    #nav2のパラメータのパスを取得
    param_file_name = 'nav_nav2.yaml'
    param_dir = LaunchConfiguration(
        'params_file',
        default=os.path.join(
            get_package_share_directory('nav_dev'),
            'params',
            param_file_name))

    #nav2のランチファイルのパスを取得
    nav2_launch_file_dir = os.path.join(get_package_share_directory('nav2_bringup'), 'launch')

    #rviz2の設定フィルのパスを取得
    rviz_config_dir = os.path.join(
        nav_dev_dir,
        'config',
        'nav_nav2.rviz')
    
    #nav2の起動設定
    nav2 = IncludeLaunchDescription(
            PythonLaunchDescriptionSource([nav2_launch_file_dir, '/bringup_launch.py']),
            launch_arguments={
                'map': map_dir,
                'params_file': param_dir}.items(),
        )
    
    #rviz2の起動設定
    rviz2 = Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_dir],
            output='screen')
    
   
    
    return LaunchDescription([
        states_pub_node,

        robot_state_publisher,

        DeclareLaunchArgument(
            'map',
            default_value=map_dir,
            description='Full path to map file to load'),

        DeclareLaunchArgument(
            'params_file',
            default_value=param_dir,
            description='Full path to param file to load'),

        nav2,
        rviz2,
    ])
