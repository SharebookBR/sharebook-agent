#!/usr/bin/env python3
import argparse
import json
import textwrap
from typing import List, Tuple


DEFAULT_MAX_CHARS = 44
MIN_DOTS = 2
MIN_SPACE_BETWEEN = 1


def wrap_text(text: str, width: int) -> List[str]:
    text = str(text).strip()
    if not text:
        return [""]
    if width < 1:
        raise ValueError("wrap width must be at least 1")
    return textwrap.wrap(
        text,
        width=width,
        break_long_words=True,
        break_on_hyphens=False,
        drop_whitespace=True,
    ) or [""]


def choose_widths(left_text: str, right_text: str, max_chars: int) -> Tuple[int, int, List[str], List[str]]:
    best = None

    for right_width in range(8, max_chars - MIN_DOTS - MIN_SPACE_BETWEEN):
        left_width = max_chars - right_width - MIN_DOTS - MIN_SPACE_BETWEEN
        if left_width < 1:
            continue

        left_lines = wrap_text(left_text, left_width)
        right_lines = wrap_text(right_text, right_width)

        connector_len = len(left_lines[-1]) + MIN_SPACE_BETWEEN + MIN_DOTS + len(right_lines[0])
        if connector_len > max_chars:
            continue

        score = (
            max(len(left_lines), len(right_lines)),
            len(left_lines) + len(right_lines),
            abs(left_width - right_width),
            -right_width,
        )

        if best is None or score < best[0]:
            best = (score, left_width, right_width, left_lines, right_lines)

    if best is None:
        raise ValueError(
            f"max_chars too small for pair left='{left_text}' right='{right_text}'"
        )

    _, left_width, right_width, left_lines, right_lines = best
    return left_width, right_width, left_lines, right_lines


def format_pair(left_text: str, right_text: str, max_chars: int) -> List[str]:
    _, right_width, left_lines, right_lines = choose_widths(left_text, right_text, max_chars)

    right_indent = max_chars - right_width
    shared_rows = min(len(left_lines), len(right_lines))
    connector_row = shared_rows - 1
    rows = max(len(left_lines), len(right_lines))
    lines: List[str] = []

    for row in range(rows):
        left_line = left_lines[row] if row < len(left_lines) else ""
        right_line = right_lines[row] if row < len(right_lines) else ""

        if row == connector_row and left_line and right_line:
            dots_count = max_chars - len(left_line) - MIN_SPACE_BETWEEN - len(right_line)
            if dots_count < MIN_DOTS:
                raise ValueError("internal layout error: insufficient dots")
            lines.append(f"{left_line} {'.' * dots_count}{right_line}")
            continue

        if left_line and right_line:
            left_pad = " " * max(max_chars - right_width - len(left_line), 1)
            lines.append(f"{left_line}{left_pad}{right_line}")
        elif left_line:
            lines.append(left_line)
        else:
            lines.append(" " * right_indent + right_line)

    return lines


def format_two_arrays(left: List[str], right: List[str], max_chars: int = DEFAULT_MAX_CHARS) -> str:
    if len(left) != len(right):
        raise ValueError("left and right must have the same length")
    if max_chars < 12:
        raise ValueError("max_chars must be at least 12")

    rendered: List[str] = []
    for index, (l, r) in enumerate(zip(left, right)):
        if index > 0:
            rendered.append("")
        rendered.extend(format_pair(str(l), str(r), max_chars))

    return "\n".join(rendered)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Format two string arrays into dotted two-column blocks")
    parser.add_argument("--left", required=True, help="JSON array of left strings")
    parser.add_argument("--right", required=True, help="JSON array of right strings")
    parser.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS, help=f"Maximum chars per output line (default: {DEFAULT_MAX_CHARS})")
    args = parser.parse_args()

    left = json.loads(args.left)
    right = json.loads(args.right)

    if not isinstance(left, list) or not isinstance(right, list):
        raise ValueError("--left and --right must be JSON arrays")

    print(format_two_arrays(left, right, args.max_chars))
