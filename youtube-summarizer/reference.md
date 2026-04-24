# YouTube Summarizer — Reference

Extended documentation for the youtube-summarizer skill.

## Example Summary

```json
{
  "title": "How Fast Will A.I. Agents Rip Through the Economy?",
  "video_url": "https://www.youtube.com/watch?v=lIJelwO8yHQ",
  "duration": "1:38:00",
  "summary_date": "2026-04-11",
  "tags": ["AI", "Anthropic", "Economy", "Ezra Klein"],
  "themes": [
    {
      "name": "The Shift from Tools to Agents",
      "description": "AI is evolving from passive tools (chatbots) to active agents that can work autonomously"
    },
    {
      "name": "Economic Disruption",
      "description": "AI agents threaten traditional software companies and entry-level white-collar jobs"
    },
    {
      "name": "Human-AI Collaboration",
      "description": "The future is not AI replacing humans, but humans managing teams of AI agents"
    }
  ],
  "sections": [
    {
      "time": "00:00:00",
      "title": "Introduction: The AI Agent Revolution",
      "summary": "Ezra Klein introduces the shift from AI proof-of-concepts to systems that can actually do useful work. The sci-fi models that can program independently and make jobs obsolete are here now.",
      "key_points": [
        {"time": "00:00:00", "text": "AI has shifted from 'talkers' to 'doers' - the models we were waiting for are here"},
        {"time": "00:00:31", "text": "S&P 500 Software index fell 20%, threatening traditional software companies"},
        {"time": "00:01:34", "text": "2023-2024 were talkers; 2026-2027 will be agents that work together"}
      ]
    },
    {
      "time": "00:02:05",
      "title": "What Are AI Agents?",
      "summary": "Jack Clark explains AI agents as language models that can use tools and work autonomously over time, like a colleague rather than a chatbot.",
      "key_points": [
        {"time": "00:02:43", "text": "An AI agent can be given instruction and goes away to do stuff for you"},
        {"time": "00:03:12", "text": "Clark built a species simulation in 10 minutes that would take days manually"},
        {"time": "00:04:18", "text": "Success requires treating Claude as extremely literal, not like a knowledgeable person"}
      ]
    }
  ]
}
```

## Structure Guidelines

**Sections (6-10 recommended):**
- Each section covers a major topic or discussion segment
- Has a clear title, timestamp, and summary
- Contains 3-5 key points
- Sections are collapsible in the HTML output

**Key Points (3-5 per section):**
- Specific insights, quotes, or takeaways
- Each has its own timestamp
- Concise (1 sentence ideally, 2 max)
- Listed under their parent section

**Themes (optional, 3-5 recommended):**
- Cross-cutting ideas that span multiple sections
- Big-picture concepts or recurring topics
- Help readers understand the forest, not just trees

**Optional Fields:**
- `video_url`: Link to the YouTube video
- `duration`: Total video length (displayed in header)
- `summary_date`: When the summary was created
- `tags`: Array of topic tags (max 5 recommended)

## HTML Features

### Summary Page (`summary.html`)

Polished product detail page with purple-blue indigo branding (same design system as homepage):
- **Branded Header**: Light lavender/blue radial gradient, bold title, icon metadata (📋 key points · 📑 sections · ⏱️ duration · 📝 date), indigo pill tags
- **Primary Actions**: "🎥 Watch on YouTube" (filled indigo button) + "↗ Share" (outlined button that copies video URL)
- **Sidebar Navigation**: Rounded white card with table of contents, active item highlighted with light purple-blue background + brand-colored left accent bar + indigo timestamp pill
- **Bidirectional Sync**: Click section header ↔ sidebar updates
- **Collapsible Section Cards**: White rounded cards with soft shadows and subtle borders; hover gets light purple-blue tint; expanded state gets stronger border + more breathing room
- **Themes Card**: White rounded card with indigo left accent bars and subtle dividers between theme items
- **Copy to Clipboard**: One-click markdown export (indigo floating button)
- **Responsive Design**: Sidebar becomes scrollable panel on mobile, cards stack cleanly
- **Smooth Scrolling**: Click TOC items to scroll smoothly

### Index Page (`index.html`)

