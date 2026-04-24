---
name: youtube-summarizer
description: Summarize YouTube videos with key points and timestamps. Fetches transcripts, organizes summaries hierarchically (Sections → Key Points), and generates a browsable HTML index with search, filters, and thumbnails.
---

# YouTube Video Summarizer

Hierarchical video summaries with collapsible sections, cross-cutting themes, and a polished SaaS-style HTML interface (indigo accent, lavender header gradient, card previews, search & filters).

## Quick Start

**Important:** Run commands from your project root. `videos/` is created in your **current working directory**.

### Step 1: Process the Video

```bash
# Check deps
python3 -c "import youtube_transcript_api" 2>/dev/null || pip install youtube-transcript-api
python3 -c "import yt_dlp" 2>/dev/null || pip install yt-dlp

# Process video
python3 youtube-summarizer/scripts/process_video.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

This creates `./videos/<slug>/` with `transcript.md`, `summary.json` template, and updates `videos/index.html`.

### Step 2: Read the Transcript

```bash
# Read transcript to understand content
./videos/<slug>/transcript.md
```

### Step 3: Fill in summary.json

Edit `./videos/<slug>/summary.json`:

```json
{
  "title": "Video Title",
  "video_url": "https://youtube.com/watch?v=...",
  "duration": "1:38:00",
  "summary_date": "2026-04-11",
  "tags": ["AI", "Technology", "Economy"],
  "themes": [
    {"name": "Theme Name", "description": "Cross-cutting theme description"}
  ],
  "sections": [
    {
      "time": "00:00:00",
      "title": "Section Title",
      "summary": "Brief summary (2-3 sentences)",
      "key_points": [
        {"time": "00:01:30", "text": "Key point description"}
      ]
    }
  ]
}
```

**Guidelines:**
- **Tags:** 3-5 topic tags
- **Themes:** 3-5 cross-cutting themes
- **Sections:** 6-10 major sections, each with a timestamp, title, summary, and 3-5 key points
- **Key Points:** Concise insights with timestamps (1 sentence ideally)

**For videos > 1 hour — timestamp accuracy is critical:**

Long videos are especially prone to timestamp drift. It's easy to front-load sections and accidentally leave 20-30 minute gaps uncovered.

**Verify with the validation script (run BEFORE generating HTML):**
```bash
python3 youtube-summarizer/scripts/verify_summary.py \
  -i videos/<slug>/summary.json \
  -d HH:MM:SS
```

This catches:
- Large gaps between sections (>15 min flagged, >20 min error)
- Sections that don't span the full video
- Key points placed outside their section's time range
- Out-of-order timestamps

**Manual spot-check:** Sample the transcript at section boundaries:
```bash
# Check ~3 points in the video: start, middle, end
head -20 videos/<slug>/transcript.md
sed -n '4500,4520p' videos/<slug>/transcript.md
tail -20 videos/<slug>/transcript.md
```

**Common pitfall:** Writing sections from memory/notes without checking the transcript. A section you think is at "00:20" might actually start at "00:35". Always verify key timestamps against the transcript.

**Avoid:** All sections mapped to the first 40% of a long video, leaving the rest uncovered.

### Step 4: Generate HTML

```bash
python3 youtube-summarizer/scripts/generate_html.py \
  --input videos/<slug>/summary.json \
  --output videos/<slug>/summary.html
```

This also regenerates `videos/index.html` with the new design.

### Step 5: Open the Index

```bash
open ./videos/index.html   # macOS
xdg-open ./videos/index.html  # Linux
```

## What the User Sees

### Index Page (`videos/index.html`)

A polished SaaS-style grid gallery with indigo accents:
- **Branded header** with radial lavender/blue gradient, app icon, "Your Personal Video Summary Library" title, and indigo pill badge (▶ N videos)
- **Thumbnail cards** in a 3-column grid (2 tablet, 1 mobile) with YouTube thumbnails, duration badge, hover zoom
- **Card previews** — 2-line description from the first theme under each title
- **Icon metadata** — 📋 key points · ⏱ timestamps · 📖 formatted duration
- **Search bar** — filters cards by title or tag in real-time
- **Tag filter chips** — indigo selected state, "More ▼" toggle for overflow tags
- **Sort dropdown** — by date (newest/oldest) or title (A-Z/Z-A)
- **Quick preview modal** — click any card for theme summary with full CTA
- **Action buttons** — "Read summary" (filled), "▶ Watch" and "↗ Share" (outlined)

### Summary Page (`videos/<slug>/summary.html`)

Polished product detail page with the same purple-blue branding as the homepage:
- **Branded header** with light lavender/blue radial gradient, strong title hierarchy, icon metadata row, indigo pill tags
- **Primary actions** — "🎥 Watch on YouTube" (filled indigo) and "↗ Share" (outlined) buttons
- **Sidebar TOC** inside a rounded white card — active item gets light purple-blue background + brand-colored left accent bar + indigo timestamp pill
- **Collapsible section cards** — white rounded cards with soft shadows, hover tint, expanded state with stronger border and more breathing room
- **Themes card** at the top — white rounded card with indigo left accent bars and subtle dividers between items
- **Copy button** (floating, indigo) — copies the full summary as markdown
- **Responsive** — sidebar becomes scrollable on mobile, cards stack cleanly

## Directory Structure

```
./videos/
├── index.html                    # Auto-generated grid index
├── <video-slug>/
│   ├── transcript.md
│   ├── summary.json
│   └── summary.html              # Auto-generated full summary
└── ...
```

## Interview-Style Videos

Transcripts lack speaker labels. Distinguish by context:

| Interviewer | Interviewee |
|-------------|-------------|
| Setup questions | Core arguments & evidence |
| "Tell me about..." | Technical deep-dives |
| Follow-up prompts | Personal anecdotes |
| Transition phrases | Predictions & recommendations |

**Extract:** substantive responses, claims with evidence, memorable quotes, technical explanations, actionable takeaways.

**Skip:** "thank you for joining us", interviewer reactions, setup questions without substance, administrative transitions.

## Long Video Tips (Critical)

For videos > 1 hour, **timestamp accuracy is critical** (transcripts can have 10,000+ lines).

1. **Check duration** in `summary.json`
2. **Sample the transcript** at start, middle, and end:
   ```bash
   head -20 transcript.md
   sed -n '5000,5020p' transcript.md
   tail -20 transcript.md
   ```
3. **Map line numbers to timestamps**: Line 1000 ≈ 00:10:00, Line 5000 ≈ 00:50:00, etc.
4. **Verify coverage**: Sections must span the entire video
5. **Avoid**: All sections mapped to first 60 min of a 2.5 hr video

## Supported URLs

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`
- Direct video ID (11 characters)

## Setup (New Projects)

```bash
mkdir my-video-summaries && cd my-video-summaries
cp -r /path/to/youtube-summarizer/scripts .
python3 scripts/init_project.py   # creates videos/ directory
```

See `reference.md` for full examples, HTML features, detailed commands, and extended tips.
