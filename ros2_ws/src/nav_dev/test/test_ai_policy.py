import math
import pathlib
import sys
import unittest


sys.path.insert(0, str(pathlib.Path(__file__).parents[1] / "scripts"))

from ai_policy import (  # noqa: E402
    HIDDEN_SIZE,
    INPUT_SIZE,
    MAX_ANGULAR,
    MAX_LINEAR,
    MAX_RANGE,
    SECTOR_COUNT,
    Policy,
    apply_safety_guard,
    make_features,
    obstacle_detour_command,
    scan_to_sectors,
    teacher_action,
)


class AiPolicyTest(unittest.TestCase):
    def test_scan_is_binned_by_angle_and_keeps_nearest_return(self):
        ranges = [MAX_RANGE] * 360
        ranges[180] = 0.8
        ranges[181] = 0.5

        sectors = scan_to_sectors(ranges, -math.pi, 2.0 * math.pi / 360, 0.12)

        self.assertAlmostEqual(sectors[9], 0.5 / MAX_RANGE)
        self.assertEqual(len(sectors), SECTOR_COUNT)

    def test_invalid_scan_returns_are_treated_as_clear(self):
        sectors = scan_to_sectors([math.inf, math.nan, 0.0], -math.pi, 0.1, 0.12)

        self.assertEqual(sectors, [1.0] * SECTOR_COUNT)

    def test_policy_output_is_bounded_and_clear_path_preserves_command(self):
        weights_in = [[0.0] * INPUT_SIZE for _ in range(HIDDEN_SIZE)]
        weights_out = [[0.0] * HIDDEN_SIZE for _ in range(2)]
        bias_hidden = [0.0] * HIDDEN_SIZE
        bias_out = [math.atanh(0.13 / MAX_LINEAR), math.atanh(-0.25)]
        policy = Policy(weights_in, bias_hidden, weights_out, bias_out)
        features = make_features([1.0] * SECTOR_COUNT, 0.13, -0.25)

        linear, angular = policy.predict(features)
        guarded = apply_safety_guard(
            features, linear * MAX_LINEAR, angular * MAX_ANGULAR
        )

        self.assertAlmostEqual(guarded[0], 0.13)
        self.assertAlmostEqual(guarded[1], -0.25)

    def test_emergency_guard_stops_forward_motion_and_turns_to_clear_side(self):
        sectors = [1.0] * SECTOR_COUNT
        sectors[8] = 0.05
        sectors[10] = 0.2
        features = make_features(sectors, MAX_LINEAR, 0.0)

        linear, angular = apply_safety_guard(features, MAX_LINEAR, 0.0)

        self.assertEqual(linear, 0.0)
        self.assertLess(angular, 0.0)

    def test_teacher_slows_for_obstacle_and_preserves_clear_path(self):
        clear = make_features([1.0] * SECTOR_COUNT, MAX_LINEAR, 0.0)
        blocked_sectors = [1.0] * SECTOR_COUNT
        blocked_sectors[8:10] = [0.05, 0.05]
        blocked = make_features(blocked_sectors, MAX_LINEAR, 0.0)

        self.assertAlmostEqual(teacher_action(clear)[0], 1.0)
        self.assertLess(teacher_action(blocked)[0], 0.1)

    def test_detour_starts_toward_clear_side_when_front_is_blocked(self):
        sectors = [1.0] * SECTOR_COUNT
        sectors[8:10] = [0.1, 0.1]
        sectors[4:8] = [0.2] * 4

        command, direction = obstacle_detour_command(sectors, 0)

        self.assertEqual(direction, 1)
        self.assertIsNotNone(command)
        self.assertGreater(command[0], 0.0)
        self.assertGreater(command[1], 0.0)

    def test_detour_stops_close_and_releases_after_obstacle_is_passed(self):
        sectors = [1.0] * SECTOR_COUNT
        sectors[8] = 0.05

        command, direction = obstacle_detour_command(sectors, 1)
        self.assertEqual(command[0], 0.0)
        self.assertGreater(command[1], 0.0)

        command, direction = obstacle_detour_command([1.0] * SECTOR_COUNT, direction)
        self.assertIsNone(command)
        self.assertEqual(direction, 0)

    def test_trained_policy_slows_and_stops_for_close_obstacles(self):
        model_path = pathlib.Path(__file__).parents[1] / "models" / "avoidance_policy.json"
        policy = Policy.load(model_path)
        clear_features = make_features([1.0] * SECTOR_COUNT, MAX_LINEAR, 0.0)
        clear_action = policy.predict(clear_features)
        clear_speed, _ = apply_safety_guard(
            clear_features, clear_action[0] * MAX_LINEAR, clear_action[1]
        )

        near_sectors = [1.0] * SECTOR_COUNT
        near_sectors[8:10] = [0.1, 0.1]
        near_features = make_features(near_sectors, MAX_LINEAR, 0.0)
        near_action = policy.predict(near_features)
        near_speed, _ = apply_safety_guard(
            near_features, near_action[0] * MAX_LINEAR, near_action[1]
        )

        emergency_sectors = [1.0] * SECTOR_COUNT
        emergency_sectors[8:10] = [0.05, 0.05]
        emergency_features = make_features(emergency_sectors, MAX_LINEAR, 0.0)
        emergency_action = policy.predict(emergency_features)
        emergency_speed, _ = apply_safety_guard(
            emergency_features, emergency_action[0] * MAX_LINEAR, emergency_action[1]
        )

        self.assertGreater(clear_speed, 0.1)
        self.assertLess(near_speed, clear_speed * 0.5)
        self.assertEqual(emergency_speed, 0.0)


if __name__ == "__main__":
    unittest.main()