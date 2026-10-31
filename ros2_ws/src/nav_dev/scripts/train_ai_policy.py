#!/usr/bin/env python3
import argparse
import json
import math
import random
from pathlib import Path

from ai_policy import (
    HIDDEN_SIZE,
    INPUT_SIZE,
    MAX_ANGULAR,
    MAX_LINEAR,
    SECTOR_COUNT,
    make_features,
    teacher_action,
)


def make_training_example(rng):
    sectors = [1.0] * SECTOR_COUNT
    obstacle_count = rng.randint(1, 4)
    for obstacle_index in range(obstacle_count):
        if obstacle_index == 0 and rng.random() < 0.7:
            center = rng.randint(6, 11)
        else:
            center = rng.randrange(SECTOR_COUNT)
        radius = rng.randint(0, 2)
        distance = rng.choice((
            rng.uniform(0.06, 0.12),
            rng.uniform(0.12, 0.25),
            rng.uniform(0.25, 0.55),
            rng.uniform(0.55, 0.95),
        ))
        for offset in range(-radius, radius + 1):
            sector = (center + offset) % SECTOR_COUNT
            sectors[sector] = min(sectors[sector], distance)

    linear = rng.uniform(0.0, MAX_LINEAR)
    angular = rng.uniform(-MAX_ANGULAR, MAX_ANGULAR)
    features = make_features(sectors, linear, angular)
    return features, teacher_action(features)


def train(samples, epochs, seed):
    rng = random.Random(seed)
    limit = math.sqrt(6.0 / (INPUT_SIZE + HIDDEN_SIZE))
    weights_in = [
        [rng.uniform(-limit, limit) for _ in range(INPUT_SIZE)]
        for _ in range(HIDDEN_SIZE)
    ]
    bias_hidden = [0.0] * HIDDEN_SIZE
    weights_out = [
        [rng.uniform(-limit, limit) for _ in range(HIDDEN_SIZE)]
        for _ in range(2)
    ]
    bias_out = [0.0, 0.0]
    examples = [make_training_example(rng) for _ in range(samples)]
    learning_rate = 0.018

    for epoch in range(epochs):
        rng.shuffle(examples)
        total_loss = 0.0
        for features, target in examples:
            hidden = [
                math.tanh(sum(weight * value for weight, value in zip(row, features)) + bias)
                for row, bias in zip(weights_in, bias_hidden)
            ]
            output = [
                math.tanh(sum(weight * value for weight, value in zip(row, hidden)) + bias)
                for row, bias in zip(weights_out, bias_out)
            ]
            total_loss += sum((actual - expected) ** 2 for actual, expected in zip(output, target)) / 2.0

            output_delta = [
                (actual - expected) * (1.0 - actual * actual)
                for actual, expected in zip(output, target)
            ]
            hidden_delta = [
                sum(weights_out[out_index][hidden_index] * output_delta[out_index] for out_index in range(2))
                * (1.0 - hidden[hidden_index] * hidden[hidden_index])
                for hidden_index in range(HIDDEN_SIZE)
            ]

            for out_index in range(2):
                for hidden_index in range(HIDDEN_SIZE):
                    weights_out[out_index][hidden_index] -= (
                        learning_rate * output_delta[out_index] * hidden[hidden_index]
                    )
                bias_out[out_index] -= learning_rate * output_delta[out_index]

            for hidden_index in range(HIDDEN_SIZE):
                for input_index in range(INPUT_SIZE):
                    weights_in[hidden_index][input_index] -= (
                        learning_rate * hidden_delta[hidden_index] * features[input_index]
                    )
                bias_hidden[hidden_index] -= learning_rate * hidden_delta[hidden_index]

        print(f"epoch {epoch + 1}/{epochs}: mse={total_loss / samples:.5f}")

    return {
        "format": "2drobopac-mlp-v1",
        "inputs": INPUT_SIZE,
        "hidden": HIDDEN_SIZE,
        "outputs": 2,
        "weights_in": weights_in,
        "bias_hidden": bias_hidden,
        "weights_out": weights_out,
        "bias_out": bias_out,
    }


def main():
    parser = argparse.ArgumentParser(description="Train the LiDAR obstacle-avoidance MLP")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "models" / "avoidance_policy.json",
    )
    parser.add_argument("--samples", type=int, default=1800)
    parser.add_argument("--epochs", type=int, default=35)
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()
    if args.samples < 1 or args.epochs < 1:
        parser.error("--samples and --epochs must be positive")

    model = train(args.samples, args.epochs, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(model, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"saved trained policy to {args.output}")


if __name__ == "__main__":
    main()