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
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f7;
            min-height: 100vh;
        }}
        
        /* Header - Full width */
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 40px;
            position: sticky;
            top: 0;
            z-index: 100;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
        }}
        
        .header-content {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header h1 {{
            font-size: 1.5rem;
            font-weight: 600;
            margin-bottom: 12px;
            line-height: 1.3;
        }}
        
        .header .meta {{
            opacity: 0.9;
            font-size: 0.9rem;
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            align-items: center;
        }}
        
        .video-link a {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255,255,255,0.2);
            color: white;
            padding: 6px 14px;
            border-radius: 20px;
            text-decoration: none;
            font-weight: 500;
            font-size: 0.85rem;
            transition: all 0.3s ease;
            border: 1px solid rgba(255,255,255,0.3);
        }}
        
        .video-link a:hover {{
            background: rgba(255,255,255,0.3);
        }}
        
        .summary-date {{
            font-size: 0.85rem;
            opacity: 0.8;
            font-style: italic;
        }}
        
        .tags {{
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 10px;
        }}
        
        .tag {{
            background: rgba(255,255,255,0.25);
            color: white;
            padding: 4px 12px;
            border-radius: 15px;
            font-size: 0.75rem;
            font-weight: 500;
        }}
        
        /* Main layout with sidebar */
        .main-layout {{
            display: flex;
            max-width: 1400px;
            margin: 0 auto;
            min-height: calc(100vh - 120px);
        }}
        
        /* Sidebar - Fixed on left */
        .sidebar {{
            width: 300px;
            background: white;
            border-right: 1px solid #e0e0e0;
            position: sticky;
            top: 0;
            height: 100vh;
            overflow-y: auto;
            padding: 20px 0;
        }}
        
        .sidebar-header {{
            padding: 0 20px 15px;
            border-bottom: 1px solid #e0e0e0;
            margin-bottom: 15px;
        }}
        
        .sidebar-title {{
            font-size: 0.9rem;
            font-weight: 600;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .back-link {{
            display: inline-flex;
            align-items: center;
            gap: 6px;
            color: #667eea;
            text-decoration: none;
            font-size: 0.85rem;
            font-weight: 500;
            margin-bottom: 12px;
            padding: 0 20px;
        }}
        
        .back-link:hover {{
            color: #764ba2;
        }}
        
        .toc-list {{
            list-style: none;
            padding: 0;
        }}
        
        .toc-item {{
            position: relative;
        }}
        
        .toc-link {{
            display: flex;
            align-items: flex-start;
            gap: 10px;
            padding: 10px 20px;
            color: #555;
            text-decoration: none;
            font-size: 0.9rem;
            transition: all 0.2s ease;
            border-left: 3px solid transparent;
        }}
        
        .toc-link:hover {{
            background: #f8f9fa;
            color: #667eea;
        }}
        
        .toc-link.active {{
            background: linear-gradient(90deg, #667eea15 0%, #764ba210 100%);
            color: #667eea;
            border-left-color: #667eea;
            font-weight: 500;
        }}
        
        .toc-time {{
            background: #e9ecef;
            color: #667eea;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-family: 'SF Mono', Monaco, monospace;
            white-space: nowrap;
            flex-shrink: 0;
        }}
        
        .toc-link.active .toc-time {{
            background: #667eea;
            color: white;
        }}
        
        .toc-text {{
            flex: 1;
            line-height: 1.4;
            padding-top: 2px;
        }}
        
        /* Main content area */
        .content-wrapper {{
            flex: 1;
            padding: 30px 40px;
            max-width: 900px;
        }}
        
        .content {{
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 2px 20px rgba(0,0,0,0.05);
        }}
        
        /* Themes Section */
        .themes-section {{
            background: linear-gradient(135deg, #f8f9fa 0%, #fff 100%);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 30px;
            border: 2px solid #667eea30;
        }}
        
        .themes-title {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #667eea;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .theme-item {{
            padding: 10px 0;
            padding-left: 20px;
            border-left: 3px solid #667eea40;
            margin-bottom: 10px;
        }}
        
        .theme-name {{
            font-weight: 600;
            color: #333;
        }}
        
        .theme-desc {{
            color: #666;
            font-size: 0.95rem;
            margin-top: 4px;
        }}
        
        /* Sections */
        .section {{
            margin-bottom: 30px;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 2px 12px rgba(0,0,0,0.06);
            border: 1px solid #e9ecef;
            scroll-margin-top: 140px;
        }}
        
        .section-header {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 20px 25px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 15px;
            transition: all 0.2s ease;
        }}
        
        .section-header:hover {{
            background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
        }}
        
        .section-header.active {{
            background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
        }}
        
        .section-toggle {{
            font-size: 1.1rem;
            color: #667eea;
            transition: transform 0.3s ease;
            width: 24px;
            text-align: center;
        }}
        
        .section-header.active .section-toggle {{
            transform: rotate(90deg);
        }}
        
        .section-title-group {{
            flex: 1;
        }}
        
        .section-time {{
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
            font-family: 'SF Mono', Monaco, monospace;
        }}
        
        .section-title {{
            font-size: 1.15rem;
            font-weight: 600;
            color: #333;
            margin-top: 8px;
        }}
        
        .section-content {{
            display: none;
            padding: 25px;
            background: white;
        }}
        
        .section-content.active {{
            display: block;
        }}
        
        .section-summary {{
            color: #555;
            font-size: 1rem;
            line-height: 1.7;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 3px solid #667eea;
        }}
        
        /* Key Points */
        .key-points-title {{
            font-size: 0.9rem;
            font-weight: 600;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 15px;
        }}
        
        .key-points {{
            list-style: none;
        }}
        
        .key-point {{
            display: flex;
            align-items: flex-start;
            padding: 12px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        .key-point:last-child {{
            border-bottom: none;
        }}
        
        .key-point-time {{
            background: #e9ecef;
            color: #667eea;
            padding: 3px 10px;
            border-radius: 15px;
            font-size: 0.8rem;
            font-weight: 600;
            font-family: 'SF Mono', Monaco, monospace;
            white-space: nowrap;
            margin-right: 15px;
            cursor: pointer;
            transition: all 0.2s ease;
            flex-shrink: 0;
        }}
        
        .key-point-time:hover {{
            background: #667eea;
            color: white;
        }}
        
        .key-point-text {{
            flex: 1;
            padding-top: 2px;
            line-height: 1.6;
        }}
        
        /* Copy Button */
        .copy-btn {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: #667eea;
            color: white;
            border: none;
            padding: 15px 25px;
            border-radius: 50px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            transition: all 0.3s ease;
            z-index: 100;
        }}
        
        .copy-btn:hover {{
            background: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
        }}
        
        .copy-btn.copied {{
            background: #28a745;
        }}
        
        /* Mobile responsive */
        @media (max-width: 1024px) {{
            .sidebar {{
                width: 260px;
            }}
            
            .content-wrapper {{
                padding: 20px;
            }}
        }}
        
        @media (max-width: 768px) {{
            .header {{
                padding: 20px;
            }}
            
            .header h1 {{
                font-size: 1.2rem;
            }}
            
            .main-layout {{
                flex-direction: column;
            }}
            
            .sidebar {{
                width: 100%;
                height: auto;
                position: relative;
                border-right: none;
                border-bottom: 1px solid #e0e0e0;
                max-height: 300px;
            }}
            
            .content-wrapper {{
                padding: 15px;
            }}
            
            .content {{
                padding: 20px;
            }}
            
            .section-header {{
                padding: 15px 20px;
            }}
            
            .section-title {{
                font-size: 1rem;
            }}
            
            .section-content {{
                padding: 20px;
            }}
            
            .key-point {{
                flex-direction: column;
            }}
            
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
            <h1>🎬 {title}</h1>
            <div class="meta">
                <span>📋 {total_key_points} Key Points</span>
                <span>📑 {total_sections} Sections</span>
                <span>⏱️ {duration}</span>
                {video_link_html}
            </div>
            {summary_date_html}
            {tags_html}
        </div>
    </div>
    
    <div class="main-layout">
        <nav class="sidebar">
            <a href="../index.html" class="back-link">← Back to all videos</a>
            <div class="sidebar-header">
                <div class="sidebar-title">📚 Contents</div>
            </div>
            <ul class="toc-list">
                {toc_items}
            </ul>
        </nav>
        
        <div class="content-wrapper">
            <div class="content">
                {themes_html}
                
                {sections_html}
            </div>
        </div>
    </div>
    
    <button class="copy-btn" onclick="copySummary()">📋 Copy Summary</button>
    
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
        
        // Copy to clipboard
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
        video_link_html = f'''<span class="video-link"><a href="{video_url}" target="_blank" rel="noopener">🎥 Watch on YouTube</a></span>'''
    else:
        video_link_html = ""
    
    # Generate summary date HTML if available
    if summary_date:
        summary_date_html = f'<div class="summary-date">📝 Summary created: {summary_date}</div>'
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
