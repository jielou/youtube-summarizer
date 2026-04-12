# 🎬 YouTube Video Summarizer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Version 0.1** — Early release, actively being improved

A skill for creating structured, interactive summaries of YouTube videos with timestamps, key points, and cross-cutting themes.

## 🤔 Why Use This Skill?

Compared to alternatives like **Notebook LM** or **Gemini**, this skill offers unique advantages:

| Feature | This Skill | Notebook LLM / Gemini |
|---------|-----------|----------------------|
| **Token Cost** | Uses your existing AI agent subscription | Additional tokens per video, costs add up quickly |
| **Centralized Management** | All summaries stored locally in one `videos/` folder | Dispersed across chat histories or cloud accounts |
| **Offline Access** | HTML files work without internet once generated | Requires ongoing access to the platform |
| **Data Ownership** | Your data stays on your machine | Uploaded to third-party services |
| **No Extra Sign-ups** | Works with Claude Code or Kimi Code you already have | Requires separate accounts and subscriptions |

### What Makes This Skill Special

🎨 **Beautiful HTML Visualization** — Unlike plain text summaries, get:
- **Interactive sidebar navigation** with clickable timestamps
- **Collapsible sections** for easy scanning
- **Theme-based organization** showing cross-cutting ideas
- **Responsive design** that works on mobile and desktop
- **Auto-generated index page** — all your videos in one searchable library

⚡ **No Friction** — No need to:
- Register for yet another AI product
- Upload videos to external services
- Manage API keys or pay per-use fees
- Copy-paste between different tools

🗂️ **Built for Collectors** — Designed for people who summarize videos regularly:
- Automatic organization by video
- Persistent local storage
- Quick access to your entire summary library
- Easy to share (just send the HTML files)

### See It In Action

**Index Page** — Your personal video library with quick summaries:

![Index Page](example_output/pages/main.png)

**Summary Page** — Interactive, timestamped breakdown with themes and sections:

![Summary Page](example_output/pages/summary.png)

📁 **Try the live example:** Open [`example_output/videos/index.html`](example_output/videos/index.html) in your browser.

## Table of Contents