Polished SaaS-style gallery with indigo accent color:
- **Branded Header**: Radial lavender/blue gradient, app icon, "Your Personal Video Summary Library" title, indigo pill badge (▶ N videos)
- **Grid Layout**: Responsive 3-column grid (2 tablet, 1 mobile)
- **YouTube Thumbnails**: Fetched automatically from video IDs with duration badges
- **Card Previews**: 2-line description from first theme + icon metadata (📋 key points · ⏱ timestamps · 📖 formatted duration)
- **Search**: Real-time filtering by title and tags
- **Tag Filter Chips**: Indigo selected state, "More ▼" toggle for overflow tags
- **Sort**: By date (newest/oldest) or title (A-Z/Z-A)
- **Action Buttons**: "Read summary" (filled indigo), "▶ Watch" and "↗ Share" (outlined)
- **Quick Preview Modal**: Click any card for theme summary with full CTA
- **Staggered Entrance Animation**: Cards animate in on page load

```
┌─────────────────────────────────────────────────────────┐
│  Header (sticky) - Title + Search + Sort + Tag Filters │
├─────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │  Thumbnail  │  │  Thumbnail  │  │  Thumbnail  │    │
│  │  Title      │  │  Title      │  │  Title      │    │
│  │  Tags       │  │  Tags       │  │  Tags       │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│  ┌─────────────┐  ┌─────────────┐                      │
│  │  Thumbnail  │  │  Thumbnail  │                      │
│  │  Title      │  │  Title      │                      │
│  │  Tags       │  │  Tags       │                      │
│  └─────────────┘  └─────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

## Verification

Before generating HTML, always run the verification script to catch timestamp issues:

```bash
python3 youtube-summarizer/scripts/verify_summary.py \
  -i videos/<slug>/summary.json \
  -d HH:MM:SS
```

**What it checks:**
- First section starts near `00:00`
- Last section is near the video end (no trailing 15+ min gaps)
- No large gaps between consecutive sections (>15 min warning, >20 min error)
- Timestamps are in ascending order
- Key points fall within their section's time range (±3 min buffer)

**Why this matters:** For videos >1 hour, it's easy to front-load sections and leave 20-30 minute chunks uncovered. The script catches this automatically.

**If you get warnings:** Open the transcript and check the actual timestamps at the flagged boundaries. Adjust section times or add missing sections.

## Commands

### Process Video

```bash
python3 youtube-summarizer/scripts/process_video.py "YOUTUBE_URL" [options]
```

Options:
- `--videos-dir PATH` — Base directory for videos (default: `./videos`)
- `--language CODE` — Preferred transcript language

### Fetch Transcript Only

```bash
python3 scripts/fetch_transcript.py "URL" --output path/to/transcript.md
```

### Generate HTML

```bash
python3 youtube-summarizer/scripts/generate_html.py \
  --input videos/<slug>/summary.json \
  --output videos/<slug>/summary.html
```

Also regenerates `videos/index.html` automatically.

## Tips for Creating Good Summaries

### Verifying Timestamps (Critical for Long Videos)

**The #1 mistake:** Writing summaries from memory/notes and guessing timestamps. A section you think is at 00:20 might actually be at 00:35.

**Always verify:**
1. Run `verify_summary.py` before generating HTML
2. Spot-check 2-3 section boundaries against the transcript
3. For a 2-hour video, aim for 10-14 sections with roughly even coverage
4. The last section should be within ~15 min of the video end

**Red flags:**
- Gaps >15 minutes between sections
- All sections clustered in the first half of the video
- Key point timestamps that don't match the transcript

### Identifying Sections

Look for:
- Topic changes or transitions
- New speakers or interview segments
- Question/answer shifts
- Clear thematic breaks

### Writing Section Summaries

- 2-3 sentences capturing the essence
- Include the main argument or insight
- Mention any important context

### Extracting Key Points

Focus on:
- **For interviews:** Interviewee's substantive responses (not setup questions)
- Specific claims with evidence
- Surprising or counterintuitive insights
- Actionable advice or takeaways
- Memorable quotes
- Important definitions or explanations

### Identifying Themes

Ask yourself:
- What ideas keep coming up?
- What's the bigger picture?
- What connects different sections?
- What would someone need to understand to 'get' this video?
