from pathlib import Path
import sys

from banking_generator.validation import validate


if __name__ == "__main__":
    errors = validate(Path(sys.argv[1] if len(sys.argv) > 1 else "output/small"))
    if errors:
        raise SystemExit("\n".join(errors))
    print("validation ok")

