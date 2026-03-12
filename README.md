# AI Content Creator

A CrewAI-powered workflow that researches trending AI/ML topics, generates Medium-style educational articles with hands-on projects, and prepares LinkedIn promotional content. Runs entirely locally using Ollama open-source LLMs.

## Features

- **Real-Time Research**: Discovers trending AI/ML topics from arXiv, DuckDuckGo news, and GitHub
- **Custom Topics**: Provide your own topic via CLI instead of using auto-discovery
- **Skill-Level Adaptation**: Generates articles for Beginner, Intermediate, or Expert audiences
- **Complete Article Pipeline**: Research -> Outline -> Writing -> Editing -> Code Projects
- **LinkedIn Integration**: Creates 3 promotional post variations (hook/story/question-focused)
- **Unified Flow Orchestration**: Single CrewAI flow manages the entire pipeline with checkpoints
- **100% Local**: No paid APIs required - uses Ollama for inference

## Prerequisites

- Python >=3.10, <3.14
- [Ollama](https://ollama.com) installed and running
- 16GB system RAM recommended (8GB VRAM minimum)

### Install Ollama and pull models

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the required models
ollama pull llama3.1:8b
ollama pull qwen2.5-coder:7b

# Start Ollama server (if not auto-started)
ollama serve
```

## Installation

```bash
cd content-creation-crew

# Install with uv (recommended)
uv sync

# Or with pip
pip install -e .
```

No API keys or `.env` file needed - everything runs locally via Ollama.

## Usage

### Full Workflow (Recommended)

Run the complete pipeline with interactive checkpoints:

```bash
crewai run full-workflow
```

This will:
1. Research and discover trending AI/ML topics
2. Present topics for you to select + choose skill level
3. Generate a complete article with code project
4. Pause for your review and approval
5. Prepare Medium-ready content + LinkedIn posts

### Custom Topic

Skip research and write about a topic of your choice:

```bash
add-topic --title "RAG Pipelines with LangChain" --level intermediate
add-topic --title "Fine-tuning LLMs" --summary "How to fine-tune open source LLMs on custom data" --level expert
add-topic -t "Neural Networks for Beginners" -l beginner
```

**Arguments:**
- `--title` / `-t` (required): The topic to write about
- `--summary` / `-s` (optional): Brief description (defaults to title)
- `--level` / `-l` (optional): `beginner`, `intermediate`, or `expert` (default: intermediate)

### Individual Commands

```bash
crewai run research        # Discover new AI/ML topics
crewai run select-topic    # Browse and select from discovered topics
crewai run create-article  # Select topic + create article
crewai run review          # Review and approve/reject articles
crewai run publish         # Prepare articles for Medium + LinkedIn
```

## Project Structure

```
content_creator/
├── src/content_creator/
│   ├── crews/
│   │   ├── research_crew/      # Discover and curate AI topics
│   │   ├── article_crew/       # Generate Medium articles + code projects
│   │   └── publish_crew/       # Prepare for Medium + LinkedIn
│   ├── flows/
│   │   └── __init__.py         # Flow orchestration (ContentCreationFlow)
│   ├── tools/
│   │   ├── search_tools.py     # arXiv, DuckDuckGo, GitHub search
│   │   ├── web_tools.py        # Web content reader
│   │   └── storage_tools.py    # Database operations
│   ├── database/
│   │   └── topic_db.py         # SQLite topic storage
│   └── main.py                 # CLI interface
├── data/                       # SQLite database
├── articles/                   # Generated articles + code projects
└── outputs/                    # Final Medium-ready + LinkedIn posts
```

## How It Works

### Phase 1: Research

The **ResearchCrew** discovers trending topics using real search tools:
- **Trend Scout**: Searches arXiv papers, AI news via DuckDuckGo, and GitHub trending repos
- **Impact Analyst**: Scores each topic on innovation, relevance, accessibility, and buzz
- **Topic Curator**: Saves top 10-15 topics to the SQLite database

### Phase 2: Article Creation

The **ArticleCrew** generates a complete article adapted to skill level:
- **Research Specialist**: Deep-dives into the topic using web search and content reading
- **Content Planner**: Creates a structured outline matched to skill level
- **Writer**: Writes engaging Medium-style content with code examples
- **Editor**: Reviews for accuracy, clarity, and style
- **Code Specialist**: Creates a runnable mini-project (uses `qwen2.5-coder:7b`)

| Level | Article Style | Project Size |
|-------|--------------|--------------|
| Beginner | Analogies, simple explanations | ~50 lines |
| Intermediate | Technical depth, implementation | ~100-150 lines |
| Expert | Deep technical dive, optimizations | ~200+ lines |

### Phase 3: Publishing

The **PublishCrew** prepares content for distribution:
- **SEO Optimizer**: Creates optimized titles, tags, and TL;DR
- **Formatter**: Formats article for Medium compatibility
- **LinkedIn Creator**: Generates 3 post variations (hook/story/question-focused)

## Output Files

| File | Location | Description |
|------|----------|-------------|
| Article draft | `articles/draft_{topic}.md` | Full article in markdown |
| Code project | `articles/project_{topic}.md` | Runnable mini-project |
| Medium-ready | `outputs/article_medium_ready.md` | Formatted for Medium import |
| LinkedIn posts | `outputs/linkedin_posts.txt` | 3 ready-to-copy posts |

## LLM Models Used

| Model | Used By | Purpose |
|-------|---------|---------|
| `ollama/llama3.1:8b` | All agents except code | General writing, research, editing |
| `ollama/qwen2.5-coder:7b` | Code Specialist | Code generation for mini-projects |

### Upgrade Recommendations

If you want better quality output while staying within 8GB VRAM:

- **`llama3.3:latest`**: Drop-in replacement for llama3.1:8b with better instruction following. Change `llm: ollama/llama3.1:8b` to `llm: ollama/llama3.3:latest` in the agent YAML files.
- **`qwen2.5:7b`**: Good at structured JSON output - useful for research/curator agents that need to produce formatted data.
- **`gemma2:9b`**: Strong at writing tasks - good candidate for the writer and linkedin_creator agents (may need quantization for 8GB VRAM).

You can mix models per agent by editing the `llm:` field in each crew's `config/agents.yaml`.

## Database Schema

Topics are stored in SQLite (`data/topics.db`):

| Field | Type | Description |
|-------|------|-------------|
| id | TEXT | Unique identifier (YYYYMMDD_NN) |
| title | TEXT | Topic name |
| summary | TEXT | Brief description |
| category | TEXT | AI/ML/DL/Agentic Systems/Emerging |
| impact_score | REAL | 1-10 score |
| difficulty_estimate | TEXT | beginner/intermediate/expert |
| sources | TEXT | JSON array of URLs |
| discovered_at | TEXT | ISO timestamp |
| status | TEXT | pending_selection/selected/in_progress/completed |

## Troubleshooting

**Ollama not responding:**
```bash
# Make sure Ollama is running
ollama serve
```

**Model not found:**
```bash
ollama pull llama3.1:8b
ollama pull qwen2.5-coder:7b
```

**Out of memory:**
- Close other applications using GPU memory
- Try smaller quantized models: `ollama pull llama3.1:8b-q4_0`

**Module not found errors:**
```bash
pip install -e .
```

**Database issues:**
```bash
rm -f data/topics.db  # Reset database
```

## License

MIT License
