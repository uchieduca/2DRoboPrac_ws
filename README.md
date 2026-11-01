# About
This is a repositry for developing 2D auto drive robot.
Description is in following article.
https://qiita.com/N622/items/6ca879f8b1f9d667e561


# Ubuntu のターミネーター用のコード

１．初回起動時
cd /workspaces/2DRoboPrac_ws
source /opt/ros/humble/setup.bash

cd ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash


初回にROS 2のシミュレーションを起動
ros2 launch nav_dev nav_teleop.launch.py

3. AI障害物回避付きのシミュレーションを起動
ros2 launch nav_dev nav_nav2.launch.py

4. オムニホイール制御ノードを起動
ros2 launch omni_control omni_teleop.launch.py

5. 2回目以降に使う基本手順
cd /workspaces/2DRoboPrac_ws
source /opt/ros/humble/setup.bash
source /workspaces/2DRoboPrac_ws/ros2_ws/install/setup.bash

6. 2回目以降に走行シミュレーションを起動
ros2 launch nav_dev nav_teleop.launch.py

7. 2回目以降にAI回避シミュレーションを起動
ros2 launch nav_dev nav_nav2.launch.py

8. 2回目以降にオムニホイール制御を起動
ros2 launch omni_control omni_teleop.launch.py

9. 変更後に再ビルドする場合
cd /workspaces/2DRoboPrac_ws/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select nav_dev omni_control
source install/setup.bash

10. 最短の起動例
cd /workspaces/2DRoboPrac_ws
source /opt/ros/humble/setup.bash
source /workspaces/2DRoboPrac_ws/ros2_ws/install/setup.bash
ros2 launch nav_dev nav_teleop.launch.py

※使うときは、必要な起動コマンドだけを選んで実行。
