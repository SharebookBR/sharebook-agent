#!/usr/bin/env python3
import argparse
import json
import textwrap
from typing import List, Tuple


DEFAULT_MAX_CHARS = 44
MIN_DOTS = 2
MIN_SPACE_BETWEEN = 1
MIN_LEFT_WIDTH = 12
MIN_RIGHT_WIDTH = 8
MAX_SHARED_ROW_IMBALANCE = 8
MAX_LEFTOVER_ROWS_FOR_DOTTED = 0


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


def choose_global_widths(left: List[str], right: List[str], max_chars: int) -> Tuple[int, int]:
    best = None

    for right_width in range(MIN_RIGHT_WIDTH, max_chars - MIN_DOTS - MIN_SPACE_BETWEEN):
        left_width = max_chars - right_width - MIN_DOTS - MIN_SPACE_BETWEEN
        if left_width < MIN_LEFT_WIDTH:
            continue

        total_leftover = 0
        total_rows = 0
        total_balance = 0
        worst_rows = 0
        valid = True

        for left_text, right_text in zip(left, right):
            left_lines = wrap_text(left_text, left_width)
            right_lines = wrap_text(right_text, right_width)
            shared_rows = min(len(left_lines), len(right_lines))
            if shared_rows == 0:
                valid = False
                break

            connector_len = (
                len(left_lines[shared_rows - 1])
                + MIN_SPACE_BETWEEN
                + MIN_DOTS
                + len(right_lines[shared_rows - 1])
            )
            if connector_len > max_chars:
                valid = False
                break

            total_leftover += abs(len(left_lines) - len(right_lines))
            total_rows += len(left_lines) + len(right_lines)
            total_balance += abs(len(left_lines[shared_rows - 1]) - len(right_lines[shared_rows - 1]))
            worst_rows = max(worst_rows, max(len(left_lines), len(right_lines)))

        if not valid:
            continue

        score = (
            total_leftover,
            worst_rows,
            total_rows,
            total_balance,
            abs(left_width - right_width),
            -left_width,
        )

        if best is None or score < best[0]:
            best = (score, left_width, right_width)

    if best is None:
        raise ValueError("max_chars too small for provided arrays")

    _, left_width, right_width = best
    return left_width, right_width


def should_use_dotted(left_lines: List[str], right_lines: List[str]) -> bool:
    shared_rows = min(len(left_lines), len(right_lines))
    if shared_rows == 0:
        return False

    if len(left_lines) > 2 or len(right_lines) > 2:
        return False

    leftover_rows = abs(len(left_lines) - len(right_lines))
    if leftover_rows > MAX_LEFTOVER_ROWS_FOR_DOTTED:
        return False

    connector_balance = abs(len(left_lines[shared_rows - 1]) - len(right_lines[shared_rows - 1]))
    if connector_balance > MAX_SHARED_ROW_IMBALANCE:
        return False

    return True


def format_dotted_pair(left_lines: List[str], right_lines: List[str], max_chars: int, right_width: int) -> List[str]:
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


def format_fallback_pair(left_lines: List[str], right_lines: List[str], max_chars: int, right_width: int) -> List[str]:
    right_indent = max_chars - right_width
    lines: List[str] = []

    lines.extend(left_lines)
    lines.append("." * max_chars)
    for line in right_lines:
        lines.append(" " * right_indent + line)

    return lines


def format_pair(left_text: str, right_text: str, max_chars: int, left_width: int, right_width: int) -> List[str]:
    left_lines = wrap_text(left_text, left_width)
    right_lines = wrap_text(right_text, right_width)

    if should_use_dotted(left_lines, right_lines):
        return format_dotted_pair(left_lines, right_lines, max_chars, right_width)

    return format_fallback_pair(left_lines, right_lines, max_chars, right_width)


def format_two_arrays(left: List[str], right: List[str], max_chars: int = DEFAULT_MAX_CHARS) -> str:
    if len(left) != len(right):
        raise ValueError("left and right must have the same length")
    if max_chars < 12:
        raise ValueError("max_chars must be at least 12")

    left_values = [str(item).strip() for item in left]
    right_values = [str(item).strip() for item in right]
    left_width, right_width = choose_global_widths(left_values, right_values, max_chars)

    rendered: List[str] = []
    for index, (l, r) in enumerate(zip(left_values, right_values)):
        if index > 0:
            rendered.append("")
        rendered.extend(format_pair(l, r, max_chars, left_width, right_width))

    return "\n".join(rendered)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Format two string arrays into resilient two-column dotted blocks")
    parser.add_argument("--left", required=True, help="JSON array of left strings")
    parser.add_argument("--right", required=True, help="JSON array of right strings")
    parser.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS, help=f"Maximum chars per output line (default: {DEFAULT_MAX_CHARS})")
    args = parser.parse_args()

    left = json.loads(args.left)
    right = json.loads(args.right)

    if not isinstance(left, list) or not isinstance(right, list):
        raise ValueError("--left and --right must be JSON arrays")

    print(format_two_arrays(left, right, args.max_chars))
