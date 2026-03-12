# AI Content Creator

A CrewAI-powered workflow that continuously researches the latest high-impact AI/ML topics, generates Medium-style educational articles, and prepares LinkedIn promotional content.

## Features

- **Continuous Research**: Automatically discovers trending AI/ML/DL topics from arXiv, news sources, and GitHub
- **Interactive Topic Selection**: Browse and select from curated high-impact topics
- **Skill-Level Adaptation**: Generates articles for Beginner, Intermediate, or Expert audiences
- **Complete Article Generation**: Research → Outline → Writing → Editing → Code Projects
- **LinkedIn Integration**: Creates promotional posts to share on LinkedIn
- **Checkpoint System**: Interactive workflow pauses for user approval at key stages

## Project Structure

```
content_creator/
├── src/content_creator/
│   ├── crews/
│   │   ├── research_crew/      # Discover and curate AI topics
│   │   ├── article_crew/       # Generate Medium articles
│   │   └── publish_crew/       # Prepare for Medium + LinkedIn posts
│   ├── flows/
│   │   └── __init__.py         # Flow orchestration with checkpoints
│   ├── tools/
│   │   ├── search_tools.py     # arXiv, news, GitHub search
│   │   └── storage_tools.py    # Database operations
│   ├── database/
│   │   └── topic_db.py         # SQLite topic storage
│   └── main.py                 # CLI interface
├── data/                       # SQLite database
├── articles/                   # Generated articles
└── outputs/                  # Final publish-ready files
```

## Installation

```bash
# Clone and navigate to the project
cd content_creator

# Install dependencies
pip install -e .

# Set your OpenAI API key in .env
echo "OPENAI_API_KEY=your_key_here" > .env
```

## Usage

### Quick Start - Full Workflow

Run the complete workflow with interactive checkpoints:

```bash
crewai run full-workflow
```

This will:
1. Research and discover trending AI topics
2. Present topics for you to select
3. Generate an article for your chosen skill level
4. Pause for your review and approval
5. Prepare Medium-ready content + LinkedIn posts

### Individual Commands

#### 1. Research Phase

Discover new AI/ML topics:

```bash
crewai run research
```

#### 2. Select and Create Article

Browse topics and create an article:

```bash
crewai run select-topic
crewai run create-article
```

#### 3. Review Article

Review and approve/reject generated articles:

```bash
crewai run review
```

#### 4. Prepare for Publishing

Generate Medium-ready content and LinkedIn posts:

```bash
crewai run publish
```

## How It Works

### Phase 1: Continuous Research

The **ResearchCrew** continuously monitors:
- arXiv for latest papers
- AI news and blogs
- GitHub trending repositories

Three agents work together:
- **Trend Scout**: Discovers topics from sources
- **Impact Analyst**: Scores topics on innovation, relevance, accessibility, buzz
- **Topic Curator**: Compiles and saves top 10-15 topics to database

### Phase 2: Article Creation

The **ArticleCrew** generates complete Medium articles:

Five agents collaborate:
- **Research Specialist**: Deep dive into selected topic
- **Content Planner**: Creates outline adapted to skill level
- **Writer**: Writes engaging Medium-style content
- **Editor**: Reviews for clarity, accuracy, and style
- **Code Specialist**: Creates practical mini-project

**Skill Level Adaptation:**

| Level | Article Structure | Project Size |
|-------|------------------|--------------|
| Beginner | Analogies, simple explanations | ~50 lines |
| Intermediate | Technical depth, implementation | ~100-150 lines |
| Expert | Deep technical dive, optimizations | ~200+ lines |

### Phase 3: Publishing Preparation

The **PublishCrew** prepares content for distribution:

Three agents:
- **SEO Optimizer**: Creates titles, tags, TL;DR
- **Formatter**: Formats for Medium compatibility
- **LinkedIn Creator**: Generates 3 promotional post variations:
  - Hook-focused: Attention-grabbing
  - Story-focused: Personal angle
  - Question-focused: Discussion-sparking

## Example Output

### Article Structure

```markdown
# [Article Title]

**TL;DR:** [2-3 sentence summary]

## [Engaging Hook]

## What Is [Topic]?

## Why It Matters

## The Fundamentals

## Getting Started

## Mini-Project: [Project Name]

### Prerequisites
### Step-by-Step Guide
### The Code
### Expected Output
### Extension Ideas

## Conclusion

## Further Reading
```

### LinkedIn Post Example

```
Just published a deep dive on Mixture of Experts (MoE) architectures! 🚀

These sparse architectures are changing how we scale LLMs - enabling models
with billions of parameters while keeping inference costs manageable.

I break down:
→ How MoE works (with intuitive analogies)
→ Real-world applications in GPT-4 and beyond
→ A hands-on implementation you can run in 10 minutes

If you're looking to understand the architecture behind some of today's
most powerful models, check it out 👇

[LINK]

#MachineLearning #AI #DeepLearning #LLMs #TechBlog
```

## Database Schema

Topics are stored in SQLite with the following fields:
- `id`: Unique identifier
- `title`: Topic name
- `summary`: Brief description
- `category`: AI/ML/DL/Agentic Systems/Emerging
- `impact_score`: 1-10 score
- `difficulty_estimate`: beginner/intermediate/expert
- `sources`: JSON array of URLs
- `discovered_at`: Timestamp
- `status`: pending_selection/selected/in_progress/completed

## Customization

### Adding New Search Sources

Edit `src/content_creator/tools/search_tools.py` to add new research tools:

```python
@tool("Search new source")
def search_new_source(query: str) -> str:
    # Implementation
    pass
```

### Modifying Article Structure

Edit `src/content_creator/crews/article_crew/config/tasks.yaml` to customize:
- Article sections
- Skill-level requirements
- Project complexity

### LinkedIn Post Styles

Edit `src/content_creator/crews/publish_crew/config/tasks.yaml` to:
- Add more post variations
- Change tone guidelines
- Modify hashtag strategies

## Environment Variables

Create a `.env` file with:

```
OPENAI_API_KEY=your_openai_key_here
MODEL=gpt-4o  # or gpt-4o-mini for cost savings
```

## Troubleshooting

**Module not found errors:**
```bash
pip install -e .
```

**Database issues:**
```bash
rm -f data/topics.db  # Reset database
```

**API rate limits:**
- The tool includes rate limiting
- Consider using GPT-4o-mini for development
- Add delays between research calls if needed

## Requirements

- Python >=3.10, <3.14
- OpenAI API key
- Internet connection (for research tools)

## License

MIT License - Feel free to modify and distribute.

## Acknowledgments

Built with [CrewAI](https://crewai.com) - a framework for orchestrating autonomous AI agents.