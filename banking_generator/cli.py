from __future__ import annotations

import argparse
from pathlib import Path

from .config import GeneratorConfig, PRESETS
from .generator import BankingDataGenerator
from .validation import validate


def main():
    parser = argparse.ArgumentParser(description="Synthetic banking ecosystem generator")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--small", action="store_true")
    group.add_argument("--medium", action="store_true")
    group.add_argument("--large", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output-dir", default="output")
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()

    preset = "small" if args.small or not (args.medium or args.large) else "medium" if args.medium else "large"
    cfg = GeneratorConfig(preset=preset, seed=args.seed, output_dir=Path(args.output_dir) / preset)
    BankingDataGenerator(cfg.seed, cfg.output_dir).generate_all(PRESETS[cfg.preset])
    if args.validate:
        errors = validate(cfg.output_dir)
        if errors:
            raise SystemExit("\n".join(errors))
        print("validation ok")


if __name__ == "__main__":
    main()

