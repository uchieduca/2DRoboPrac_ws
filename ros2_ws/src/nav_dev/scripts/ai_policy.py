import json
import math


SECTOR_COUNT = 18
MAX_RANGE = 4.0
MAX_LINEAR = 0.26
MAX_ANGULAR = 1.0
INPUT_SIZE = SECTOR_COUNT + 2
HIDDEN_SIZE = 16


def scan_to_sectors(ranges, angle_min, angle_increment, range_min):
    sectors = [1.0] * SECTOR_COUNT
    for index, distance in enumerate(ranges):
        if not math.isfinite(distance) or distance < range_min or distance < 0.0:
            continue
        angle = (angle_min + index * angle_increment + math.pi) % (2.0 * math.pi)
        sector = min(int(angle * SECTOR_COUNT / (2.0 * math.pi)), SECTOR_COUNT - 1)
        sectors[sector] = min(sectors[sector], min(distance, MAX_RANGE) / MAX_RANGE)
    return sectors


def make_features(sectors, linear, angular):
    if len(sectors) != SECTOR_COUNT:
        raise ValueError(f"expected {SECTOR_COUNT} LiDAR sectors")
    normalized_ranges = [min(1.0, max(0.0, float(value))) for value in sectors]
    normalized_linear = min(1.0, max(-1.0, linear / MAX_LINEAR))
    normalized_angular = min(1.0, max(-1.0, angular / MAX_ANGULAR))
    return normalized_ranges + [normalized_linear, normalized_angular]


def teacher_action(features):
    sectors = features[:SECTOR_COUNT]
    linear, angular = features[SECTOR_COUNT:]
    front = min(sectors[6:12]) * MAX_RANGE
    left = min(sectors[10:14]) * MAX_RANGE
    right = min(sectors[4:8]) * MAX_RANGE

    if linear > 0.0:
        linear *= min(1.0, max(0.0, (front - 0.28) / 0.62))
    elif linear < 0.0:
        rear = min(sectors[0:2] + sectors[16:18]) * MAX_RANGE
        linear *= min(1.0, max(0.0, (rear - 0.28) / 0.62))

    if front < 0.9:
        turn = 0.75 * (1.0 - front / 0.9)
        angular += turn if left >= right else -turn
    elif left < 0.55 and right > left + 0.12:
        angular -= 0.25 * (0.55 - left) / 0.55
    elif right < 0.55 and left > right + 0.12:
        angular += 0.25 * (0.55 - right) / 0.55

    return [min(1.0, max(-1.0, linear)), min(1.0, max(-1.0, angular))]


def apply_safety_guard(features, linear, angular):
    sectors = features[:SECTOR_COUNT]
    front = min(sectors[6:12]) * MAX_RANGE
    left = min(sectors[10:14])
    right = min(sectors[4:8])

    if linear > 0.0:
        if front <= 0.28:
            linear = 0.0
            angular = max(angular, 0.45) if left >= right else min(angular, -0.45)
        else:
            linear *= min(1.0, (front - 0.28) / 0.42)
    elif linear < 0.0:
        rear = min(sectors[0:2] + sectors[16:18]) * MAX_RANGE
        if rear <= 0.28:
            linear = 0.0
        else:
            linear *= min(1.0, (rear - 0.28) / 0.42)

    return (
        min(MAX_LINEAR, max(-MAX_LINEAR, linear)),
        min(MAX_ANGULAR, max(-MAX_ANGULAR, angular)),
    )


class Policy:
    def __init__(self, weights_in, bias_hidden, weights_out, bias_out):
        if len(weights_in) != HIDDEN_SIZE or any(len(row) != INPUT_SIZE for row in weights_in):
            raise ValueError("invalid input layer dimensions")
        if len(bias_hidden) != HIDDEN_SIZE:
            raise ValueError("invalid hidden layer dimensions")
        if len(weights_out) != 2 or any(len(row) != HIDDEN_SIZE for row in weights_out):
            raise ValueError("invalid output layer dimensions")
        if len(bias_out) != 2:
            raise ValueError("invalid output bias dimensions")
        self.weights_in = weights_in
        self.bias_hidden = bias_hidden
        self.weights_out = weights_out
        self.bias_out = bias_out

    @classmethod
    def load(cls, path):
        with open(path, "r", encoding="utf-8") as model_file:
            model = json.load(model_file)
        if model.get("format") != "2drobopac-mlp-v1":
            raise ValueError("unsupported AI policy format")
        return cls(
            model["weights_in"],
            model["bias_hidden"],
            model["weights_out"],
            model["bias_out"],
        )

    def predict(self, features):
        if len(features) != INPUT_SIZE:
            raise ValueError(f"expected {INPUT_SIZE} policy inputs")
        hidden = [
            math.tanh(sum(weight * value for weight, value in zip(row, features)) + bias)
            for row, bias in zip(self.weights_in, self.bias_hidden)
        ]
        return [
            math.tanh(sum(weight * value for weight, value in zip(row, hidden)) + bias)
            for row, bias in zip(self.weights_out, self.bias_out)
        ]