- [Why Use This Skill?](#-why-use-this-skill)
- [What It Does](#-what-it-does)
- [How to Use](#-how-to-use)
- [Summary Structure](#-summary-structure)
- [Perfect For](#-perfect-for)
- [Directory Structure](#-directory-structure)
- [Technical Details](#-technical-details)
- [Tips for Best Results](#-tips-for-best-results)
- [Example Interaction](#-example-interaction)
- [Limitations](#-limitations)
- [Testing Status](#-testing-status)
- [Future Improvements](#-future-improvements)
- [For Developers](#-for-developers)
- [Registering as a Claude Skill](#-registering-as-a-claude-skill)
- [License](#-license)

## ✨ What It Does

This skill transforms YouTube videos into rich, structured summaries that are:

- 🎯 **Hierarchical** - Organized into sections with nested key points
- ⏱️ **Timestamped** - Every key insight linked to its moment in the video
- 🏷️ **Thematic** - Cross-cutting themes that span multiple sections
- 📱 **Interactive** - Beautiful HTML output with collapsible sections
- 🔗 **Indexed** - Auto-generated landing page listing all your videos

### Output Structure

```
videos/
├── index.html                    # 📑 Landing page with all videos
└── video-slug/
    ├── transcript.md             # 📝 Full transcript
    ├── summary.json              # 📊 Structured summary data
    └── summary.html              # 🎨 Beautiful interactive summary
```

## 🚀 How to Use

Simply tell your AI agent:

> **"Summarize this video for me: https://www.youtube.com/watch?v=..."**

The agent will:
1. ✅ Set up the project structure (if needed)
2. ✅ Fetch the video transcript and metadata
3. ✅ Create a summary template
4. ✅ Generate a structured summary with sections and key points
5. ✅ Create an interactive HTML page
6. ✅ Update the index with your new video
7. ✅ Open the summary for you to view

### What You Get

After the agent finishes, you can:

- 📖 **Read the summary** - Open `videos/<video-slug>/summary.html`
- 🔍 **Browse all videos** - Open `videos/index.html`
- ✏️ **Edit if needed** - Modify `videos/<video-slug>/summary.json` and ask the agent to regenerate
- 📤 **Share** - Send the HTML files or host them anywhere

## 📋 Summary Structure

The generated summaries follow this hierarchy:

```
Video
├── Themes (3-5 cross-cutting ideas)
│   ├── Theme 1: Description
│   ├── Theme 2: Description
│   └── ...
│
└── Sections (6-10 major segments)
    ├── Section 1
    │   ├── Timestamp
    │   ├── Summary (2-3 sentences)
    │   └── Key Points (3-5 with timestamps)
    ├── Section 2
    └── ...
```

### Features of the HTML Output

- 📋 **Table of Contents** - Jump to any section instantly
- 🔽 **Collapsible Sections** - Click to expand/collapse
- 🎯 **Themes Section** - Big-picture ideas at the top
- 📋 **Copy to Clipboard** - Get markdown version
- 📱 **Responsive Design** - Works on mobile and desktop
- 🔗 **Back Navigation** - Link back to index

## 🎯 Perfect For

- **Research** - Academic talks, lectures, conference presentations
- **Learning** - Educational videos, tutorials, courses
- **Meetings** - Capturing key points from recorded sessions
- **Podcasts** - Long-form interviews and discussions
- **Documentation** - Creating reference materials from demos

## 📂 Directory Structure

The skill maintains this structure automatically:

```
workspace/
└── videos/
    ├── index.html              # Index of all summarized videos
    ├── video-1/
    │   ├── transcript.md       # Full transcript
    │   ├── summary.json        # Structured data
    │   └── summary.html        # Interactive summary
    └── video-2/
        └── ...
```

## 🛠️ Technical Details

### Dependencies

The agent automatically handles:
- `youtube-transcript-api` - Fetching transcripts
- `yt-dlp` - Video metadata

### Supported URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `https://www.youtube.com/shorts/VIDEO_ID`

### Requirements

- Videos must have transcripts (auto-generated works!)
- YouTube only (currently)

## 💡 Tips for Best Results

1. **Long videos work great** - The structure helps navigate hours of content
2. **Educational/interview content** - Works best with clear topic shifts
3. **Edit if needed** - The agent creates a draft; you can refine the JSON
4. **Regenerate** - After editing `summary.json`, ask the agent to regenerate HTML

## 📝 Example Interaction

**You:**
> Summarize this video for me: https://www.youtube.com/watch?v=C0gErQtnNFE

**Agent:**
> I'll summarize that YouTube video for you. Let me start by fetching the transcript and setting up the summary structure...
> 
> ✅ Transcript fetched
> ✅ Summary template created  
> ✅ Summary completed with 12 sections and 4 themes
> ✅ HTML generated
> ✅ Index updated
>
> **Summary complete!** The video is about Demis Hassabis and AlphaFold solving the protein folding problem. Open `videos/the-hardest-problem-ai-ever-solved-with-google/summary.html` to view.

## ⚠️ Limitations

- **YouTube only** — Currently supports YouTube URLs only
- **Transcript dependent** — Videos without transcripts (auto-generated or manual) cannot be summarized
- **English optimized** — Best results with English content; other languages may have varying quality
- **No speaker diarization** — Cannot distinguish between multiple speakers in transcripts
- **Manual review needed** — AI-generated summaries may miss nuances; always review before publishing
- **Single video at a time** — No batch processing support yet

## ✅ Testing Status

This skill has been tested with:

| Platform | Status | Notes |
|----------|--------|-------|
| **Claude Code** | ✅ Working | Primary development platform |
| **Kimi Code** | ✅ Working | Fully compatible |

Both platforms handle the skill workflow correctly: fetching transcripts, generating summaries, and creating HTML output.

## 🚀 Future Improvements

Planned enhancements for upcoming versions:

- [ ] **Batch processing** — Summarize multiple videos in one command
- [ ] **Playlist support** — Process entire YouTube playlists
- [ ] **Export formats** — PDF, Markdown, and plain text export options
- [ ] **Search & filter** — Search across all your video summaries
- [ ] **Speaker detection** — Identify and label different speakers
- [ ] **Custom templates** — User-defined HTML/CSS themes
- [ ] **Offline mode** — Work with pre-downloaded transcripts
- [ ] **Multi-language** — Better support for non-English videos
- [ ] **Integration APIs** — Notion, Obsidian, and other note-taking tools

Have ideas? Open an issue or PR!

## 🔧 For Developers

Want to customize or extend? See `SKILL.md` for:
- Script documentation
- JSON schema details
- Customization options

## 🤖 Registering as a Claude Skill

To invoke this as a proper Claude skill (e.g. `use youtube-summarizer skill`), Claude needs to find the skill definition in its skills directory. The skill file must be registered at the **user level** AND the scripts must remain accessible from your **project root**.

### Required structure

```
~/.claude/skills/
└── youtube-summarizer/
    └── SKILL.md           ← copy of youtube-summarizer/SKILL.md

<your-project-root>/       ← Claude's working directory when invoked
├── youtube-summarizer/
│   └── scripts/           ← scripts called by SKILL.md
│       ├── process_video.py
│       ├── fetch_transcript.py
│       └── generate_html.py
└── videos/                ← created automatically on first run
```

### Registration steps

**1. Copy the skill definition to Claude's skills directory:**

```bash
mkdir -p ~/.claude/skills/youtube-summarizer
cp youtube-summarizer/SKILL.md ~/.claude/skills/youtube-summarizer/SKILL.md
```

**2. Open Claude Code from your project root** (the directory containing `youtube-summarizer/scripts/`), then try:

> use youtube-summarizer skill — summarize https://www.youtube.com/watch?v=...

### Why this structure?

- `~/.claude/skills/youtube-summarizer/SKILL.md` — makes the skill discoverable by Claude's `Skill` tool
- Scripts stay in your project under `youtube-summarizer/scripts/` — the SKILL.md references them with paths relative to the working directory (`python3 youtube-summarizer/scripts/...`)
- `videos/` is created in the current working directory — keep Claude's working directory at the project root so outputs land in the right place

### Alternative: reference directly in conversation

If you don't want to register the skill globally, you can load it inline by tagging the file in your message:

> use @youtube-summarizer/SKILL.md — summarize https://www.youtube.com/watch?v=...

---

**Just give the agent a YouTube URL and enjoy your structured summary!** 🎉

## 📄 License

This project is licensed under the [MIT License](LICENSE) — feel free to use, modify, and distribute!
