#!/usr/bin/env python3
import time

import rclpy
from geometry_msgs.msg import Twist
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

from ai_policy import MAX_ANGULAR, MAX_LINEAR, Policy, apply_safety_guard, make_features, scan_to_sectors


class AiObstacleAvoidance(Node):
    def __init__(self):
        super().__init__("ai_obstacle_avoidance")
        self.declare_parameter("model_path", "")
        model_path = self.get_parameter("model_path").get_parameter_value().string_value
        if not model_path:
            raise ValueError("model_path parameter is required")
        self.policy = Policy.load(model_path)
        self.sectors = None
        self.command = None
        self.scan_time = 0.0
        self.command_time = 0.0

        self.create_subscription(LaserScan, "/scan", self.scan_callback, 10)
        self.create_subscription(Twist, "/cmd_vel", self.command_callback, 10)
        self.publisher = self.create_publisher(Twist, "/cmd_vel_ai", 10)
        self.create_timer(0.05, self.control_callback)
        self.get_logger().info(f"Loaded learned obstacle policy: {model_path}")

    def scan_callback(self, message):
        self.sectors = scan_to_sectors(
            message.ranges,
            message.angle_min,
            message.angle_increment,
            message.range_min,
        )
        self.scan_time = time.monotonic()

    def command_callback(self, message):
        self.command = (message.linear.x, message.angular.z)
        self.command_time = time.monotonic()

    def control_callback(self):
        now = time.monotonic()
        output = Twist()
        if (
            self.sectors is None
            or self.command is None
            or now - self.scan_time > 0.5
            or now - self.command_time > 0.5
        ):
            self.publisher.publish(output)
            return

        features = make_features(self.sectors, *self.command)
        learned_linear, learned_angular = self.policy.predict(features)
        output.linear.x, output.angular.z = apply_safety_guard(
            features,
            learned_linear * MAX_LINEAR,
            learned_angular * MAX_ANGULAR,
        )
        self.publisher.publish(output)


def main(args=None):
    rclpy.init(args=args)
    node = AiObstacleAvoidance()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()