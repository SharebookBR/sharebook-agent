#!/usr/bin/env python3
import argparse
import json
from typing import List


def format_two_arrays(left: List[str], right: List[str], max_chars: int) -> str:
    if len(left) != len(right):
        raise ValueError("left and right must have the same length")
    if max_chars < 5:
        raise ValueError("max_chars must be at least 5")

    right_width = max(len(str(x)) for x in right) if right else 0
    min_gap = 1
    dot = "."
    lines = []

    for l, r in zip(left, right):
        l = str(l).strip()
        r = str(r).strip()

        dots_count = max_chars - len(l) - len(r) - min_gap

        if dots_count < 2:
            allowed_left = max_chars - len(r) - min_gap - 2
            if allowed_left < 1:
                raise ValueError(f"max_chars too small for value '{r}'")
            if len(l) > allowed_left:
                l = l[: max(allowed_left - 1, 0)] + "…" if allowed_left > 1 else l[:1]
            dots_count = max_chars - len(l) - len(r) - min_gap

        line = f"{l} {dot * dots_count}{r}"
        lines.append(line)

    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Format two string arrays into WhatsApp-friendly dotted lines")
    parser.add_argument("--left", required=True, help="JSON array of left strings")
    parser.add_argument("--right", required=True, help="JSON array of right strings")
    parser.add_argument("--max-chars", type=int, default=28, help="Maximum chars per output line (default: 28)")
    args = parser.parse_args()

    left = json.loads(args.left)
    right = json.loads(args.right)

    if not isinstance(left, list) or not isinstance(right, list):
        raise ValueError("--left and --right must be JSON arrays")

    print(format_two_arrays(left, right, args.max_chars))
