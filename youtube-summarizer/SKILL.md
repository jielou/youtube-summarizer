---
name: youtube-summarizer
description: Summarize YouTube videos with key points and timestamps. Automatically fetches transcripts and video metadata from YouTube URLs, organizes summaries in a hierarchical structure (Sections → Key Points), and generates an HTML index page. Use when the user provides a YouTube URL and wants a structured summary.
---

# YouTube Video Summarizer

This skill provides a complete workflow for summarizing YouTube videos with a hierarchical structure:
- **Sections** as main containers (collapsible)
- **Key Points** nested within each section
- **Cross-Cutting Themes** for big-picture ideas

## Quick Start for Agents

When a user asks you to summarize a YouTube video, follow these steps:

**Important:** Videos are created in `./videos/` relative to your **current working directory** (where you run the command from). Make sure you're in the project root directory where you want the `videos/` folder to be created.

### Step 1: Check Dependencies and Process the Video

First, check if the required Python packages are installed and install any that are missing:

```bash
python3 -c "import youtube_transcript_api" 2>/dev/null || pip install youtube-transcript-api
python3 -c "import yt_dlp" 2>/dev/null || pip install yt-dlp
```

Then run the process_video.py script from your project root with the YouTube URL:

```bash
# From your project root directory (e.g., youtube_summarizer/)
python3 youtube-summarizer/scripts/process_video.py "https://www.youtube.com/watch?v=VIDEO_ID"
```

This will:
- Create a directory under `./videos/<slug>/` (in your current directory)
- Fetch the transcript and save as `transcript.md`
- Create a `summary.json` template
- Update `./videos/index.html` with the new video entry

### Step 2: Read the Transcript

Read the transcript file to understand the video content:

```bash
./videos/<slug>/transcript.md
```

### Step 3: Create the Summary

Edit `./videos/<slug>/summary.json` and fill in:

1. **Tags** (3-5 topics, e.g., ["AI", "Technology", "Economy"])
2. **Themes** (3-5 cross-cutting themes with descriptions)
3. **Sections** (6-10 major sections with):
   - Timestamp (HH:MM:SS format)
   - Section title
   - Brief summary (2-3 sentences)
   - 3-5 key points with timestamps

**For videos > 1 hour:** Verify your sections span the entire duration:
```bash
# Check section timestamp coverage (should span from ~00:00 to near video end)
grep '"time":' videos/<slug>/summary.json | head -5
grep '"time":' videos/<slug>/summary.json | tail -5
```
Ensure first section is near 00:00 and last section is near the video's end time.

### Step 4: Generate HTML Summary

After completing the summary.json, generate the HTML:

```bash
python3 youtube-summarizer/scripts/generate_html.py --input videos/<slug>/summary.json --output videos/<slug>/summary.html
```

**Note:** This automatically updates `videos/index.html` with the correct links and content.

### Step 5: Open the Index (REQUIRED)

**ALWAYS open the index.html file so the user can view the summary:**

```bash
open ./videos/index.html  # macOS
xdg-open ./videos/index.html  # Linux
```

## Directory Structure

The `videos/` directory is created in your **current working directory** (where you run the commands from):

```
./videos/                         # Created in current working directory
├── index.html                    # Index page listing all videos
├── <video-slug>/
│   ├── transcript.md             # Full transcript
│   ├── summary.json              # Summary data (hierarchical)
│   └── summary.html              # Generated visualization
└── ...
```

## Summary JSON Structure

```json
{
  "title": "Video Title",
  "video_url": "https://youtube.com/watch?v=...",
  "duration": "1:38:00",
  "summary_date": "2026-04-11",
  "tags": ["AI", "Technology", "Economy"],
  "themes": [
    {
      "name": "Theme Name",
      "description": "Brief description of this cross-cutting theme"
    }
  ],
  "sections": [
    {
      "time": "00:00:00",
      "title": "Section Title",
      "summary": "Brief summary of this section (2-3 sentences)",
      "key_points": [
        {"time": "00:01:30", "text": "Key point 1 description"},
        {"time": "00:05:45", "text": "Key point 2 description"}
      ]
    }
  ]
}
```

### Structure Guidelines

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
- `video_url`: Link to the YouTube video (displays "Watch on YouTube" button)
- `duration`: Total video length (displayed in header)
- `summary_date`: When the summary was created (e.g., "2026-04-11")
- `tags`: Array of topic tags (max 5 recommended)

## Contextual Understanding for Interviews

When summarizing interview-style videos (e.g., podcasts, Q&A sessions), use **contextual understanding** to focus on the content that matters:

### Identify Interviewer vs Interviewee

The transcript doesn't include speaker labels, but you can often distinguish by context:

| Interviewer (Questions) | Interviewee (Responses) |
|------------------------|-------------------------|
| Setup/introductory statements | Substantive explanations |
| "Tell me about..." | Detailed arguments with evidence |
| "What do you think about..." | Personal anecdotes and stories |
| Follow-up prompts | Technical deep-dives |
| Transition phrases | Key insights and takeaways |

### Focus on Interviewee Content

**DO extract:**
- Core arguments and explanations
- Specific claims with supporting evidence
- Memorable quotes or soundbites
- Technical explanations
- Personal experiences that illustrate points
- Predictions or recommendations

**SKIP:**
- "Thank you for joining us"
- "That's fascinating" (interviewer reactions)
- Setup questions without substance
- Repeated clarifications
- Administrative transitions

### Example: Interview Extraction

