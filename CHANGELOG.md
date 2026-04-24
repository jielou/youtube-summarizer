# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.3.0] - 2026-04-24

### Added

**Index page — full redesign**
- SaaS-style grid gallery with indigo accent and lavender/blue radial gradient header
- YouTube thumbnail cards with hover zoom and duration badge overlay
- Real-time search bar — filters cards by title or tag as you type
- Tag filter chips with "More ▼" overflow toggle for large tag collections
- Sort dropdown — by date (newest/oldest) or title (A-Z/Z-A)
- Quick preview modal — click any card to see themes and metadata before opening the full summary
- Card metadata row: 📋 key point count · ⏱ timestamp count · 📖 formatted duration
- Card preview text pulled from the first theme description
- Action buttons in modal: "Read Summary" (filled), "▶ Watch" and "↗ Share" (outlined)

**Summary page — full redesign**
- CSS custom properties for consistent theming throughout
- Light lavender/blue radial gradient header replacing the old solid dark-purple bar
- Logo badge in header with soft box shadow
- Stronger title hierarchy and improved metadata row layout
- Sidebar TOC: active item gets purple-blue background highlight + indigo timestamp pill
- Collapsible section cards with soft shadows and hover tint
- Themes card at top with indigo left accent bars and subtle dividers
- Floating "Copy" button — copies the full summary as markdown
- "🎥 Watch on YouTube" (filled indigo) and "↗ Share" (outlined) buttons in header
- Fully responsive — sidebar collapses gracefully on mobile

**Workflow & tooling**
- `verify_summary.py` — validates `summary.json` before generating HTML: catches large timestamp gaps (>15 min flagged, >20 min error), sections not spanning the full video, key points outside their section window, and out-of-order timestamps
- `reference.md` — internal reference for summary schema, field conventions, and extended tips
- `artifacts/` folder as the canonical home for shared assets (logo, etc.)
- Logo auto-copied from `artifacts/logo.png` into `videos/` on every index update — no more manual placement needed

### Changed
- `generate_html.py`: rebuilt from scratch with the new summary page design
- `process_video.py`: index rebuilt with richer cards, tag/search/sort/modal logic; added logo auto-copy via `shutil`
- `SKILL.md`: condensed and updated to reflect the new UI, features, and verify workflow
- `example_output/`: updated to use a new example video ("Building Claude Code with Boris Cherny") with the new HTML design


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
