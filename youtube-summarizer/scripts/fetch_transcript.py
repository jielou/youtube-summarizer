#!/usr/bin/env python3
"""
Fetch YouTube video transcript and metadata, save to file.

Requires: 
    pip install youtube-transcript-api
    pip install yt-dlp
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    from youtube_transcript_api import YouTubeTranscriptApi
    from youtube_transcript_api.formatters import TextFormatter
except ImportError:
    print("Error: youtube-transcript-api not installed.", file=sys.stderr)
    print("Install with: pip install youtube-transcript-api", file=sys.stderr)
    sys.exit(1)

# yt-dlp is optional but recommended for metadata
try:
    from yt_dlp import YoutubeDL
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False


def extract_video_id(url: str) -> str:
    """Extract YouTube video ID from various URL formats."""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/v/|youtube\.com/shorts/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',  # Direct video ID
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def fetch_metadata(video_id: str) -> dict:
    """Fetch video metadata using yt-dlp."""
    if not YTDLP_AVAILABLE:
        return None
    
    try:
        url = f"https://www.youtube.com/watch?v={video_id}"
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return {
                'title': info.get('title'),
                'channel': info.get('channel'),
                'channel_id': info.get('channel_id'),
                'duration': info.get('duration'),
                'upload_date': info.get('upload_date'),
                'view_count': info.get('view_count'),
                'description': info.get('description'),
            }
    except Exception as e:
        print(f"Warning: Could not fetch metadata: {e}", file=sys.stderr)
        return None


def fetch_transcript(video_id: str, languages: list = None) -> dict:
    """Fetch transcript for a YouTube video."""
    if languages is None:
        languages = ['en', 'en-US', 'en-GB', 'zh', 'zh-CN', 'zh-TW', 'es', 'fr', 'de', 'ja', 'ko']
    
    try:
        ytt_api = YouTubeTranscriptApi()
        
        # List available transcripts
        transcript_list = ytt_api.list(video_id)
        
        # Try to find transcript in preferred languages
        transcript = None
        for lang in languages:
            try:
                transcript = transcript_list.find_transcript([lang])
                break
            except:
                continue
        
        # If no preferred language found, try any available generated transcript
        if transcript is None:
            try:
                transcript = transcript_list.find_generated_transcript(['en'])
            except:
                # Get first available transcript
                available = list(transcript_list)
                if available:
                    transcript = available[0]
        
        if transcript is None:
            raise Exception("No transcript found for this video")
        
        # Fetch the actual transcript data
        data = transcript.fetch()
        
        # Convert to serializable format
        data_list = [
            {
                'text': snippet.text,
                'start': snippet.start,
                'duration': snippet.duration
            }
            for snippet in data
        ]
        
        return {
            'video_id': video_id,
            'language': transcript.language,
            'language_code': transcript.language_code,
            'is_generated': transcript.is_generated,
            'data': data_list
        }
        
    except Exception as e:
        raise Exception(f"Failed to fetch transcript: {e}")


def format_transcript(transcript_data: dict, video_url: str = None, title: str = None, 
                      metadata: dict = None) -> str:
    """Format transcript data into markdown."""
    lines = []
    
    # Header
    if video_url:
        lines.append(f"Link: {video_url}")
    else:
        lines.append(f"Video ID: {transcript_data['video_id']}")
    
    # Use provided title or metadata title
    display_title = title or (metadata.get('title') if metadata else None)
    if display_title:
        lines.append(f"Title: {display_title}")
    
    if metadata:
        if metadata.get('channel'):
            lines.append(f"Channel: {metadata['channel']}")
        if metadata.get('upload_date'):
            # Format YYYYMMDD to YYYY-MM-DD
            date = metadata['upload_date']
            formatted_date = f"{date[:4]}-{date[4:6]}-{date[6:8]}"
            lines.append(f"Published: {formatted_date}")
        if metadata.get('duration'):
            duration = metadata['duration']
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            seconds = duration % 60
            if hours > 0:
                duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                duration_str = f"{minutes}:{seconds:02d}"
            lines.append(f"Duration: {duration_str}")
    
    lines.append(f"Language: {transcript_data['language']} ({transcript_data['language_code']})")
    lines.append(f"Generated: {'Yes' if transcript_data['is_generated'] else 'No'}")
    lines.append("")
    
    # Add description if available
    if metadata and metadata.get('description'):
        lines.append("## Description")
        lines.append("")
        lines.append(metadata['description'][:500] + "..." if len(metadata['description']) > 500 else metadata['description'])
        lines.append("")
        lines.append("---")
        lines.append("")
    
    # Transcript content with timestamps
    lines.append("## Transcript")
    lines.append("")
    
    for entry in transcript_data['data']:
        start = entry['start']
        text = entry['text']
        
        # Format timestamp as HH:MM:SS or MM:SS
        hours = int(start // 3600)
        minutes = int((start % 3600) // 60)
        seconds = int(start % 60)
        
        if hours > 0:
            timestamp = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            timestamp = f"{minutes:02d}:{seconds:02d}"
        
        lines.append(timestamp)
        lines.append(text)
        lines.append("")
    
    return "\n".join(lines)


def format_transcript_text_only(transcript_data: dict) -> str:
    """Format transcript as plain text without timestamps."""
    lines = [entry['text'] for entry in transcript_data['data']]
    return " ".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Fetch YouTube video transcript and metadata"
    )
    parser.add_argument(
        "url",
        help="YouTube video URL or video ID"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output file path (default: transcript.md)"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["markdown", "text", "json"],
        default="markdown",
        help="Output format"
    )
    parser.add_argument(
        "--title", "-t",
        help="Video title to include in output (auto-fetched if not provided and yt-dlp is installed)"
    )
    parser.add_argument(
        "--language", "-l",
        help="Preferred language code (e.g., en, zh, es)"
    )
    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Skip fetching video metadata"
    )
    
    args = parser.parse_args()
    
    # Extract video ID
    video_id = extract_video_id(args.url)
    if not video_id:
        print(f"Error: Could not extract video ID from: {args.url}", file=sys.stderr)
        print("Expected formats:", file=sys.stderr)
        print("  - https://www.youtube.com/watch?v=VIDEO_ID", file=sys.stderr)
        print("  - https://youtu.be/VIDEO_ID", file=sys.stderr)
        print("  - VIDEO_ID (11 characters)", file=sys.stderr)
        sys.exit(1)
    
    print(f"Fetching transcript for video: {video_id}")
    
    # Fetch metadata if available
    metadata = None
    if not args.no_metadata and YTDLP_AVAILABLE:
        print("Fetching video metadata...")
        metadata = fetch_metadata(video_id)
        if metadata and metadata.get('title'):
            print(f"Title: {metadata['title']}")
    elif not YTDLP_AVAILABLE and not args.title:
        print("Note: Install yt-dlp (pip install yt-dlp) to auto-fetch video title and metadata")
    
    # Set language preference
    languages = None
    if args.language:
        languages = [args.language, f"{args.language}-{args.language.upper()}"]
    
    # Fetch transcript
    try:
        transcript_data = fetch_transcript(video_id, languages)
        print(f"Found transcript: {transcript_data['language']} (Generated: {transcript_data['is_generated']})")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Determine output format and content
    if args.format == "json":
        output_data = {
            'metadata': metadata,
            'transcript': transcript_data
        }
        content = json.dumps(output_data, indent=2, ensure_ascii=False)
        default_ext = ".json"
    elif args.format == "text":
        content = format_transcript_text_only(transcript_data)
        default_ext = ".txt"
    else:  # markdown
        content = format_transcript(transcript_data, args.url, args.title, metadata)
        default_ext = ".md"
    
    # Write output
    output_path = args.output or f"transcript{default_ext}"
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"Transcript saved to: {output_file.absolute()}")
    
    # Also return the path for scripting
    return str(output_file.absolute())


if __name__ == "__main__":
    main()
