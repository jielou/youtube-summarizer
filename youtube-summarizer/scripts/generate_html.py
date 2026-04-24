#!/usr/bin/env python3
"""
Generate an HTML summary file for YouTube video transcripts.
Supports hierarchical structure: Sections containing Key Points.
Features sidebar navigation with active section highlighting.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Import process_video's index generation function
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))
from process_video import generate_index_html


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Video Summary</title>
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
            --primary-lighter: #F5F7FF;
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
        }}
        
        /* ===== Header ===== */
        .header {{
            background:
                radial-gradient(circle at 15% 20%, rgba(99, 102, 241, 0.10), transparent 32%),
                radial-gradient(circle at 85% 80%, rgba(139, 92, 246, 0.07), transparent 35%),
                linear-gradient(135deg, #F5F7FF 0%, #EEF2FF 45%, #F8FAFC 100%);
            border-bottom: 1px solid var(--border);
            padding: 40px;
        }}
        
        .header-content {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header-brand {{
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 16px;
        }}
        
        .header-logo {{
            width: 44px;
            height: 44px;
            border-radius: 12px;
            flex-shrink: 0;
            object-fit: cover;
            box-shadow: 0 4px 14px rgba(79, 70, 229, 0.20);
        }}
        
        .header h1 {{
            font-size: 1.9rem;
            font-weight: 800;
            letter-spacing: -0.6px;
            line-height: 1.2;
            color: var(--text-primary);
        }}
        
        .header-meta {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            align-items: center;
            color: var(--text-secondary);
            font-size: 0.88rem;
            font-weight: 500;
            margin-bottom: 14px;
        }}
        
        .header-meta span {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }}
        
        .header-actions {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            align-items: center;
            margin-top: 14px;
        }}
        
        .btn-primary {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: var(--primary);
            color: #fff;
            padding: 10px 18px;
            border-radius: 10px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.88rem;
            border: none;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 4px 14px rgba(79, 70, 229, 0.30);
        }}
        
        .btn-primary:hover {{
            background: var(--primary-hover);
            transform: translateY(-1px);
            box-shadow: 0 6px 18px rgba(79, 70, 229, 0.40);
        }}
        
        .btn-secondary {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: var(--card-bg);
            color: #334155;
            padding: 10px 18px;
            border-radius: 10px;
            text-decoration: none;
            font-weight: 600;
            font-size: 0.88rem;
            border: 1px solid var(--border);
            cursor: pointer;
            transition: all 0.2s ease;
        }}
        
        .btn-secondary:hover {{
            background: var(--primary-light);
            border-color: #C7D2FE;
            color: var(--primary-hover);
        }}
        
        .tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 10px;
        }}
        
        .tag {{
            background: var(--primary-light);
            color: var(--primary);
            padding: 4px 12px;
            border-radius: 10px;
            font-size: 0.78rem;
            font-weight: 600;
        }}
        
        /* ===== Layout ===== */
        .main-layout {{
            display: flex;
            max-width: 1400px;
            margin: 0 auto;
            min-height: calc(100vh - 200px);
            gap: 28px;
            padding: 32px 40px 60px;
        }}
        
        /* ===== Sidebar ===== */
        .sidebar {{
            width: 300px;
            flex-shrink: 0;
        }}
        
        .sidebar-card {{
            background: var(--card-bg);
            border-radius: 18px;
            border: 1px solid rgba(226, 232, 240, 0.9);
            box-shadow: var(--shadow-soft);
            overflow: hidden;
            position: sticky;
            top: 24px;
            max-height: calc(100vh - 48px);
            display: flex;
            flex-direction: column;
        }}
        
        .back-link {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 600;
            padding: 16px 20px 14px;
            border-bottom: 1px solid var(--border);
            transition: all 0.2s ease;
        }}
        
        .back-link:hover {{
            color: var(--primary);
            background: var(--primary-lighter);
        }}
        
        .sidebar-header {{
            padding: 14px 20px 10px;
        }}
        
        .sidebar-title {{
            font-size: 0.82rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.6px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .toc-list {{
            list-style: none;
            padding: 0 12px 14px;
            overflow-y: auto;
        }}
        
        .toc-item {{
            position: relative;
        }}
        
        .toc-link {{
            display: flex;
            align-items: flex-start;
            gap: 10px;
            padding: 10px 12px;
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 0.87rem;
            transition: all 0.15s ease;
            border-radius: 10px;
            border-left: 3px solid transparent;
            margin-bottom: 2px;
        }}
        
        .toc-link:hover {{
            background: var(--primary-lighter);
            color: var(--text-primary);
        }}
        
        .toc-link.active {{
            background: var(--primary-light);
            color: var(--primary);
            border-left-color: var(--primary);
            font-weight: 600;
        }}
        
        .toc-time {{
            background: #f2f2f7;
            color: var(--text-muted);
            padding: 2px 8px;
            border-radius: 8px;
            font-size: 0.74rem;
            font-family: 'SF Mono', Monaco, monospace;
            white-space: nowrap;
            flex-shrink: 0;
            font-weight: 600;
        }}
        
        .toc-link.active .toc-time {{
            background: var(--primary);
            color: #fff;
        }}
        
        .toc-text {{
            flex: 1;
            line-height: 1.4;
            padding-top: 2px;
        }}
        
        /* ===== Content ===== */
        .content-wrapper {{
            flex: 1;
            min-width: 0;
            max-width: 900px;
        }}
        
        .content {{
            display: flex;
            flex-direction: column;
            gap: 24px;
        }}
        
        /* ===== Themes Card ===== */
        .themes-section {{
            background: var(--card-bg);
            border-radius: 18px;
            padding: 28px;
            border: 1px solid rgba(226, 232, 240, 0.9);
            box-shadow: var(--shadow-soft);
        }}
        
        .themes-title {{
            font-size: 0.85rem;
            font-weight: 700;
            color: var(--text-primary);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .theme-item {{
            padding: 18px 0;
            border-bottom: 1px solid var(--border);
            border-left: 3px solid var(--primary);
            padding-left: 20px;
            margin-left: 0;
        }}
        
        .theme-item:last-child {{
            border-bottom: none;
            padding-bottom: 0;
        }}
        
        .theme-item:first-child {{
            padding-top: 0;
        }}
        
        .theme-name {{
            font-weight: 700;
            color: var(--text-primary);
            font-size: 1rem;
            line-height: 1.4;
        }}
        
        .theme-desc {{
            color: var(--text-secondary);
            font-size: 0.95rem;
            margin-top: 6px;
            line-height: 1.65;
        }}
        
        /* ===== Section Accordion Cards ===== */
        .section {{
            background: var(--card-bg);
            border-radius: 18px;
            overflow: hidden;
            box-shadow: var(--shadow-soft);
            border: 1px solid rgba(226, 232, 240, 0.9);
            scroll-margin-top: 180px;
            transition: box-shadow 0.2s ease, border-color 0.2s ease;
        }}
        
        .section:hover {{
            box-shadow: var(--shadow-hover);
            border-color: #C7D2FE;
        }}
        
        .section-header {{
            padding: 20px 24px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 14px;
            transition: all 0.2s ease;
            background: var(--card-bg);
            border-bottom: 1px solid transparent;
        }}
        
        .section-header:hover {{
            background: var(--primary-lighter);
        }}
        
        .section-header.active {{
            background: var(--primary-light);
            border-bottom-color: #C7D2FE;
        }}
        
        .section-toggle {{
            font-size: 0.85rem;
            width: 26px;
            height: 26px;
            text-align: center;
            line-height: 26px;
            flex-shrink: 0;
            background: var(--primary-light);
            border-radius: 8px;
            color: var(--primary);
            font-weight: 700;
            transition: transform 0.3s ease;
        }}
        
        .section-header.active .section-toggle {{
            transform: rotate(90deg);
        }}
        
        .section-title-group {{
            flex: 1;
            min-width: 0;
        }}
        
        .section-time {{
            background: var(--primary-light);
            color: var(--primary);
            padding: 4px 12px;
            border-radius: 10px;
            font-size: 0.82rem;
            font-weight: 700;
            font-family: 'SF Mono', Monaco, monospace;
        }}
        
        .section-title {{
            font-size: 1.1rem;
            font-weight: 700;
            color: var(--text-primary);
            margin-top: 8px;
            line-height: 1.35;
        }}
        
        .section-content {{
            display: none;
            padding: 28px;
            background: var(--card-bg);
        }}
        
        .section-content.active {{
            display: block;
        }}
        
        .section-summary {{
            color: var(--text-secondary);
            font-size: 1rem;
            line-height: 1.75;
            margin-bottom: 24px;
            padding: 20px;
            background: #f9fafb;
            border-radius: 12px;
            border-left: 3px solid var(--primary);
        }}
        
        /* ===== Key Points ===== */
        .key-points-title {{
            font-size: 0.82rem;
            font-weight: 700;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 16px;
        }}
        
        .key-points {{
            list-style: none;
        }}
        
        .key-point {{
            display: flex;
            align-items: flex-start;
            padding: 14px 0;
            border-bottom: 1px solid var(--border);
        }}
        
        .key-point:last-child {{
            border-bottom: none;
        }}
        
        .key-point-time {{
            background: var(--primary-light);
            color: var(--primary);
            padding: 3px 10px;
            border-radius: 8px;
            font-size: 0.78rem;
            font-weight: 700;
            font-family: 'SF Mono', Monaco, monospace;
            white-space: nowrap;
            margin-right: 14px;
            cursor: pointer;
            transition: all 0.2s ease;
            flex-shrink: 0;
        }}
        
        .key-point-time:hover {{
            background: var(--primary);
            color: #fff;
        }}
        
        .key-point-text {{
            flex: 1;
            padding-top: 2px;
            line-height: 1.65;
            color: var(--text-primary);
        }}
        
        /* ===== Copy Button ===== */
        .copy-btn {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: var(--primary);
            color: white;
            border: none;
            padding: 14px 24px;
            border-radius: 14px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 6px 20px rgba(79, 70, 229, 0.35);
            transition: all 0.3s ease;
            z-index: 100;
        }}
        
        .copy-btn:hover {{
            background: var(--primary-hover);
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(79, 70, 229, 0.45);
        }}
        
        .copy-btn.copied {{
            background: #10B981;
        }}
        
        /* ===== Toast ===== */
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
        
        /* ===== Mobile ===== */
        @media (max-width: 1024px) {{
            .sidebar {{ width: 260px; }}
            .main-layout {{ padding: 24px; gap: 20px; }}
        }}
        
        @media (max-width: 768px) {{
            .header {{ padding: 24px 20px; }}
            .header h1 {{ font-size: 1.4rem; }}
            .header-meta {{ gap: 12px; }}
            .main-layout {{
                flex-direction: column;
                padding: 16px;
                gap: 16px;
            }}
            .sidebar {{
                width: 100%;
                position: relative;
            }}
            .sidebar-card {{
                position: relative;
                top: 0;
                max-height: 320px;
            }}
            .content-wrapper {{ padding: 0; }}
            .themes-section,
            .section-content {{ padding: 20px; }}
            .section-header {{ padding: 16px 20px; }}
            .key-point {{ flex-direction: column; }}
            .key-point-time {{
                margin-bottom: 8px;
                margin-right: 0;
                align-self: flex-start;
            }}
            .copy-btn {{
                bottom: 20px;
                right: 20px;
                padding: 12px 20px;
                font-size: 0.9rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="header-brand">
                <img src="../logo.png" alt="" class="header-logo">
                <h1>{title}</h1>
            </div>
            <div class="header-meta">
                <span>📋 {total_key_points} key points</span>
                <span>📑 {total_sections} sections</span>
                <span>⏱️ {duration}</span>
                {summary_date_html}
            </div>
            {tags_html}
            <div class="header-actions">
                {video_link_html}
                {share_html}
            </div>
        </div>
    </div>
    
    <div class="main-layout">
        <nav class="sidebar">
            <div class="sidebar-card">
                <a href="../index.html" class="back-link">← Back to all videos</a>
                <div class="sidebar-header">
                    <div class="sidebar-title">📚 Contents</div>
                </div>
                <ul class="toc-list">
                    {toc_items}
                </ul>
            </div>
        </nav>
        
        <div class="content-wrapper">
            <div class="content">
                {themes_html}
                
                {sections_html}
            </div>
        </div>
    </div>
    
    <button class="copy-btn" onclick="copySummary()">📋 Copy Summary</button>
    <div class="toast" id="toast">Link copied!</div>
    
    <script>
        // Toggle sections
        document.querySelectorAll('.section-header').forEach(header => {{
            header.addEventListener('click', function() {{
                const content = this.nextElementSibling;
                const section = this.closest('.section');
                const isActive = content.classList.contains('active');
                
                // Close all sections
                document.querySelectorAll('.section-content').forEach(c => c.classList.remove('active'));
                document.querySelectorAll('.section-header').forEach(h => h.classList.remove('active'));
                
                // Open clicked section if it wasn't active
                if (!isActive) {{
                    content.classList.add('active');
                    this.classList.add('active');
                    
                    // Update sidebar highlight to match clicked section
                    if (section && section.id) {{
                        updateActiveTOC(section.id);
                    }}
                }}
            }});
        }});
        
        // Open first section by default
        document.querySelector('.section-header')?.click();
        
        // Smooth scroll to section and update active TOC
        document.querySelectorAll('.toc-link').forEach(link => {{
            link.addEventListener('click', function(e) {{
                e.preventDefault();
                const targetId = this.getAttribute('href').substring(1);
                const targetSection = document.getElementById(targetId);
                
                if (targetSection) {{
                    // Expand the section
                    const content = targetSection.querySelector('.section-content');
                    const header = targetSection.querySelector('.section-header');
                    document.querySelectorAll('.section-content').forEach(c => c.classList.remove('active'));
                    document.querySelectorAll('.section-header').forEach(h => h.classList.remove('active'));
                    content.classList.add('active');
                    header.classList.add('active');
                    
                    // Scroll to section
                    targetSection.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                    
                    // Update active TOC
                    updateActiveTOC(targetId);
                }}
            }});
        }});
        
        // Update active TOC item
        function updateActiveTOC(activeId) {{
            document.querySelectorAll('.toc-link').forEach(link => {{
                link.classList.remove('active');
                if (link.getAttribute('href') === '#' + activeId) {{
                    link.classList.add('active');
                }}
            }});
        }}
        
        // Scroll spy - update active TOC on scroll
        const observerOptions = {{
            root: null,
            rootMargin: '-150px 0px -60% 0px',
            threshold: 0
        }};
        
        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    updateActiveTOC(entry.target.id);
                }}
            }});
        }}, observerOptions);
        
        // Observe all sections
        document.querySelectorAll('.section').forEach(section => {{
            observer.observe(section);
        }});
        
        // Copy full summary to clipboard
        function copySummary() {{
            const title = document.querySelector('h1').textContent;
            let text = `# ${{title}}\\n\\n`;
            
            document.querySelectorAll('.section').forEach(section => {{
                const header = section.querySelector('.section-title');
                const time = section.querySelector('.section-time');
                const summary = section.querySelector('.section-summary');
                
                if (header && time) {{
                    text += `## [${{time.textContent}}] ${{header.textContent}}\\n\\n`;
                    if (summary) text += `${{summary.textContent}}\\n\\n`;
                    
                    const points = section.querySelectorAll('.key-point');
                    if (points.length > 0) {{
                        text += `**Key Points:**\\n`;
                        points.forEach(point => {{
                            const pt = point.querySelector('.key-point-time');
                            const txt = point.querySelector('.key-point-text');
                            text += `- [${{pt.textContent}}] ${{txt.textContent}}\\n`;
                        }});
                        text += `\\n`;
                    }}
                }}
            }});
            
            navigator.clipboard.writeText(text).then(() => {{
                const btn = document.querySelector('.copy-btn');
                btn.textContent = '✅ Copied!';
                btn.classList.add('copied');
                setTimeout(() => {{
                    btn.textContent = '📋 Copy Summary';
                    btn.classList.remove('copied');
                }}, 2000);
            }});
        }}
        
        // Copy video URL to clipboard
        function copyVideoUrl(url) {{
            if (!url) return;
            navigator.clipboard.writeText(url).then(() => {{
                const toast = document.getElementById('toast');
                toast.textContent = 'Video link copied!';
                toast.classList.add('show');
                setTimeout(() => toast.classList.remove('show'), 1800);
            }});
        }}
    </script>
</body>
</html>"""


