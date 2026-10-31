# 2D自律走行ロボットとAI障害物回避レポート

## リポジトリの概要と目的

このリポジトリは、ROS 2、Gazebo、STM32などを用いて2次元自律走行ロボットを開発するためのものです。ROS 2側にはシミュレーションとナビゲーション、STM32側にはマイコン制御、CAD側にはロボットの機構設計データが含まれています。

今回の変更では、Gazebo上のロボットがLiDARで周囲を観測し、Nav2の経路追従指令をAIで補正しながら障害物を避ける仕組みを `nav_dev` に追加しました。

## 追加した処理

1. `train_ai_policy.py` が、18方向に分割したLiDAR距離とNav2の速度指令を入力とする小型MLPを学習します。
2. 学習データは、ランダムに配置した合成障害物と、距離に応じて減速・旋回する教師ルールから生成します。したがって、方式は強化学習ではなく教師あり模倣学習です。
3. `ai_obstacle_avoidance.py` が `/scan` と `/cmd_vel` を購読し、学習済みモデルで速度を推論して `/cmd_vel_ai` に出力します。
4. Gazeboブリッジは `/cmd_vel_ai` を受け取るようにし、Nav2の経路計画・目標追従とAIによる局所的な速度補正を組み合わせます。

## 工夫した点

- LiDARの全測距点を18セクターに集約し、入力サイズを抑えつつ近い障害物を特徴として残します。
- 学習データでは前方の近距離障害物を重点的に生成し、接近時の減速・旋回を学びやすくしています。
- 推論結果だけに安全性を委ねず、独立したガードを追加しました。センサーまたは速度指令が0.5秒以上更新されない場合は停止し、前方0.28 m以内の障害物では停止して空き側へ旋回します。速度にも上限を設けています。
- 学習モデルはJSON形式で保存し、推論側は標準Pythonで読み込む構成です。学習に重い外部機械学習ライブラリを必要としません。

## 主な追加・変更ファイル

- `ros2_ws/src/nav_dev/scripts/ai_policy.py`: LiDAR前処理、MLP推論、安全ガード
- `ros2_ws/src/nav_dev/scripts/train_ai_policy.py`: 合成データ生成と学習
- `ros2_ws/src/nav_dev/scripts/ai_obstacle_avoidance.py`: ROS 2推論ノード
- `ros2_ws/src/nav_dev/models/avoidance_policy.json`: 学習済みモデル
- `ros2_ws/src/nav_dev/launch/nav_nav2.launch.py`: AIノードの起動とGazebo指令の接続
- `ros2_ws/src/nav_dev/test/test_ai_policy.py`: 前処理、推論、安全ガードの単体テスト

## 学習・起動方法

リポジトリのルートからモデルを再学習するには、次を実行します。

```bash
python3 ros2_ws/src/nav_dev/scripts/train_ai_policy.py --samples 1800 --epochs 35
```

ROS 2 Humbleなど必要なROS/Gazeboパッケージを用意し、ワークスペースをビルド・sourceした後、シミュレーションを起動します。

```bash
cd ros2_ws
colcon build --packages-select nav_dev
source install/setup.bash
ros2 launch nav_dev nav_nav2.launch.py
```

## 検証状況と注意事項

AIポリシーの単体テスト6件、Python構文チェック、学習済みモデルの近距離障害物に対する減速・停止チェックを実施しました。一方、この作業環境にはROS 2がなく、colconビルドおよびGazebo上での走行試験は未実施です。

学習データは合成環境で、教師ルールも単純です。そのため、この変更だけで多様な動的障害物を確実に回避できることが保証されるわけではありません。実際のGazeboワールドでの検証と、必要に応じた学習データ・モデルの改善が必要です。また、このAIノードはシミュレーションのNav2起動に接続しており、実機の制御経路には接続していません。
