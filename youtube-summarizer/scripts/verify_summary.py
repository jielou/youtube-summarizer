#!/usr/bin/env python3
"""
Verify summary.json timestamps for coverage and gaps.

For videos > 1 hour, it's easy to front-load sections and miss large chunks.
This script checks:
1. Sections span the entire video (first near 00:00, last near end)
2. No large gaps between consecutive sections (> 15 min flagged)
3. Timestamps are in ascending order
4. Key point timestamps roughly fall within their section's range (±3 min buffer)
"""

import argparse
import json
import sys
from pathlib import Path


def parse_time(t: str) -> int:
    """Convert HH:MM:SS or MM:SS to total seconds."""
    parts = t.strip().split(":")
    if len(parts) == 3:
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
    elif len(parts) == 2:
        return int(parts[0]) * 60 + int(parts[1])
    return 0


def fmt_time(seconds: int) -> str:
    """Convert seconds back to MM:SS or HH:MM:SS."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def verify_summary(summary_path: Path, duration: str = None):
    with open(summary_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    sections = data.get("sections", [])
    video_duration = duration or data.get("duration", "")
    errors = []
    warnings = []

    if not sections:
        errors.append("No sections found.")
        print("\n".join(errors))
        sys.exit(1)

    # Parse video duration
    video_seconds = parse_time(video_duration) if video_duration else 0

    # Check 1: First section starts near 00:00
    first_time = parse_time(sections[0].get("time", "0:0"))
    if first_time > 120:
        warnings.append(f"First section starts at {fmt_time(first_time)} — should be closer to 00:00.")

    # Check 2: Last section is near video end
    if video_seconds > 0:
        last_time = parse_time(sections[-1].get("time", "0:0"))
        gap_to_end = video_seconds - last_time
        if gap_to_end > 1200:  # > 20 min
            warnings.append(f"Last section at {fmt_time(last_time)}, but video ends at {video_duration}. "
                          f"Gap of {fmt_time(gap_to_end)} with no sections.")
        elif gap_to_end > 600:  # > 10 min
            warnings.append(f"Last section at {fmt_time(last_time)}, video ends at {video_duration}. "
                          f"Trailing gap of {fmt_time(gap_to_end)}.")

    # Check 3: Gaps between consecutive sections
    for i in range(1, len(sections)):
        prev_time = parse_time(sections[i - 1].get("time", "0:0"))
        curr_time = parse_time(sections[i].get("time", "0:0"))
        gap = curr_time - prev_time

        if gap < 0:
            errors.append(f"Section {i+1} timestamp ({sections[i]['time']}) is BEFORE section {i} ({sections[i-1]['time']}).")
        elif gap > 1200:  # > 20 minutes
            errors.append(f"CRITICAL: {fmt_time(gap)} gap between section {i} ({sections[i-1]['time']}) and section {i+1} ({sections[i]['time']}). Large chunk of video is uncovered.")
        elif gap > 900:  # > 15 minutes
            warnings.append(f"Large gap between section {i} ({sections[i-1]['time']}) and section {i+1} ({sections[i]['time']}): {fmt_time(gap)} of missing coverage.")

    # Check 4: Key point timestamps roughly fall within section range (±3 min buffer)
    BUFFER = 180  # 3 minutes in seconds
    for i, section in enumerate(sections):
        section_start = parse_time(section.get("time", "0:0"))
        section_end = parse_time(sections[i + 1]["time"]) if i + 1 < len(sections) else video_seconds
        for kp in section.get("key_points", []):
            kp_time = parse_time(kp.get("time", "0:0"))
            if kp_time < section_start - BUFFER:
                warnings.append(f"Key point [{kp.get('time')}] in section '{section['title']}' is more than 3 min BEFORE the section starts ({section['time']}).")
            elif kp_time > section_end + BUFFER:
                warnings.append(f"Key point [{kp.get('time')}] in section '{section['title']}' is more than 3 min AFTER the section ends ({fmt_time(section_end)}).")

    # Report
    print(f"\n📋 Summary Verification: {summary_path.name}")
    print(f"   Sections: {len(sections)}  |  Video: {video_duration or 'unknown'}")

    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"   • {e}")

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"   • {w}")

    if not errors and not warnings:
        print("\n✅ All checks passed. Timestamps look good.")

    if errors:
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Verify summary.json timestamps")
    parser.add_argument("--input", "-i", required=True, help="Path to summary.json")
    parser.add_argument("--duration", "-d", help="Video duration (HH:MM:SS or MM:SS)")
    args = parser.parse_args()
    verify_summary(Path(args.input), args.duration)


if __name__ == "__main__":
    main()
