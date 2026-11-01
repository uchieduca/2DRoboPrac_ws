# About

下記内容を踏まえて、最終課題用に編集を行いました。

This is a repositry for developing 2D auto drive robot.
Description is in following article.
https://qiita.com/N622/items/6ca879f8b1f9d667e561

## 実行環境

- Ubuntu
- ROS 2 Humble
- ROS 2ワークスペース: `ros2_ws`

以下のコマンド例では、リポジトリを `/workspaces/2DRoboPrac_ws` に配置しているものとします。

## 初回セットアップ

依存パッケージをインストールし、ワークスペースをビルドします。

```bash
cd /workspaces/2DRoboPrac_ws
source /opt/ros/humble/setup.bash
cd ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

## 起動方法

初回セットアップ後、または新しいターミナルを開いた後に、次の環境設定を実行してください。各起動コマンドは、環境設定後に実行します。

```bash
source /opt/ros/humble/setup.bash
source /workspaces/2DRoboPrac_ws/ros2_ws/install/setup.bash
```

### シミュレーションとテレオペレーション

```bash
ros2 launch nav_dev nav_teleop.launch.py
```

### AI障害物回避付きシミュレーション

```bash
ros2 launch nav_dev nav_nav2.launch.py
```

### オムニホイール制御

```bash
ros2 launch omni_control omni_teleop.launch.py
```

## ソース変更後の再ビルド

`nav_dev` または `omni_control` を変更した場合の例です。

```bash
cd /workspaces/2DRoboPrac_ws/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select nav_dev omni_control
source install/setup.bash
```
