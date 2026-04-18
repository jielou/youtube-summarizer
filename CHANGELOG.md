# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.2.0] - 2026-04-18

### Added
- `CHANGELOG.md` to track project changes

### Changed
- `youtube-summarizer/SKILL.md`: Added detailed guidance for handling long videos (>1 hour), including timestamp verification techniques and common mistakes to avoid
- `.gitignore`: Added `videos/` directory to ignore generated video summary folders

## [0.1.0] - 2025-04-11

### Added
- Initial release of YouTube Video Summarizer
- `process_video.py` — Main script to process YouTube videos: fetches metadata, transcripts, creates summary templates, and updates the video index
- `fetch_transcript.py` — Fetches YouTube transcripts and saves them as Markdown
- `generate_html.py` — Generates interactive HTML summaries from `summary.json` with sidebar navigation, collapsible sections, themes, and copy-to-clipboard
- `init_project.py` — Project initialization helper
- Hierarchical summary structure: Sections → Key Points with cross-cutting Themes
- Auto-generated `videos/index.html` listing all summarized videos
- Support for multiple YouTube URL formats (watch, youtu.be, embed, shorts)