**Transcript snippet:**
```
[00:05:23] Host: So tell me about AI agents. What makes them different from regular chatbots?
[00:05:45] Guest: AI agents represent a fundamental shift from passive tools to active systems...
[00:06:12] Guest: The key difference is autonomy. A chatbot waits for input...
```

**Summary approach:**
- Skip the host's question
- Focus on the guest's explanation about autonomy and active systems
- Timestamp: `00:05:45`
- Key point: "AI agents shift from passive tools to autonomous systems that can act independently"

## Example Summary

```json
{
  "title": "How Fast Will A.I. Agents Rip Through the Economy?",
  "video_url": "https://www.youtube.com/watch?v=lIJelwO8yHQ",
  "duration": "1:38:00",
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

## HTML Features

- **Sidebar Navigation**: Fixed left sidebar with table of contents for easy navigation
- **Active Section Highlighting**: Sidebar automatically highlights the current section as you scroll, click sidebar items, or click section headers
- **Bidirectional Sync**: Click a section header in the main content and the sidebar updates; click a sidebar item and the section expands
- **Collapsible Sections**: Click section headers to expand/collapse content
- **Themes Section**: Big-picture ideas displayed at the top of the main content
- **Copy to Clipboard**: One-click button to copy the full summary as markdown
- **Responsive Design**: Sidebar collapses on mobile, works on all screen sizes
- **Sticky Header**: Video info stays visible while scrolling
- **Smooth Scrolling**: Click any TOC item to smoothly scroll to that section
- **Back Navigation**: Link back to index page

### Layout Overview

```
┌─────────────────────────────────────────────────────────┐
│  Header (sticky) - Title, Meta, Tags, Watch Link       │
├──────────┬──────────────────────────────────────────────┤
│          │                                              │
│ Sidebar  │   Main Content                               │
│ (fixed)  │   ┌──────────────────────────────────────┐   │
│          │   │ Themes Section                       │   │
│  📚      │   └──────────────────────────────────────┘   │
│ Contents │                                              │
│          │   ┌──────────────────────────────────────┐   │
│  [00:00] │   │ ▶ Section 1                          │   │
│  Intro   │   │   Summary text...                    │   │
│          │   │   • Key point 1                      │   │
│  [02:15] │   │   • Key point 2                      │   │
│  Topic   │   └──────────────────────────────────────┘   │
│          │                                              │
│  ...     │              ...                             │
│          │                                              │
├──────────┴──────────────────────────────────────────────┤
│  [📋 Copy Summary] - Floating button                    │
└─────────────────────────────────────────────────────────┘
```

## Detailed Commands

### Process Video

```bash
# Run from your project root directory
python3 youtube-summarizer/scripts/process_video.py "YOUTUBE_URL" [options]
```

Options:
- `--videos-dir PATH` - Base directory for videos (default: `./videos` in current working directory)
- `--language CODE` - Preferred transcript language

**Note:** By default, the `videos/` directory is created in your current working directory (`./videos/`). Use `--videos-dir` to specify a different location.

### Fetch Transcript Only

```bash
python3 scripts/fetch_transcript.py "URL" --output path/to/transcript.md
```

### Generate HTML

```bash
# Run from your project root directory
python3 youtube-summarizer/scripts/generate_html.py --input videos/<slug>/summary.json --output videos/<slug>/summary.html
```

**Note:** This command also updates the index.html automatically.

## Tips for Creating Good Summaries

### Handling Long Videos (Critical)

For videos longer than 1 hour, **timestamp accuracy is critical**. The transcript file may have 10,000+ lines, and content from different parts of the video can easily be misattributed to wrong timestamps.

**ALWAYS verify timestamp distribution:**

1. **Check the video duration** in `summary.json` (e.g., `"duration": "2:28:26"`)

2. **Sample the transcript at multiple points** to understand the timeline:
   ```bash
   # Check start, middle, and end timestamps
   head -20 transcript.md                    # See start timestamps
   sed -n '5000,5020p' transcript.md         # Check middle (~1 hour in)
   tail -20 transcript.md                    # See end timestamps
   ```

3. **Map content to correct timestamps** - When reading sections from different transcript locations, verify the actual timestamp in the file:
   - Line 1000 might be 00:10:00
   - Line 5000 might be 00:50:00  
   - Line 10000 might be 01:45:00

4. **Review step - Verify timestamp coverage:**
   - Your sections should span the ENTIRE video duration
   - First section: near 00:00
   - Last section: near end of video (e.g., 02:20:00 for a 2:28:26 video)
   - Check for large gaps between section timestamps

5. **Common mistake to avoid:**
   - ❌ Wrong: All sections mapped to first 60 minutes of a 2.5 hour video
   - ✅ Correct: Sections distributed across all 2.5 hours

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

## Supported URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`
- Direct video ID: `VIDEO_ID` (11 characters)

## Setup (For New Projects)

### Option A: Quick Setup (Recommended)

Use the initialization script to set up the project automatically:

```bash
# Create your project directory
mkdir my-video-summaries
cd my-video-summaries

# Copy the scripts directory
cp -r /path/to/youtube-summarizer/scripts .

# Initialize the project (creates videos/ in current directory)
python3 scripts/init_project.py
```

**Required files in `scripts/`:**
- `process_video.py` - Main script to process videos
- `fetch_transcript.py` - Fetches YouTube transcripts
- `generate_html.py` - Generates HTML from summary.json
- `init_project.py` - (Optional) Project initialization helper

### Option B: Manual Setup

Create the structure yourself:

```bash
# Create your project directory
mkdir my-video-summaries
cd my-video-summaries

# Create the videos directory in your project root
mkdir videos
```

The first time you process a video, `videos/index.html` will be created automatically.