def generate_html(data: dict) -> str:
    """Generate HTML from summary data with hierarchical structure."""
    title = data.get("title", "Video Summary")
    sections = data.get("sections", [])
    themes = data.get("themes", [])
    duration = data.get("duration", "")
    video_url = data.get("video_url", "")
    summary_date = data.get("summary_date", "")
    tags = data.get("tags", [])
    
    # Calculate totals
    total_key_points = sum(len(s.get("key_points", [])) for s in sections)
    total_sections = len(sections)
    
    # Generate themes HTML
    if themes:
        themes_html = '''            <div class="themes-section">
                <div class="themes-title">🎯 Cross-Cutting Themes</div>
'''
        for theme in themes:
            themes_html += f'''                <div class="theme-item">
                    <div class="theme-name">{theme.get("name", "")}</div>
                    <div class="theme-desc">{theme.get("description", "")}</div>
                </div>
'''
        themes_html += '            </div>\n'
    else:
        themes_html = ""
    
    # Generate TOC items (first one will be active by default)
    toc_items = []
    for i, section in enumerate(sections):
        section_id = f"section-{i}"
        time = section.get("time", "")
        section_title = section.get("title", f"Section {i+1}")
        active_class = "active" if i == 0 else ""
        toc_items.append(f'''                <li class="toc-item">
                    <a href="#{section_id}" class="toc-link {active_class}">
                        <span class="toc-time">{time}</span>
                        <span class="toc-text">{section_title}</span>
                    </a>
                </li>''')
    
    # Generate sections HTML
    sections_html = []
    for i, section in enumerate(sections):
        section_id = f"section-{i}"
        time = section.get("time", "")
        section_title = section.get("title", f"Section {i+1}")
        summary = section.get("summary", section.get("description", ""))
        key_points = section.get("key_points", [])
        active_class = "active" if i == 0 else ""
        content_active = "active" if i == 0 else ""
        
        section_html = f'''            <div class="section" id="{section_id}">
                <div class="section-header {active_class}">
                    <span class="section-toggle">▶</span>
                    <div class="section-title-group">
                        <span class="section-time">{time}</span>
                        <div class="section-title">{section_title}</div>
                    </div>
                </div>
                <div class="section-content {content_active}">
                    <div class="section-summary">{summary}</div>
                    
                    <div class="key-points-title">Key Points</div>
                    <ul class="key-points">
'''
        
        for kp in key_points:
            kp_time = kp.get("time", "")
            kp_text = kp.get("text", "")
            section_html += f'''                        <li class="key-point">
                            <span class="key-point-time">{kp_time}</span>
                            <span class="key-point-text">{kp_text}</span>
                        </li>
'''
        
        section_html += '''                    </ul>
                </div>
            </div>'''
        sections_html.append(section_html)
    
    # Generate video link HTML if available
    if video_url:
        video_link_html = f'''<a class="btn-primary" href="{video_url}" target="_blank" rel="noopener">🎥 Watch on YouTube</a>'''
        share_html = f'''<button class="btn-secondary" onclick="copyVideoUrl('{video_url}')">↗ Share</button>'''
    else:
        video_link_html = ""
        share_html = ""
    
    # Generate summary date HTML if available
    if summary_date:
        summary_date_html = f'<span>📝 {summary_date}</span>'
    else:
        summary_date_html = ""
    
    # Generate tags HTML if available
    if tags:
        tags_html = '<div class="tags">' + ''.join([f'<span class="tag">{tag}</span>' for tag in tags[:5]]) + '</div>'
    else:
        tags_html = ""
    
    return HTML_TEMPLATE.format(
        title=title,
        total_key_points=total_key_points,
        total_sections=total_sections,
        duration=duration,
        video_link_html=video_link_html,
        share_html=share_html,
        summary_date_html=summary_date_html,
        tags_html=tags_html,
        themes_html=themes_html,
        toc_items='\n'.join(toc_items),
        sections_html='\n'.join(sections_html)
    )


def main():
    parser = argparse.ArgumentParser(
        description="Generate HTML summary for YouTube video transcripts"
    )
    parser.add_argument(
        "--input", "-i",
        required=True,
        help="Path to JSON input file"
    )
    parser.add_argument(
        "--output", "-o",
        required=True,
        help="Path to HTML output file"
    )
    
    args = parser.parse_args()
    
    # Read input JSON
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Generate HTML
    html = generate_html(data)
    
    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"HTML summary generated: {output_path.absolute()}")
    
    # Update index.html to reflect the new summary
    videos_dir = output_path.parent.parent
    if videos_dir.name == "videos":
        index_path = videos_dir / "index.html"
        index_html = generate_index_html(videos_dir)
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_html)
        print(f"Index updated: {index_path}")


if __name__ == "__main__":
    main()
