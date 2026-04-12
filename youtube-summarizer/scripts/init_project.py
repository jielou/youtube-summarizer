#!/usr/bin/env python3
"""
Initialize a new YouTube Video Summarizer project.

This script sets up the initial directory structure for a new project:
- Creates the videos/ directory
- Creates an empty index.html
- Prints next steps

Usage:
    python3 init_project.py [target_directory]

If target_directory is not specified, uses the current directory.
"""

import argparse
import sys
from pathlib import Path


def init_project(target_dir: Path = None):
    """Initialize a new project structure."""
    
    if target_dir is None:
        target_dir = Path.cwd()
    else:
        target_dir = Path(target_dir).resolve()
    
    print(f"🎬 YouTube Video Summarizer - Project Initialization")
    print(f"=" * 60)
    print()
    
    # Create videos directory
    videos_dir = target_dir / 'videos'
    videos_dir.mkdir(parents=True, exist_ok=True)
    print(f"✅ Created videos directory: {videos_dir}")
    
    # Create empty index.html (will be populated on first video)
    index_path = videos_dir / 'index.html'
    if not index_path.exists():
        index_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YouTube Video Summaries</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            max-width: 600px;
            background: white;
            border-radius: 16px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
        }
        h1 { color: #667eea; margin-bottom: 20px; }
        p { color: #666; margin-bottom: 30px; }
        code {
            background: #f4f4f4;
            padding: 2px 8px;
            border-radius: 4px;
            font-family: 'SF Mono', Monaco, monospace;
            font-size: 0.9rem;
        }
        .steps {
            text-align: left;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            margin-top: 20px;
        }
        .steps ol {
            margin-left: 20px;
            color: #555;
        }
        .steps li {
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎬 YouTube Video Summaries</h1>
        <p>Welcome! This index will be automatically populated as you process videos.</p>
        
        <div class="steps">
            <p><strong>To get started:</strong></p>
            <ol>
                <li>Process your first video:<br>
                    <code>python3 scripts/process_video.py "YOUTUBE_URL"</code>
                </li>
                <li>Edit the generated <code>summary.json</code> file</li>
                <li>Generate the HTML summary</li>
                <li>This index will update automatically!</li>
            </ol>
        </div>
    </div>
</body>
</html>'''
        index_path.write_text(index_html, encoding='utf-8')
        print(f"✅ Created initial index.html: {index_path}")
    else:
        print(f"ℹ️  Index already exists: {index_path}")
    
    print()
    print(f"📁 Project structure:")
    print(f"   {target_dir}/")
    print(f"   └── videos/")
    print(f"       └── index.html")
    print()
    print(f"🚀 Next steps:")
    print(f"   1. Process your first video:")
    print(f"      python3 scripts/process_video.py \"https://youtube.com/watch?v=...\"")
    print()
    print(f"   2. Open the index:")
    if sys.platform == 'darwin':
        print(f"      open {videos_dir}/index.html")
    else:
        print(f"      xdg-open {videos_dir}/index.html")
    print()
    print(f"✨ Happy summarizing!")


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new YouTube Video Summarizer project",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 init_project.py              # Initialize in current directory
  python3 init_project.py ~/my-project # Initialize in specific directory
        """
    )
    parser.add_argument(
        "target_dir",
        nargs="?",
        help="Target directory for the project (default: current directory)"
    )
    
    args = parser.parse_args()
    
    try:
        init_project(args.target_dir)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
