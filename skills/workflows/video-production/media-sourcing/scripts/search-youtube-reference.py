#!/usr/bin/env python3
"""
YouTube Reference Search - search YouTube and filter/rank videos for reference suitability.

Uses ONLY Python standard library + yt-dlp (already installed).

Usage:
    python3 search-youtube-reference.py --query "chicago navy pier winter ice" --campaign ./my-campaign
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Suitability heuristics keywords
POSITIVE_KEYWORDS = [
    "broll", "b-roll", "stock", "footage", "raw", "4k", "1080p", "cinematic",
    "overlay free", "no copyright", "copyright free", "royalty free", "establishing shot",
    "uncut", "unedited", "no music", "ambient", "natural sound", "nat sound", "clean"
]

NEGATIVE_KEYWORDS = [
    "vlog", "review", "reaction", "meme", "compilation", "shorts", "tiktok",
    "how to", "tutorial", "podcast", "gaming", "interview", "news", "funny",
    "edit", "talking head", "show", "episode", "commercial", "advertisement",
    "text overlay", "subtitles", "lyrics", "with text", "watermark"
]


def error(msg):
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def format_duration(seconds):
    """Format duration in seconds to MM:SS or HH:MM:SS."""
    if not seconds:
        return "00:00"
    try:
        seconds = int(seconds)
    except ValueError:
        return "00:00"
    
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


def score_video(video):
    """
    Score a video based on stock footage suitability.
    Higher score means more likely to be clean, unedited stock/b-roll footage.
    """
    title = video.get("title", "").lower()
    description = video.get("description", "").lower()
    channel = video.get("channel", "").lower()
    duration = video.get("duration")

    score = 0
    matched_pos = set()
    matched_neg = set()

    # Title check (highest weight)
    for word in POSITIVE_KEYWORDS:
        pattern = r"\b" + re.escape(word) + r"\b"
        # Handle "b-roll" / "broll" boundary differences
        if word in ["broll", "b-roll"]:
            pattern = r"\bb-?roll\b"
        if re.search(pattern, title):
            score += 20
            matched_pos.add(word)
            
    for word in NEGATIVE_KEYWORDS:
        if re.search(r"\b" + re.escape(word) + r"\b", title):
            score -= 30
            matched_neg.add(word)

    # Description check (medium weight)
    for word in POSITIVE_KEYWORDS:
        pattern = r"\b" + re.escape(word) + r"\b"
        if word in ["broll", "b-roll"]:
            pattern = r"\bb-?roll\b"
        if re.search(pattern, description):
            score += 5
            matched_pos.add(word)

    for word in NEGATIVE_KEYWORDS:
        if re.search(r"\b" + re.escape(word) + r"\b", description):
            score -= 10
            matched_neg.add(word)

    # Channel check
    for word in NEGATIVE_KEYWORDS:
        if re.search(r"\b" + re.escape(word) + r"\b", channel):
            score -= 25
            matched_neg.add(f"channel:{word}")
    
    # Specific positive channel naming clues (e.g. "Stock Footage", "Free B-Roll")
    for word in ["stock", "footage", "broll", "b-roll", "free b-roll", "cinematic"]:
        pattern = r"\b" + re.escape(word) + r"\b"
        if word in ["broll", "b-roll"]:
            pattern = r"\bb-?roll\b"
        if re.search(pattern, channel):
            score += 15
            matched_pos.add(f"channel:{word}")

    # Creative Commons bonus points
    license_text = video.get("license", "")
    if license_text and "creative commons" in license_text.lower():
        score += 15
        matched_pos.add("cc-license")
    elif "creative commons" in description.lower() or "cc-by" in description.lower():
        score += 10
        matched_pos.add("cc-mention")

    # Duration scoring
    if duration:
        try:
            d_sec = int(duration)
            if d_sec <= 15:
                score += 5   # very short, good single clip
            elif 15 < d_sec <= 120:
                score += 15  # ideal length for a b-roll clip
            elif 120 < d_sec <= 300:
                score += 5   # reasonable b-roll package/clip
            elif 300 < d_sec <= 600:
                score -= 10  # starting to look like a vlog or compilation
            else:
                score -= 30  # > 10 minutes is highly unlikely to be clean stock
        except (ValueError, TypeError):
            pass

    return score, sorted(list(matched_pos)), sorted(list(matched_neg))


def main():
    parser = argparse.ArgumentParser(
        description="YouTube reference search - search and filter/rank for b-roll/reference suitability."
    )
    parser.add_argument("--query", required=True, help="YouTube search query")
    parser.add_argument("--limit", type=int, default=10, help="Max number of videos to retrieve and rank (default: 10)")
    parser.add_argument("--cc-only", action="store_true", help="Hard filter search query on YouTube for Creative Commons license only")
    parser.add_argument("--campaign", default="[campaign-folder]", help="Campaign directory to generate rip commands for")
    
    args = parser.parse_args()

    # Append filter keyword to query if CC only requested
    search_query = args.query
    if args.cc_only:
        search_query += ", creativecommons"

    print(f"Searching YouTube for: '{search_query}' (limit: {args.limit})...")
    
    cmd = [
        "yt-dlp",
        "--ignore-errors",
        "--no-download",
        "--no-playlist",
        "--dump-json",
        f"ytsearch{args.limit}:{search_query}"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        error("yt-dlp command not found. Please run 'brew install yt-dlp' first.")

    videos = []
    if result.stdout:
        for line in result.stdout.strip().splitlines():
            if not line:
                continue
            try:
                video_data = json.loads(line)
                videos.append(video_data)
            except json.JSONDecodeError:
                continue

    if not videos:
        print("No search results found.")
        sys.exit(0)

    # Score and rank videos
    ranked_videos = []
    for v in videos:
        score, pos, neg = score_video(v)
        ranked_videos.append({
            "score": score,
            "pos": pos,
            "neg": neg,
            "data": v
        })

    # Sort by score descending
    ranked_videos.sort(key=lambda x: x["score"], reverse=True)

    print("\n" + "=" * 100)
    print(f"{'RANK':<5} {'SCORE':<7} {'DURATION':<10} {'TITLE':<45} {'CHANNEL':<30}")
    print("=" * 100)

    for idx, item in enumerate(ranked_videos, 1):
        v = item["data"]
        score = item["score"]
        pos = item["pos"]
        neg = item["neg"]

        title = v.get("title", "Unknown Title")
        if len(title) > 42:
            title = title[:39] + "..."
            
        channel = v.get("channel", "Unknown Channel")
        if len(channel) > 28:
            channel = channel[:25] + "..."

        duration_str = format_duration(v.get("duration"))
        
        # Color score green if >= 15, red if < 0 (using ANSI escape codes)
        color_start = ""
        color_end = ""
        if score >= 15:
            color_start = "\033[92m" # Green
            color_end = "\033[0m"
        elif score < 0:
            color_start = "\033[91m" # Red
            color_end = "\033[0m"

        print(f"{idx:<5} {color_start}{score:<7}{color_end} {duration_str:<10} {title:<45} {channel:<30}")
        
        # Print matched details
        match_details = []
        if pos:
            match_details.append(f"Pos: {', '.join(pos)}")
        if neg:
            match_details.append(f"Neg: {', '.join(neg)}")
        
        if match_details:
            print(f"      [{' | '.join(match_details)}]")

        # Print URL and rip instruction
        url = v.get("webpage_url", "No URL")
        print(f"      URL: {url}")
        
        # Find script location for recommended command and keep it readable
        # when the script is run from a repo root.
        rip_script_path = Path(__file__).resolve().parent / "download-youtube-reference.py"
        try:
            rip_script = str(rip_script_path.relative_to(Path.cwd()))
        except ValueError:
            rip_script = str(rip_script_path)
                
        print(f"      Rip cmd: python3 {rip_script} \"{url}\" {args.campaign} --start 0:00 --end 0:10")
        print("-" * 100)


if __name__ == "__main__":
    main()
