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
import shutil
import sys
from pathlib import Path
from datetime import datetime, timedelta

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
    
    import html as html_module
    
    def fmt_duration(dur):
        if not dur:
            return ''
        parts = dur.split(':')
        if len(parts) == 3:
            h, m, s = int(parts[0]), int(parts[1]), int(parts[2])
            if h > 0:
                return f"{h} hr {m} min"
            return f"{m} min"
        return dur
    
    # Find all video directories
    video_dirs = []
    all_tags = set()
    for item in videos_dir.iterdir():
        if item.is_dir():
            summary_json_path = item / 'summary.json'
            if summary_json_path.exists():
                try:
                    with open(summary_json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    themes = data.get('themes', [])
                    themes_text = '\n'.join([f"• {t.get('name', '')}: {t.get('description', '')}" for t in themes[:3]])
                    
                    preview = ""
                    if themes and themes[0].get('description'):
                        preview = themes[0]['description']
                    elif data.get('sections') and data['sections'][0].get('summary'):
                        preview = data['sections'][0]['summary']
                    if len(preview) > 150:
                        preview = preview[:147] + '...'
                    preview = html_module.escape(preview)
                    
                    sections = data.get('sections', [])
                    total_kp = sum(len(s.get('key_points', [])) for s in sections)
                    total_secs = len(sections)
                    dur = data.get('duration', '')
                    
                    meta_parts = []
                    if total_kp:
                        meta_parts.append(f"📋&nbsp;{total_kp}&nbsp;key&nbsp;points")
                    if total_secs:
                        meta_parts.append(f"⏱&nbsp;{total_secs}&nbsp;timestamps")
                    fd = fmt_duration(dur)
                    if fd:
                        meta_parts.append(f"📖&nbsp;{fd}")
                    meta_line = "&nbsp;·&nbsp;".join(meta_parts) if meta_parts else ""
                    
                    summary_html_path = item / 'summary.html'
                    has_summary_html = summary_html_path.exists()
                    
                    tags = data.get('tags', [])
                    all_tags.update(tags)
                    
                    video_dirs.append({
                        'slug': item.name,
                        'title': data.get('title', item.name),
                        'summary_date': data.get('summary_date', ''),
                        'video_url': data.get('video_url', ''),
                        'video_id': data.get('video_id', ''),
                        'duration': dur,
                        'tags': tags,
                        'themes_text': themes_text,
                        'preview': preview,
                        'meta_line': meta_line,
                        'path': item.name + '/summary.html',
                        'has_summary_html': has_summary_html,
                    })
                except:
                    pass
    
    video_dirs.sort(key=lambda x: (x['summary_date'] or '0000-00-00', x['slug']), reverse=True)
    sorted_tags = sorted(all_tags)
    
    # Priority filter tags
    PRIORITY = ['AI', 'OpenAI', 'Anthropic', 'NVIDIA', 'DeepMind', 'Science', 'Business', 'Geopolitics', 'Investing', 'Semiconductors']
    priority_tags = [t for t in PRIORITY if t in sorted_tags]
    more_tags = [t for t in sorted_tags if t not in priority_tags]
    
    def make_chip(tag, is_more=False):
        cls = 'filter-chip more-chip' if is_more else 'filter-chip'
        return f'<button class="{cls}" data-tag="{html_module.escape(tag)}" onclick="filterByTag(\'{html_module.escape(tag)}\')">{html_module.escape(tag)}</button>'
    
    priority_html = ''.join([make_chip(t) for t in priority_tags])
    more_html = ''.join([make_chip(t, True) for t in more_tags])
    has_more = bool(more_html)
    
    # Generate cards
    video_cards = []
    for i, video in enumerate(video_dirs):
        date_str = video['summary_date']
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                date_display = date_obj.strftime("%b %d, %Y").upper()
            except:
                date_display = date_str.upper()
        else:
            date_display = ""
        
        vid = video.get('video_id', '')
        thumb = f'<img src="https://img.youtube.com/vi/{vid}/mqdefault.jpg" alt="" class="card-thumb-img" loading="lazy">' if vid else '<div class="card-thumb-placeholder">🎬</div>'
        dur_badge = f'<span class="card-duration">{html_module.escape(video["duration"])}</span>' if video.get('duration') else ''
        
        tags_html = ''.join([f'<span class="card-tag">{html_module.escape(tag)}</span>' for tag in video['tags'][:5]])
        
        video_link = video['video_url'] or ''
        
        if video['has_summary_html']:
            read_btn = f'<a href="{video["path"]}" class="action-btn action-primary" onclick="event.stopPropagation()">Read&nbsp;summary</a>'
            modal_cta = f'<a href="{video["path"]}" class="modal-cta">Read Full Summary →</a>'
            card_click = f'onclick="openModal({i})"'
        else:
            read_btn = '<span class="action-btn action-primary" style="opacity:0.5;cursor:not-allowed;" title="Generate HTML summary first">Read&nbsp;summary</span>'
            modal_cta = '<p style="color:#888;font-style:italic;">💡 Generate HTML summary to view full details</p>'
            card_click = ''
        
        watch_btn = f'<a href="{video_link}" class="action-btn action-secondary" target="_blank" rel="noopener" onclick="event.stopPropagation()">▶&nbsp;Watch</a>' if video_link else ''
        share_btn = f'<button class="action-btn action-secondary" onclick="event.stopPropagation(); copyUrl(\'{video_link}\')">↗&nbsp;Share</button>' if video_link else ''

        preview_html = f'<p class="card-preview">{video["preview"]}</p>' if video['preview'] else ''
        meta_html = f'<div class="card-meta">{video["meta_line"]}</div>' if video['meta_line'] else ''
        
        card = f'''            <div class="video-card" data-index="{i}" data-title="{html_module.escape(video['title']).lower()}" data-tags="{','.join(video['tags'])}" data-date="{video['summary_date']}" {card_click}>
                <div class="card-thumb">
                    {thumb}
                    {dur_badge}
                </div>
                <div class="card-body">
                    <div class="card-date">{date_display}</div>
                    <h3 class="card-title">{html_module.escape(video['title'])}</h3>
                    {preview_html}
                    {meta_html}
                    <div class="card-tags">{tags_html}</div>
                    <div class="card-actions">
                        {read_btn}
                        {watch_btn}
                        {share_btn}
                    </div>
                </div>
            </div>
            
            <div id="modal-{i}" class="modal">
                <div class="modal-backdrop" onclick="closeModal({i})"></div>
                <div class="modal-content">
                    <div class="modal-thumb">
                        {thumb}
                        {dur_badge}
                    </div>
                    <div class="modal-body">
                        <div class="modal-header-row">
                            <h2>{html_module.escape(video['title'])}</h2>
                            <button class="modal-close" onclick="closeModal({i})">&times;</button>
                        </div>
                        <div class="modal-meta">
                            <span>{date_display}</span>
                            {f'<a href="{video_link}" target="_blank" rel="noopener">🎥 Watch on YouTube</a>' if video_link else ''}
                        </div>
                        <div class="modal-tags">{tags_html}</div>
                        <div class="quick-summary">
                            <h3>{"🎯 Key Themes" if video["has_summary_html"] else "📝 Status: Pending Summary"}</h3>
                            <p>{video['themes_text'] if video['themes_text'] else 'Video processed. Edit summary.json to add themes and key points, then generate HTML.'}</p>
                        </div>
                        <div class="modal-footer">
                            {modal_cta}
                        </div>
                    </div>
                </div>
            </div>'''
        video_cards.append(card)
    
    videos_html = '\n'.join(video_cards) if video_cards else '''            <div class="empty-state">
                <div class="empty-icon">🎬</div>
                <p>No videos summarized yet.</p>
                <p>Run: <code>python3 scripts/process_video.py "YOUTUBE_URL"</code></p>
            </div>'''
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Personal Video Summary Library</title>
    <style>
        :root {{
            --page-bg: #F7F8FC;
            --card-bg: #FFFFFF;
            --text-primary: #111827;
            --text-secondary: #4B5563;
            --text-muted: #6B7280;
            --primary: #4F46E5;
            --primary-hover: #4338CA;
            --primary-light: #EEF2FF;
            --border: #E5E7EB;
            --shadow-soft: 0 8px 24px rgba(15, 23, 42, 0.06);
            --shadow-hover: 0 14px 34px rgba(15, 23, 42, 0.10);
        }}
        
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: var(--text-primary);
            background: var(--page-bg);
            min-height: 100vh;
            padding-bottom: 60px;
        }}
        
        /* Header */
        .header {{
            background:
                radial-gradient(circle at 15% 20%, rgba(99, 102, 241, 0.14), transparent 32%),
                radial-gradient(circle at 85% 80%, rgba(139, 92, 246, 0.10), transparent 35%),
                linear-gradient(135deg, #F5F7FF 0%, #EEF2FF 45%, #F8FAFC 100%);
            border-bottom: 1px solid var(--border);
            padding: 48px 32px 40px;
        }}
        
        .header-inner {{
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 24px;
            flex-wrap: wrap;
        }}
        
        .header-brand {{
            display: flex;
            align-items: center;
            gap: 18px;
        }}
        
        .header-logo {{
            width: 52px;
            height: 52px;
            border-radius: 14px;
            flex-shrink: 0;
            object-fit: cover;
            box-shadow: 0 6px 20px rgba(79, 70, 229, 0.25);
        }}
        
        .header-text h1 {{
            font-size: 1.8rem;
            font-weight: 800;
            color: var(--text-primary);
            letter-spacing: -0.6px;
            line-height: 1.15;
        }}
        
        .header-text p {{
            font-size: 1rem;
            color: var(--text-secondary);
            margin-top: 6px;
            max-width: 480px;
            line-height: 1.5;
        }}
        
        .header-badge {{
            background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
            color: #fff;
            padding: 9px 18px;
            border-radius: 20px;
            font-size: 0.88rem;
            font-weight: 700;
            flex-shrink: 0;
            box-shadow: 0 4px 14px rgba(79, 70, 229, 0.30);
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        
        /* Toolbar */
        .toolbar {{
            max-width: 1200px;
            margin: 32px auto 0;
            padding: 0 32px;
            display: flex;
            gap: 14px;
            flex-wrap: wrap;
            align-items: center;
        }}
        
        .search-wrap {{
            flex: 1;
            min-width: 260px;
            position: relative;
        }}
        
        .search-wrap input {{
            width: 100%;
            padding: 16px 18px 16px 46px;
            border: 1px solid var(--border);
            border-radius: 14px;
            font-size: 0.95rem;
            background: var(--card-bg);
            color: var(--text-primary);
            transition: all 0.2s ease;
            outline: none;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
        }}
        
        .search-wrap input::placeholder {{ color: #9CA3AF; }}
        
        .search-wrap input:focus {{
            border-color: #6366F1;
            box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.12), 0 4px 14px rgba(15, 23, 42, 0.04);
        }}
        
        .search-wrap::before {{
            content: "🔍";
            position: absolute;
            left: 17px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 0.95rem;
            opacity: 0.45;
        }}
        
        .sort-select {{
            padding: 16px 18px;
            border: 1px solid var(--border);
            border-radius: 14px;
            font-size: 0.9rem;
            background: var(--card-bg);
            color: var(--text-secondary);
            cursor: pointer;
            outline: none;
            min-width: 160px;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
            transition: all 0.2s ease;
        }}
        
        .sort-select:focus {{
            border-color: #6366F1;
            box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.12);
        }}
        
        /* Filter chips */
        .filter-bar {{
            max-width: 1200px;
            margin: 18px auto 0;
            padding: 0 32px;
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            align-items: center;
        }}
        
        .filter-chip, .more-toggle {{
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            border: 1px solid var(--border);
            background: var(--card-bg);
            color: #374151;
            cursor: pointer;
            transition: all 0.15s ease;
            white-space: nowrap;
        }}
        
        .filter-chip:hover, .more-toggle:hover {{
            background: var(--primary-light);
            border-color: #C7D2FE;
            color: var(--primary-hover);
        }}
        
        .filter-chip.active {{
            background: var(--primary);
            border-color: var(--primary);
            color: #fff;
        }}
        
        .more-filters {{
            display: none;
            gap: 8px;
            flex-wrap: wrap;
            align-items: center;
            width: 100%;
            padding-top: 4px;
        }}
        
        .more-filters.open {{ display: flex; }}
        
        .clear-chip {{
            font-size: 0.85rem;
            color: var(--primary);
            cursor: pointer;
            padding: 8px 10px;
            font-weight: 600;
            display: none;
            background: none;
            border: none;
        }}
        
        .clear-chip.visible {{ display: inline-block; }}
        
        /* Grid */
        .container {{
            max-width: 1200px;
            margin: 32px auto 0;
            padding: 0 32px;
        }}
        
        .video-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 24px;
        }}
        
        /* Card */
        .video-card {{
            background: var(--card-bg);
            border: 1px solid rgba(226, 232, 240, 0.9);
            border-radius: 18px;
            overflow: hidden;
            box-shadow: var(--shadow-soft);
            cursor: pointer;
            transition: transform 160ms ease, box-shadow 160ms ease, border-color 160ms ease;
            animation: cardEnter 0.5s ease backwards;
            display: flex;
            flex-direction: column;
        }}
        
        .video-card.hidden {{ display: none; }}
        
        @keyframes cardEnter {{
            from {{ opacity: 0; transform: translateY(16px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .video-card:hover {{
            transform: translateY(-3px);
            box-shadow: var(--shadow-hover);
            border-color: #C7D2FE;
        }}
        
        .card-thumb {{
            position: relative;
            width: 100%;
            aspect-ratio: 16 / 9;
            background: #1e1e2e;
            overflow: hidden;
        }}
        
        .card-thumb-img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
            transition: transform 0.5s ease;
        }}
        
        .video-card:hover .card-thumb-img {{ transform: scale(1.05); }}
        
        .card-thumb-placeholder {{
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        
        .card-duration {{
            position: absolute;
            bottom: 10px;
            right: 10px;
            background: rgba(0,0,0,0.75);
            color: #fff;
            padding: 3px 8px;
            border-radius: 6px;
            font-size: 0.72rem;
            font-weight: 600;
            font-family: 'SF Mono', Monaco, monospace;
            backdrop-filter: blur(4px);
        }}
        
        .card-body {{
            padding: 20px 22px 22px;
            display: flex;
            flex-direction: column;
            flex: 1;
        }}
        
        .card-date {{
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.04em;
            color: #64748B;
            text-transform: uppercase;
            margin-bottom: 8px;
        }}
        
        .card-title {{
            font-size: 16px;
            line-height: 1.35;
            font-weight: 700;
            color: #111827;
            margin-bottom: 10px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        
        .card-preview {{
            font-size: 14px;
            line-height: 1.45;
            color: #4B5563;
            margin-bottom: 10px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }}
        
        .card-meta {{
            font-size: 12px;
            color: #64748B;
            font-weight: 500;
            margin-bottom: 14px;
        }}
        
        .card-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 5px;
            margin-bottom: 16px;
        }}
        
        .card-tag {{
            background: var(--primary-light);
            color: var(--primary);
            padding: 3px 10px;
            border-radius: 10px;
            font-size: 0.72rem;
            font-weight: 600;
        }}
        
        .card-actions {{
            display: flex;
            gap: 8px;
            align-items: center;
            margin-top: auto;
            flex-wrap: wrap;
        }}
        
        .action-btn {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            padding: 8px 14px;
            border-radius: 10px;
            font-size: 0.82rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            border: none;
            white-space: nowrap;
        }}
        
        .action-primary {{
            background: var(--primary);
            color: #fff;
        }}
        
        .action-primary:hover {{
            background: var(--primary-hover);
            transform: translateY(-1px);
        }}
        
        .action-secondary {{
            background: var(--card-bg);
            color: #334155;
            border: 1px solid var(--border);
        }}
        
        .action-secondary:hover {{
            background: var(--primary-light);
            border-color: #C7D2FE;
            color: var(--primary-hover);
        }}
        

        /* Empty state */
        .empty-state {{
            background: var(--card-bg);
            border-radius: 18px;
            padding: 80px 30px;
            text-align: center;
            color: var(--text-muted);
            grid-column: 1 / -1;
            border: 1px solid var(--border);
            box-shadow: var(--shadow-soft);
        }}
        
        .empty-icon {{ font-size: 3rem; margin-bottom: 16px; }}
        .empty-state p {{ margin-bottom: 8px; }}
        .empty-state code {{
            background: #f4f4f4;
            padding: 3px 10px;
            border-radius: 6px;
            font-family: 'SF Mono', Monaco, monospace;
            font-size: 0.85rem;
        }}
        
        /* Modal */
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }}
        
        .modal.active {{ display: flex; }}
        
        .modal-backdrop {{
            position: absolute;
            inset: 0;
            background: rgba(0,0,0,0.35);
            backdrop-filter: blur(6px);
        }}
        
        .modal-content {{
            position: relative;
            background: var(--card-bg);
            border-radius: 20px;
            max-width: 520px;
            width: 100%;
            max-height: 85vh;
            overflow-y: auto;
            box-shadow: 0 24px 80px rgba(0,0,0,0.25);
            animation: modalScaleIn 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            z-index: 1;
        }}
        
        @keyframes modalScaleIn {{
            from {{ opacity: 0; transform: scale(0.94) translateY(8px); }}
            to {{ opacity: 1; transform: scale(1) translateY(0); }}
        }}
        
        .modal-thumb {{
            position: relative;
            width: 100%;
            aspect-ratio: 16 / 9;
            background: #1e1e2e;
            overflow: hidden;
        }}
        
        .modal-thumb img {{ width: 100%; height: 100%; object-fit: cover; }}
        
        .modal-body {{ padding: 20px 24px 24px; }}
        
        .modal-header-row {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 12px;
            margin-bottom: 10px;
        }}
        
        .modal-header-row h2 {{
            font-size: 1.1rem;
            font-weight: 700;
            line-height: 1.4;
            color: var(--text-primary);
        }}
        
        .modal-close {{
            background: #f3f4f6;
            border: none;
            color: var(--text-muted);
            width: 32px;
            height: 32px;
            border-radius: 50%;
            font-size: 1.5rem;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            margin-top: -4px;
        }}
        
        .modal-close:hover {{
            background: var(--primary);
            color: #fff;
        }}
        
        .modal-meta {{
            display: flex;
            gap: 16px;
            margin-bottom: 12px;
            flex-wrap: wrap;
            color: var(--text-muted);
            font-size: 0.82rem;
        }}
        
        .modal-meta a {{
            color: var(--primary);
            text-decoration: none;
            font-weight: 500;
        }}
        
        .modal-meta a:hover {{ text-decoration: underline; }}
        
        .modal-tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-bottom: 14px;
        }}
        
        .modal-tags .card-tag {{
            background: var(--primary-light);
            color: var(--primary);
            padding: 3px 10px;
            border-radius: 10px;
            font-size: 0.78rem;
            font-weight: 600;
        }}
        
        .quick-summary {{
            background: #f9fafb;
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 16px;
        }}
        
        .quick-summary h3 {{
            color: var(--text-primary);
            font-size: 0.8rem;
            font-weight: 700;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.4px;
        }}
        
        .quick-summary p {{
            color: var(--text-secondary);
            line-height: 1.65;
            white-space: pre-line;
            font-size: 0.88rem;
        }}
        
        .modal-footer {{ text-align: center; }}
        
        .modal-cta {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: var(--primary);
            color: white;
            padding: 11px 22px;
            border-radius: 12px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.9rem;
            transition: all 0.2s ease;
        }}
        
        .modal-cta:hover {{ background: var(--primary-hover); }}
        
        /* Toast */
        .toast {{
            position: fixed;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%) translateY(20px);
            background: #1a1a1a;
            color: #fff;
            padding: 10px 22px;
            border-radius: 10px;
            font-size: 0.85rem;
            font-weight: 500;
            opacity: 0;
            transition: all 0.3s ease;
            z-index: 2000;
            pointer-events: none;
        }}
        
        .toast.show {{
            opacity: 1;
            transform: translateX(-50%) translateY(0);
        }}
        
        @media (max-width: 1024px) {{
            .video-grid {{ grid-template-columns: repeat(2, 1fr); }}
        }}
        
        @media (max-width: 640px) {{
            .header {{ padding: 28px 20px 24px; }}
            .header-inner {{ flex-direction: column; gap: 14px; }}
            .header-badge {{ margin-top: 0; }}
            .toolbar {{ padding: 0 20px; flex-direction: column; align-items: stretch; }}
            .sort-select {{ width: 100%; }}
            .filter-bar {{ padding: 0 20px; }}
            .container {{ padding: 0 20px; }}
            .video-grid {{ grid-template-columns: 1fr; gap: 18px; }}
            .modal-content {{ margin: 10px; max-height: 90vh; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-inner">
            <div class="header-brand">
                <img src="logo.png" alt="" class="header-logo">
                <div class="header-text">
                    <h1>Your Personal Video Summary Library</h1>
                    <p>Save, search, and understand long-form videos in minutes with key ideas and timestamps.</p>
                </div>
            </div>
            <div class="header-badge">▶ {len(video_dirs)} videos</div>
        </div>
    </div>
    
    <div class="toolbar">
        <div class="search-wrap">
            <input type="text" id="searchInput" placeholder="Search videos, topics, people, or tags..." oninput="filterVideos()">
        </div>
        <select class="sort-select" id="sortSelect" onchange="sortVideos()">
            <option value="date-desc">📅 Newest first</option>
            <option value="date-asc">📅 Oldest first</option>
            <option value="title-asc">🔤 Title A-Z</option>
            <option value="title-desc">🔤 Title Z-A</option>
        </select>
    </div>
    
    <div class="filter-bar">
        <button class="filter-chip active" data-tag="" onclick="clearFilter()">All</button>
        {priority_html}
        {f'<button class="more-toggle" id="moreBtn" onclick="toggleMore()">More&nbsp;▼</button>' if has_more else ''}
        <div class="more-filters" id="moreFilters">
            {more_html}
        </div>
        <button class="clear-chip" id="clearFilter" onclick="clearFilter()">✕ Clear</button>
    </div>
    
    <div class="container">
        <div class="video-grid" id="videoGrid">
{videos_html}
        </div>
    </div>
    
    <div class="toast" id="toast">Link copied!</div>
    
    <script>
        function openModal(index) {{
            document.getElementById('modal-' + index).classList.add('active');
            document.body.style.overflow = 'hidden';
        }}
        
        function closeModal(index) {{
            document.getElementById('modal-' + index).classList.remove('active');
            document.body.style.overflow = '';
        }}
        
        document.addEventListener('click', function(e) {{
            if (e.target.classList.contains('modal-backdrop')) {{
                e.target.parentElement.classList.remove('active');
                document.body.style.overflow = '';
            }}
        }});
        
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                document.querySelectorAll('.modal.active').forEach(m => m.classList.remove('active'));
                document.body.style.overflow = '';
            }}
        }});
        
        function filterVideos() {{
            const query = document.getElementById('searchInput').value.toLowerCase();
            document.querySelectorAll('.video-card').forEach(card => {{
                const title = card.getAttribute('data-title');
                const tags = card.getAttribute('data-tags').toLowerCase();
                card.classList.toggle('hidden', !(title.includes(query) || tags.includes(query)));
            }});
        }}
        
        let activeTag = null;
        function filterByTag(tag) {{
            const pills = document.querySelectorAll('.filter-chip');
            const clearBtn = document.getElementById('clearFilter');
            if (activeTag === tag) {{
                clearFilter();
                return;
            }}
            activeTag = tag;
            pills.forEach(p => p.classList.toggle('active', p.getAttribute('data-tag') === tag));
            clearBtn.classList.add('visible');
            document.querySelectorAll('.video-card').forEach(card => {{
                card.classList.toggle('hidden', !card.getAttribute('data-tags').includes(tag));
            }});
        }}
        
        function clearFilter() {{
            activeTag = null;
            document.querySelectorAll('.filter-chip').forEach(p => p.classList.remove('active'));
            document.querySelector('.filter-chip[data-tag=""]').classList.add('active');
            document.getElementById('clearFilter').classList.remove('visible');
            document.querySelectorAll('.video-card').forEach(card => card.classList.remove('hidden'));
        }}
        
        function sortVideos() {{
            const sortValue = document.getElementById('sortSelect').value;
            const grid = document.getElementById('videoGrid');
            const cards = Array.from(grid.querySelectorAll('.video-card'));
            cards.sort((a, b) => {{
                if (sortValue === 'date-desc') return b.getAttribute('data-date').localeCompare(a.getAttribute('data-date'));
                if (sortValue === 'date-asc') return a.getAttribute('data-date').localeCompare(b.getAttribute('data-date'));
                if (sortValue === 'title-asc') return a.getAttribute('data-title').localeCompare(b.getAttribute('data-title'));
                if (sortValue === 'title-desc') return b.getAttribute('data-title').localeCompare(a.getAttribute('data-title'));
                return 0;
            }});
            cards.forEach(card => grid.appendChild(card));
        }}
        
        function toggleMore() {{
            const el = document.getElementById('moreFilters');
            const btn = document.getElementById('moreBtn');
            el.classList.toggle('open');
            btn.innerHTML = el.classList.contains('open') ? 'Less&nbsp;▲' : 'More&nbsp;▼';
        }}
        
        function copyUrl(url) {{
            if (!url) return;
            navigator.clipboard.writeText(url).then(() => {{
                const toast = document.getElementById('toast');
                toast.textContent = 'Link copied!';
                toast.classList.add('show');
                setTimeout(() => toast.classList.remove('show'), 1800);
            }});
        }}
        

        document.querySelectorAll('.video-card').forEach((card, i) => {{
            card.style.animationDelay = (i * 0.06) + 's';
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

    # Copy logo from artifacts/ (single source of truth) into videos dir
    artifacts_logo = Path(__file__).parents[2] / 'artifacts' / 'logo.png'
    if artifacts_logo.exists():
        shutil.copy2(artifacts_logo, videos_dir / 'logo.png')

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
