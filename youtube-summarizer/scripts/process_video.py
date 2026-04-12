#!/usr/bin/env python3
"""
Master script to process a YouTube video: fetch transcript, prepare for summarization,
and generate HTML summary.

Usage:
    python3 process_video.py "https://youtube.com/watch?v=VIDEO_ID"

This will:
    1. Create videos/<slug>/ directory based on video title
    2. Fetch transcript and metadata (using YouTube's official API)
    3. Save transcript.md
    4. Create a summary template for you to fill in
    5. Generate HTML summary
    6. Update videos/index.html with the new video

Note on Speaker Identification:
    This tool fetches the raw transcript without speaker labels. When creating
    summaries of interviews or discussions, focus on extracting key points from
    the content itself. The agent should use contextual understanding to:
    - Identify interview questions vs. substantive responses
    - Focus on insights from the main subject (interviewee)
    - Skip procedural questions or setup from the interviewer
    - Extract key points, arguments, and takeaways
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import other scripts
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

from fetch_transcript import extract_video_id, fetch_metadata, fetch_transcript


def slugify_title(title: str, max_length: int = 50) -> str:
    """Convert title to a short, filesystem-safe slug."""
    # Remove non-alphanumeric characters (except spaces and hyphens)
    slug = re.sub(r'[^\w\s-]', '', title)
    # Replace spaces with hyphens
    slug = re.sub(r'\s+', '-', slug)
    # Remove multiple consecutive hyphens
    slug = re.sub(r'-+', '-', slug)
    # Convert to lowercase
    slug = slug.lower().strip('-')
    # Truncate to max_length, but try to end at a word boundary
    if len(slug) > max_length:
        slug = slug[:max_length].rsplit('-', 1)[0]
    return slug


def create_summary_template(transcript_data: dict, metadata: dict, video_url: str) -> dict:
    """Create a summary JSON template for manual completion."""
    return {
        "title": metadata.get('title', 'Video Summary') if metadata else 'Video Summary',
        "video_url": video_url,
        "video_id": transcript_data['video_id'],
        "duration": "",
        "summary_date": datetime.now().strftime("%Y-%m-%d"),
        "tags": ["tag1", "tag2", "tag3"],
        "themes": [
            {
                "name": "Theme 1",
                "description": "[Cross-cutting theme description]"
            }
        ],
        "sections": [
            {
                "time": "00:00:00",
                "title": "Introduction",
                "summary": "[Brief summary of this section]",
                "key_points": [
                    {"time": "00:00:00", "text": "[Key point 1]"},
                    {"time": "[TIMESTAMP]", "text": "[Key point 2]"}
                ]
            }
        ],
        "notes": [
            "Read through the transcript and identify key moments",
            "Focus on insights from the main subject (interviewee), not interviewer questions",
            "For interviews: identify questions that elicit substantive responses",
            "Replace [TIMESTAMP] with actual timestamps (HH:MM:SS format)",
            "Add 6-10 sections with 3-5 key points each",
            "Add 3-5 cross-cutting themes",
            "Add up to 5 tags (e.g., ['AI', 'Technology', 'Economy'])",
            "Keep descriptions concise (1-2 sentences)"
        ]
    }


def generate_index_html(videos_dir: Path) -> str:
    """Generate the main index.html listing all processed videos with modal for quick summary."""
    
    # Find all video directories (those with summary.json - summary.html is optional)
    video_dirs = []
    for item in videos_dir.iterdir():
        if item.is_dir():
            summary_json_path = item / 'summary.json'
            if summary_json_path.exists():
                try:
                    with open(summary_json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Get themes for quick summary
                    themes = data.get('themes', [])
                    themes_text = '\n'.join([f"• {t.get('name', '')}: {t.get('description', '')}" for t in themes[:3]])
                    
                    # Check if summary.html exists
                    summary_html_path = item / 'summary.html'
                    has_summary_html = summary_html_path.exists()
                    
                    video_dirs.append({
                        'slug': item.name,
                        'title': data.get('title', item.name),
                        'summary_date': data.get('summary_date', ''),
                        'video_url': data.get('video_url', ''),
                        'tags': data.get('tags', []),
                        'themes_text': themes_text,
                        'path': item.name + '/summary.html',
                        'has_summary_html': has_summary_html
                    })
                except:
                    pass
    
    # Sort by summary_date (newest first), then by slug for videos without dates
    video_dirs.sort(key=lambda x: (x['summary_date'] or '0000-00-00', x['slug']), reverse=True)
    
    # Generate video cards HTML
    video_cards = []
    for i, video in enumerate(video_dirs):
        # Format date
        date_str = video['summary_date']
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                date_display = date_obj.strftime("%b %d, %Y")
            except:
                date_display = date_str
        else:
            date_display = ""
        
        # Generate tags HTML
        tags_html = ''.join([f'<span class="tag">{tag}</span>' for tag in video['tags'][:5]])
        
        # Video link HTML
        video_link_html = f'<a href="{video["video_url"]}" class="video-link-mini" target="_blank" rel="noopener" onclick="event.stopPropagation()">🎥 Watch</a>' if video['video_url'] else ''
        
        # View button HTML - depends on whether summary.html exists
        if video['has_summary_html']:
            view_btn_html = f'<a href="{video["path"]}" class="view-btn" onclick="event.stopPropagation()">View Full →</a>'
            modal_actions_html = f'<a href="{video["path"]}" class="view-full-btn">View Full Summary →</a>'
            card_onclick_attr = f'onclick="openModal({i})"'
            summary_btn_html = f'<button class="summary-btn" onclick="event.stopPropagation(); openModal({i})">📋 Quick Summary</button>'
        else:
            view_btn_html = f'<span class="view-btn" style="opacity:0.5;cursor:not-allowed;" title="Generate HTML summary first">View Full →</span>'
            modal_actions_html = '<p style="color:#888;font-style:italic;">💡 Generate HTML summary to view full details</p>'
            card_onclick_attr = ''
            summary_btn_html = f'<button class="summary-btn" onclick="event.stopPropagation(); openModal({i})">📝 Edit Summary</button>'
        
        card = f'''            <div class="video-card" {card_onclick_attr}>
                <div class="video-header">
                    <div class="video-title">{video['title']}</div>
                    <div class="video-date">{date_display}</div>
                </div>
                <div class="video-actions">
                    {video_link_html}
                    {summary_btn_html}
                    {view_btn_html}
                </div>
                <div class="tags-row">{tags_html}</div>
            </div>
            
            <div id="modal-{i}" class="modal">
                <div class="modal-content">
                    <div class="modal-header">
                        <h2>{video['title']}</h2>
                        <button class="close-btn" onclick="closeModal({i})">&times;</button>
                    </div>
                    <div class="modal-body">
                        <div class="modal-meta">
                            <span>📅 {date_display}</span>
                            {f'<a href="{video["video_url"]}" target="_blank" rel="noopener">🎥 Watch on YouTube →</a>' if video['video_url'] else ''}
                        </div>
                        <div class="modal-tags">{tags_html}</div>
                        <div class="quick-summary">
                            <h3>{"🎯 Key Themes" if video["has_summary_html"] else "📝 Status: Pending Summary"}</h3>
                            <p>{video['themes_text'] if video['themes_text'] else 'Video processed. Edit summary.json to add themes and key points, then generate HTML.'}</p>
                        </div>
                        <div class="modal-actions">
                            {modal_actions_html}
                        </div>
                    </div>
                </div>
            </div>'''
        video_cards.append(card)
    
    videos_html = '\n'.join(video_cards) if video_cards else '''            <div class="empty-state">
                <p>No videos processed yet.</p>
                <p>Run: <code>python3 scripts/process_video.py "YOUTUBE_URL"</code></p>
            </div>'''
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Video Summaries</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}
        
        .header {{
            text-align: center;
            padding: 40px 20px;
            color: white;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            font-weight: 600;
            margin-bottom: 10px;
        }}
        
        .header p {{
            opacity: 0.9;
            font-size: 1.1rem;
        }}
        
        .video-grid {{
            display: grid;
            gap: 20px;
            padding: 20px 0;
        }}
        
        .video-card {{
            background: white;
            border-radius: 12px;
            padding: 20px 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: all 0.3s ease;
            border-left: 4px solid #667eea;
        }}
        
        .video-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            border-left-color: #764ba2;
        }}
        
        .video-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 15px;
            margin-bottom: 12px;
        }}
        
        .video-title {{
            font-size: 1.15rem;
            font-weight: 600;
            color: #333;
            flex: 1;
            line-height: 1.4;
        }}
        
        .video-date {{
            color: #888;
            font-size: 0.85rem;
            white-space: nowrap;
        }}
        
        .video-actions {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 10px;
        }}
        
        .video-link-mini,
        .summary-btn,
        .view-btn {{
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
            text-decoration: none;
            transition: all 0.2s ease;
            border: none;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 5px;
        }}
        
        .video-link-mini {{
            background: #ff0000;
            color: white;
        }}
        
        .video-link-mini:hover {{
            background: #cc0000;
        }}
        
        .summary-btn {{
            background: #667eea;
            color: white;
        }}
        
        .summary-btn:hover {{
            background: #764ba2;
        }}
        
        .view-btn {{
            background: #f0f0f0;
            color: #667eea;
        }}
        
        .view-btn:hover {{
            background: #e0e0e0;
        }}
        
        .tags-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
        }}
        
        .tag {{
            background: #f0f0f0;
            color: #666;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.75rem;
        }}
        
        .empty-state {{
            background: white;
            border-radius: 12px;
            padding: 50px 30px;
            text-align: center;
            color: #666;
        }}
        
        .empty-state code {{
            background: #f4f4f4;
            padding: 2px 8px;
            border-radius: 4px;
            font-family: 'SF Mono', Monaco, monospace;
            font-size: 0.9rem;
        }}
        
        .stats {{
            background: rgba(255,255,255,0.15);
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            display: flex;
            justify-content: center;
            gap: 40px;
        }}
        
        .stat {{
            text-align: center;
            color: white;
        }}
        
        .stat-value {{
            font-size: 2rem;
            font-weight: 700;
        }}
        
        .stat-label {{
            opacity: 0.9;
            font-size: 0.9rem;
        }}
        
        /* Modal Styles */
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            backdrop-filter: blur(4px);
        }}
        
        .modal.active {{
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        
        .modal-content {{
            background: white;
            border-radius: 16px;
            max-width: 600px;
            width: 100%;
            max-height: 80vh;
            overflow-y: auto;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            animation: modalSlideIn 0.3s ease;
        }}
        
        @keyframes modalSlideIn {{
            from {{
                opacity: 0;
                transform: translateY(-30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        
        .modal-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px 25px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 15px;
        }}
        
        .modal-header h2 {{
            font-size: 1.3rem;
            font-weight: 600;
            line-height: 1.4;
        }}
        
        .close-btn {{
            background: rgba(255,255,255,0.2);
            border: none;
            color: white;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            font-size: 1.5rem;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .close-btn:hover {{
            background: rgba(255,255,255,0.3);
        }}
        
        .modal-body {{
            padding: 25px;
        }}
        
        .modal-meta {{
            display: flex;
            gap: 20px;
            margin-bottom: 15px;
            flex-wrap: wrap;
            color: #666;
            font-size: 0.9rem;
        }}
        
        .modal-meta a {{
            color: #667eea;
            text-decoration: none;
        }}
        
        .modal-meta a:hover {{
            text-decoration: underline;
        }}
        
        .modal-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-bottom: 20px;
        }}
        
        .modal-tags .tag {{
            background: #667eea20;
            color: #667eea;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
        }}
        
        .quick-summary {{
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 20px;
        }}
        
        .quick-summary h3 {{
            color: #667eea;
            font-size: 1.1rem;
            margin-bottom: 12px;
        }}
        
        .quick-summary p {{
            color: #555;
            line-height: 1.7;
            white-space: pre-line;
        }}
        
        .modal-actions {{
            text-align: center;
        }}
        
        .view-full-btn {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 25px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .view-full-btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }}
        
        @media (max-width: 600px) {{
            .header h1 {{
                font-size: 1.8rem;
            }}
            
            .video-header {{
                flex-direction: column;
            }}
            
            .video-date {{
                font-size: 0.8rem;
            }}
            
            .video-actions {{
                flex-wrap: wrap;
            }}
            
            .modal-content {{
                margin: 10px;
                max-height: 90vh;
            }}
            
            .stats {{
                flex-direction: column;
                gap: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎬 YouTube Video Summaries</h1>
            <p>Key points and timestamps from video transcripts</p>
            <div class="stats">
                <div class="stat">
                    <div class="stat-value">{len(video_dirs)}</div>
                    <div class="stat-label">Videos</div>
                </div>
            </div>
        </div>
        
        <div class="video-grid">
{videos_html}
        </div>
    </div>
    
    <script>
        function openModal(index) {{
            document.getElementById('modal-' + index).classList.add('active');
            document.body.style.overflow = 'hidden';
        }}
        
        function closeModal(index) {{
            document.getElementById('modal-' + index).classList.remove('active');
            document.body.style.overflow = '';
        }}
        
        // Close modal when clicking outside
        document.addEventListener('click', function(e) {{
            if (e.target.classList.contains('modal')) {{
                e.target.classList.remove('active');
                document.body.style.overflow = '';
            }}
        }});
        
        // Close modal with Escape key
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                document.querySelectorAll('.modal.active').forEach(modal => {{
                    modal.classList.remove('active');
                }});
                document.body.style.overflow = '';
            }}
        }});
    </script>
</body>
</html>'''
    
    return html


def update_index(videos_dir: Path):
    """Update the main index.html file."""
    index_html = generate_index_html(videos_dir)
    index_path = videos_dir / 'index.html'
    
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    return index_path


def process_video(url: str, videos_base_dir: str = None, language: str = None):
    """Process a YouTube video end-to-end."""
    
    # Determine videos directory
    if videos_base_dir is None:
        # Default to creating videos/ in the current working directory
        videos_dir = Path.cwd() / 'videos'
    else:
        videos_dir = Path(videos_base_dir)
    
    videos_dir.mkdir(parents=True, exist_ok=True)
    print(f"Videos directory: {videos_dir.absolute()}")
    
    # Extract video ID
    video_id = extract_video_id(url)
    if not video_id:
        print(f"Error: Could not extract video ID from: {url}", file=sys.stderr)
        print("Expected formats:", file=sys.stderr)
        print("  - https://www.youtube.com/watch?v=VIDEO_ID", file=sys.stderr)
        print("  - https://youtu.be/VIDEO_ID", file=sys.stderr)
        sys.exit(1)
    
    print(f"\nProcessing video: {video_id}")
    
    # Fetch metadata
    print("Fetching video metadata...")
    metadata = fetch_metadata(video_id)
    
    if metadata and metadata.get('title'):
        title = metadata['title']
        print(f"Title: {title}")
        if metadata.get('channel'):
            print(f"Channel: {metadata['channel']}")
        if metadata.get('duration'):
            mins = metadata['duration'] // 60
            print(f"Duration: {mins} minutes")
    else:
        title = f"video_{video_id}"
        print(f"Warning: Could not fetch title, using: {title}")
    
    # Create slug for directory name
    slug = slugify_title(title)
    
    # Ensure unique directory name
    video_dir = videos_dir / slug
    counter = 1
    original_slug = slug
    while video_dir.exists():
        slug = f"{original_slug}-{counter}"
        video_dir = videos_dir / slug
        counter += 1
    
    print(f"\nCreating directory: {video_dir}")
    video_dir.mkdir(parents=True, exist_ok=True)
    
    # Fetch transcript
    print("\nFetching transcript...")
    
    languages = None
    if language:
        languages = [language, f"{language}-{language.upper()}"]
    
    try:
        transcript_data = fetch_transcript(video_id, languages)
        print(f"Found transcript: {transcript_data['language']} (Generated: {transcript_data['is_generated']})")
        print(f"Total segments: {len(transcript_data['data'])}")
    except Exception as e:
        print(f"Error fetching transcript: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Save transcript
    transcript_path = video_dir / 'transcript.md'
    from fetch_transcript import format_transcript
    transcript_content = format_transcript(transcript_data, url, title, metadata)
    
    with open(transcript_path, 'w', encoding='utf-8') as f:
        f.write(transcript_content)
    
    print(f"\nTranscript saved: {transcript_path}")
    
    # Create summary template
    summary_template = create_summary_template(transcript_data, metadata, url)
    summary_json_path = video_dir / 'summary.json'
    
    with open(summary_json_path, 'w', encoding='utf-8') as f:
        json.dump(summary_template, indent=2, fp=f, ensure_ascii=False)
    
    print(f"Summary template: {summary_json_path}")
    
    # Update index
    index_path = update_index(videos_dir)
    print(f"Index updated: {index_path}")
    
    # Print next steps
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print(f"\n1. Edit the summary template:")
    print(f"   {summary_json_path}")
    print(f"\n   Fill in key_points and sections based on the transcript.")
    print(f"   Focus on insights from the main subject, not interviewer questions.")
    print(f"   The transcript is available at:")
    print(f"   {transcript_path}")
    print(f"\n2. Generate HTML summary:")
    print(f"   python3 scripts/generate_html.py --input {summary_json_path} --output {video_dir / 'summary.html'}")
    print(f"\n3. View the index:")
    print(f"   open {index_path}  # macOS")
    print(f"   xdg-open {index_path}  # Linux")
    print(f"\nOr view the summary directly:")
    print(f"   open {video_dir / 'summary.html'}")
    print("=" * 60)
    
    return {
        'video_dir': video_dir,
        'transcript_path': transcript_path,
        'summary_json_path': summary_json_path,
        'index_path': index_path,
        'slug': slug
    }


def main():
    parser = argparse.ArgumentParser(
        description="Process a YouTube video: fetch transcript and prepare for summarization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python3 process_video.py "https://www.youtube.com/watch?v=..."
  
  # With custom videos directory
  python3 process_video.py "URL" --videos-dir ~/my-videos
  
  # With language preference
  python3 process_video.py "URL" --language zh

Note on Speaker Identification:
  This tool fetches raw transcript without speaker labels. When summarizing
  interviews, use contextual understanding to:
  - Focus on substantive responses from the interviewee
  - Skip procedural/setup questions from the interviewer  
  - Extract key insights, arguments, and takeaways
        """
    )
    parser.add_argument(
        "url",
        help="YouTube video URL or video ID"
    )
    parser.add_argument(
        "--videos-dir", "-d",
        help="Base directory for videos (default: ./videos)"
    )
    parser.add_argument(
        "--language", "-l",
        help="Preferred transcript language code (e.g., en, zh, es)"
    )
    
    args = parser.parse_args()
    
    process_video(args.url, args.videos_dir, args.language)


if __name__ == "__main__":
    main()
