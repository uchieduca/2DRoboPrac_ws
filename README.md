<<<<<<< HEAD
## About

下記内容を踏まえて、最終課題用に編集を行った。

This is a repositry for developing 2D auto drive robot.
Description is in following article.
https://qiita.com/N622/items/6ca879f8b1f9d667e561


## Ubuntu のターミネーター用のコード

１．初回起動時
```bash
cd /workspaces/2DRoboPrac_ws
source /opt/ros/humble/setup.bash

=======
# 2DRoboPrac

2D自動走行ロボットの開発リポジトリです。ROS 2によるロボット制御やGazeboシミュレーションなど、開発に使用するソースコードと関連ファイルを管理しています。

プロジェクトの概要は、以下の記事を参照してください。

- [プロジェクト紹介記事（Qiita）](https://qiita.com/N622/items/6ca879f8b1f9d667e561)

## 実行環境

- Ubuntu
- ROS 2 Humble
- ROS 2ワークスペース: `ros2_ws`

以下のコマンド例では、リポジトリを `/workspaces/2DRoboPrac_ws` に配置しているものとします。

## 初回セットアップ

依存パッケージをインストールし、ROS 2ワークスペースをビルドします。

```bash
cd /workspaces/2DRoboPrac_ws
source /opt/ros/humble/setup.bash
>>>>>>> 43c8990 (最終課題)
cd ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

<<<<<<< HEAD
2. 初回にROS 2のシミュレーションを起動
=======
## 起動方法

### シミュレーションとテレオペレーション

>>>>>>> 43c8990 (最終課題)
```bash
ros2 launch nav_dev nav_teleop.launch.py
```

<<<<<<< HEAD
3. AI障害物回避付きのシミュレーションを起動
=======
### AI障害物回避付きシミュレーション

>>>>>>> 43c8990 (最終課題)
```bash
ros2 launch nav_dev nav_nav2.launch.py
```

<<<<<<< HEAD
4. オムニホイール制御ノードを起動
=======
### オムニホイール制御

>>>>>>> 43c8990 (最終課題)
```bash
ros2 launch omni_control omni_teleop.launch.py
```

<<<<<<< HEAD
5. 2回目以降に使う基本手順
```bash
cd /workspaces/2DRoboPrac_ws
=======
### 2回目以降の起動

新しいターミナルを開いたときは、ROS 2とワークスペースの環境を読み込みます。その後、上記の起動コマンドから実行したいものを選んでください。

```bash
>>>>>>> 43c8990 (最終課題)
source /opt/ros/humble/setup.bash
source /workspaces/2DRoboPrac_ws/ros2_ws/install/setup.bash
```

<<<<<<< HEAD
6. 2回目以降に走行シミュレーションを起動
```bash
ros2 launch nav_dev nav_teleop.launch.py
```

7. 2回目以降にAI回避シミュレーションを起動
```bash
ros2 launch nav_dev nav_nav2.launch.py
```

8. 2回目以降にオムニホイール制御を起動
```bash
ros2 launch omni_control omni_teleop.launch.py
```

9. 変更後に再ビルドする場合
=======
## ソース変更後の再ビルド

`nav_dev` または `omni_control` の変更をビルドする例です。

>>>>>>> 43c8990 (最終課題)
```bash
cd /workspaces/2DRoboPrac_ws/ros2_ws
source /opt/ros/humble/setup.bash
colcon build --symlink-install --packages-select nav_dev omni_control
source install/setup.bash
```

<<<<<<< HEAD
10. 最短の起動例
=======
## 最短起動例

環境の読み込みからシミュレーションの起動までを続けて実行します。

>>>>>>> 43c8990 (最終課題)
```bash
cd /workspaces/2DRoboPrac_ws
source /opt/ros/humble/setup.bash
source /workspaces/2DRoboPrac_ws/ros2_ws/install/setup.bash
ros2 launch nav_dev nav_teleop.launch.py
```
<<<<<<< HEAD

※使うときは、必要な起動コマンドだけを選んで実行。
=======
>>>>>>> 43c8990 (最終課題)
