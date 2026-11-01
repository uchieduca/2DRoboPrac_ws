# 2DRoboPrac

本リポジトリは、2D自動走行ロボットの開発を目的としています。フォーク元のコードと以下の記事を参考に、PAI最終課題向けに編集しました。

- 参考記事: [Qiita記事](https://qiita.com/N622/items/6ca879f8b1f9d667e561)

## 実行環境

- Ubuntu
- ROS 2 Humble
- ROS 2ワークスペース: `ros2_ws`

UbuntuにROS 2 Humbleがインストールされていることを前提とします。初めて `rosdep` を使う環境では、依存関係をインストールする前に一度だけ初期化してください。すでに初期化済みの場合は、この手順を省略できます。

```bash
sudo apt install python3-rosdep
sudo rosdep init
rosdep update
```

以下のコマンド例では、リポジトリを `/workspaces/2DRoboPrac_ws` に配置しているものとします。

## 初回セットアップ

Nav2・RViz・ジョイスティック制御など、launchファイルで使用するROSパッケージをインストールしてから、依存関係を解決し、ワークスペースをビルドします。

```bash
cd /workspaces/2DRoboPrac_ws
source /opt/ros/humble/setup.bash
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup ros-humble-rviz2 ros-humble-joy xterm
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

### オムニホイールのジョイスティック操作

このlaunchでは、ジョイスティック入力からオムニホイール用の制御指令を生成し、状態表示を起動します。実機用の `omni_hardware_node` は起動しません。

```bash
ros2 launch omni_control omni_teleop.launch.py
```

## ソース変更後の再ビルド

`nav_dev` または `omni_control` を変更した場合の例です。

```bash
cd /workspaces/2DRoboPrac_ws/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-up-to nav_dev omni_control
source install/setup.bash
```
