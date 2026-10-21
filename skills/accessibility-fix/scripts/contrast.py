#!/usr/bin/env python3
"""Compute WCAG 2.2 contrast ratios, with alpha compositing and optional fix suggestions. No network calls."""

import argparse
import json
import math
import re
import sys

THRESHOLDS = [
    ("1.4.3", "AA", "normal text", 4.5),
    ("1.4.3", "AA", "large text", 3.0),
    ("1.4.6", "AAA", "normal text", 7.0),
    ("1.4.6", "AAA", "large text", 4.5),
    ("1.4.11", "AA", "non-text UI and graphics", 3.0),
]
NUMBER = r"[-+]?(?:\d+\.?\d*|\.\d+)"


def parse_color(text):
    """Return (r, g, b, a) with channels 0-255 and alpha 0-1."""
    value = text.strip().lower()
    if value == "white":
        return (255.0, 255.0, 255.0, 1.0)
    if value == "black":
        return (0.0, 0.0, 0.0, 1.0)
    match = re.fullmatch(r"#?([0-9a-f]{3,4}|[0-9a-f]{6}|[0-9a-f]{8})", value)
    if match:
        digits = match.group(1)
        if len(digits) in (3, 4):
            digits = "".join(ch * 2 for ch in digits)
        channels = [int(digits[i:i + 2], 16) for i in range(0, len(digits), 2)]
        alpha = channels[3] / 255 if len(channels) == 4 else 1.0
        return (float(channels[0]), float(channels[1]), float(channels[2]), alpha)
    match = re.fullmatch(r"rgba?\((.*)\)", value)
    if match:
        parts = [p for p in re.split(r"[\s,/]+", match.group(1).strip()) if p]
        if len(parts) in (3, 4):
            rgb = []
            for part in parts[:3]:
                if not re.fullmatch(NUMBER + "%?", part):
                    break
                number = float(part.rstrip("%"))
                rgb.append(number * 2.55 if part.endswith("%") else number)
            else:
                alpha = 1.0
                if len(parts) == 4:
                    if not re.fullmatch(NUMBER + "%?", parts[3]):
                        raise ValueError(f"Unrecognized color: {text}")
                    alpha = float(parts[3].rstrip("%")) / (100 if parts[3].endswith("%") else 1)
                if all(0 <= c <= 255 for c in rgb) and 0 <= alpha <= 1:
                    return (*rgb, alpha)
    raise ValueError(f"Unrecognized color: {text}. Use hex (#rgb, #rrggbb, #rrggbbaa) or rgb()/rgba().")


def composite(top, bottom):
    """Alpha-composite top over an opaque bottom color."""
    alpha = top[3]
    return tuple(top[i] * alpha + bottom[i] * (1 - alpha) for i in range(3)) + (1.0,)


def luminance(color):
    def channel(value):
        c = value / 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (channel(v) for v in color[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(foreground, background):
    lighter, darker = sorted((luminance(foreground), luminance(background)), reverse=True)
    return (lighter + 0.05) / (darker + 0.05)


def truncate(value):
    """Two decimals, never rounded up, so 4.4955 reports as 4.49 rather than a passing 4.5."""
    return math.floor(value * 100) / 100


def to_hex(color):
    return "#" + "".join(f"{round(c):02x}" for c in color[:3])


def suggest(foreground, background, target):
    """Smallest mix of the foreground toward black or white that reaches the target ratio."""
    options = []
    for anchor in ((0.0, 0.0, 0.0, 1.0), (255.0, 255.0, 255.0, 1.0)):
        if ratio(anchor, background) < target:
            continue
        low, high = 0.0, 1.0
        for _ in range(40):
            mid = (low + high) / 2
            mixed = tuple(foreground[i] + (anchor[i] - foreground[i]) * mid for i in range(3)) + (1.0,)
            if ratio(mixed, background) >= target:
                high = mid
            else:
                low = mid
        candidate = tuple(foreground[i] + (anchor[i] - foreground[i]) * high for i in range(3)) + (1.0,)
        # Rounding to hex can land just under the target; step further until it passes.
        rounded = parse_color(to_hex(candidate))
        while ratio(rounded, background) < target and high < 1:
            high = min(1.0, high + 0.002)
            candidate = tuple(foreground[i] + (anchor[i] - foreground[i]) * high for i in range(3)) + (1.0,)
            rounded = parse_color(to_hex(candidate))
        options.append((high, to_hex(rounded), ratio(rounded, background)))
    if not options:
        return None
    change, color, achieved = min(options)
    return {"color": color, "ratio": truncate(achieved), "change": round(change, 3)}


def evaluate(foreground_text, background_text, base_text="white", target=None):
    base = parse_color(base_text)
    if base[3] < 1:
        raise ValueError("The base color must be opaque.")
    background = parse_color(background_text)
    notes = []
    if background[3] < 1:
        notes.append(f"Background is translucent; composited over {base_text}. Confirm the real underlying color.")
        background = composite(background, base)
    foreground = parse_color(foreground_text)
    if foreground[3] < 1:
        notes.append("Foreground is translucent; composited over the background.")
        foreground = composite(foreground, background)
    value = ratio(foreground, background)
    result = {
        "foreground": to_hex(foreground),
        "background": to_hex(background),
        "ratio": truncate(value),
        "ratio_exact": value,
        "checks": [
            {"criterion": c, "level": lvl, "applies_to": what, "required": req, "pass": value >= req}
            for c, lvl, what, req in THRESHOLDS
        ],
        "notes": notes,
    }
    if target is not None and value < target:
        result["suggestion"] = suggest(foreground, background, target)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("foreground", help="Text or graphic color, e.g. #767676 or rgba(0,0,0,.6)")
    parser.add_argument("background", help="Adjacent background color")
    parser.add_argument("--base", default="white", help="Opaque color under a translucent background (default white)")
    parser.add_argument("--target", type=float, help="Suggest the nearest foreground reaching this ratio, e.g. 4.5")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()
    if args.target is not None and not (math.isfinite(args.target) and 1 < args.target <= 21):
        parser.error("--target must be a ratio greater than 1 and at most 21")
    try:
        result = evaluate(args.foreground, args.background, args.base, args.target)
    except ValueError as error:
        print(f"Contrast error: {error}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
        return 0
    print(f"{result['foreground']} on {result['background']}: {result['ratio']:.2f}:1")
    for check in result["checks"]:
        mark = "pass" if check["pass"] else "FAIL"
        print(f"  {mark}  {check['criterion']} {check['level']:<3} {check['applies_to']} (needs {check['required']}:1)")
    for note in result["notes"]:
        print(f"  note: {note}")
    if args.target is not None:
        tip = result.get("suggestion")
        if args.target and result["ratio_exact"] >= args.target:
            print(f"  Already meets {args.target}:1.")
        elif tip:
            print(f"  Nearest foreground meeting {args.target}:1: {tip['color']} ({tip['ratio']}:1)")
        else:
            print(f"  No foreground color reaches {args.target}:1 on this background; change the background.")
    print("  Large text is at least 18pt (24 CSS px) regular or 14pt (about 18.66 CSS px) bold.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
