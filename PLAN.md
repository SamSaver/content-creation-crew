# AI Content Creator Workflow Plan

## Overview

This CrewAI-based system continuously researches high-impact AI/ML topics and generates Medium-style articles with three distinct modes of operation.

## Workflow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           AI CONTENT CREATOR WORKFLOW                           │
└─────────────────────────────────────────────────────────────────────────────────┘

PHASE 1: CONTINUOUS RESEARCH (Automated, runs on schedule)
┌──────────────────┐
│  Research Crew   │ ◄── Queries AI news sources, arXiv, blogs, Twitter/X
│                  │     (Runs every 6 hours via cron or on-demand trigger)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Curator Agent    │ ◄── Ranks topics by impact, novelty, relevance
│                  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Topic Database   │ ◄── Stores: title, summary, source URLs, impact score,
│ (SQLite/JSON)    │     category tags, timestamp
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌─────────────────────────────────────────────────────┐
│ CLI/UI Present   │────►│  User sees:                                         │
│ Findings         │     │  • [1] Multi-Agent Reinforcement Learning (9.2/10)  │
│                  │     │  • [2] Mixture of Experts (MoE) Architecture (8.8/10)│
│                  │     │  • [3] Test-Time Compute Scaling (8.5/10)           │
│                  │     │  • [4] Neural Architecture Search (8.3/10)         │
│                  │     │  • [5] ... more options                             │
└──────────────────┘     └─────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────┐
│ User Selection   │ ◄── User picks topic + skill level (beginner/intermediate/expert)
│ (Interactive)    │
└────────┬─────────┘

PHASE 2: ARTICLE CREATION (Triggered after user selection)
         │
         ▼
┌──────────────────┐
│ Research Agent   │ ◄── Deep dive into selected topic
│ (Deep Research)  │     Gathers comprehensive information, papers, tutorials
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Content Planner  │ ◄── Creates article outline based on skill level
│                  │     Structures: concept → why it matters → fundamentals
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Writer Agent     │ ◄── Writes the Medium-style article
│                  │     • Engaging hook and introduction
│                  │     • Concept explanation (adapted to skill level)
│                  │     • Why it matters (real-world impact)
│                  │     • Fundamentals breakdown
│                  │     • Step-by-step getting started guide
│                  │     • Practical mini-project with code
│                  │     • Conclusion with resources
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Editor Agent     │ ◄── Reviews for clarity, accuracy, Medium style
│                  │     • Grammar and flow check
│                  │     • Technical accuracy verification
│                  │     • Readability optimization
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Code Validator   │ ◄── (Optional) Tests any code in the project section
│                  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐     ┌─────────────────────────────────────────────────────┐
│ Article Output   │────►│  Saved to: articles/{topic}_{date}.md               │
│ (Markdown)       │     │  User reviews and approves/rejects                   │
└──────────────────┘     └─────────────────────────────────────────────────────┘
         │
         ▼
┌──────────────────┐
│ Review Checkpoint│ ◄── PAUSE: User reviews article quality
│ (Interactive)    │     Options: [APPROVE] [REVISIONS_NEEDED] [REJECT]
└────────┬─────────┘
         │
         ▼ (If APPROVED)
┌──────────────────┐
│ Publisher Agent  │ ◄── Prepares for Medium publishing
│                  │     • Generates SEO-optimized title
│                  │     • Creates tags and topics
│                  │     • Extracts TL;DR/abstract
│                  │     • Suggests featured image
│                  │     • Formats for Medium import (HTML or markdown)
└────────┬─────────┘
         │
┌──────────────────┐
│  Final Output    │ ◄── Ready-to-publish files:
│                  │     • article_medium_ready.md (formatted)
│                  │     • metadata.json (title, tags, abstract, image prompt)
│                  │     • import_instructions.txt
└──────────────────┘
```

## Phase 1: Continuous Research System

### Crew: ResearchCrew

**Purpose:** Automatically discover and catalog trending AI/ML topics

#### Agents:

1. **Trend Scout Agent**
   - **Role:** AI News Scout
   - **Goal:** Monitor AI news sources for breakthrough research, trending topics, and emerging technologies
   - **Backstory:** Expert at scanning arXiv, AI blogs, research Twitter/X, and tech news
   - **Tools:** Web search, RSS feed reader, arXiv API, GitHub trending

2. **Impact Analyst Agent**
   - **Role:** Technology Impact Assessor
   - **Goal:** Evaluate each discovered topic for potential impact on the industry
   - **Backstory:** Former tech analyst who understands market trends and practical applications

3. **Topic Curator Agent**
   - **Role:** Content Strategist
   - **Goal:** Compile and rank topics, preparing them for user selection
   - **Backstory:** Experienced editor who knows what content resonates with different audiences

#### Tasks:

1. **discover_topics**
   - Search arXiv, Papers With Code, AI Twitter/X, tech blogs
   - Identify trending papers and breakthroughs
   - Output: Raw list of potential topics with brief summaries

2. **analyze_impact**
   - Score each topic on:
     - Innovation factor (1-10)
     - Practical relevance (1-10)
     - Beginner accessibility (1-10)
     - Current buzz/attention (1-10)
   - Categorize: AI/ML/DL/Agentic Systems/Emerging

3. **curate_findings**
   - Compile top 10-15 topics
   - Create compelling summaries
   - Save to database with metadata

#### Output:
- JSON/Database with topic entries:
  ```json
  {
    "id": "uuid",
    "title": "Mixture of Experts (MoE): Scaling Neural Networks",
    "summary": "Brief compelling summary...",
    "category": "Deep Learning",
    "impact_score": 8.8,
    "sources": ["arxiv_url", "blog_url"],
    "discovered_at": "timestamp",
    "status": "pending_selection"
  }
  ```

---

## Phase 2: Article Creation System

### Crew: ArticleCrew

**Purpose:** Generate high-quality, skill-level-appropriate Medium articles

#### Agents:

1. **Research Specialist Agent**
   - **Role:** Deep Research Analyst
   - **Goal:** Gather comprehensive information on the selected topic
   - **Backstory:** PhD-level researcher with expertise in synthesizing complex technical papers
   - **Tools:** Web search, code repository search, paper analysis

2. **Content Planner Agent**
   - **Role:** Technical Content Strategist
   - **Goal:** Create detailed article outline adapted to the chosen skill level
   - **Backstory:** Experienced technical writer who knows how to structure educational content

3. **Writer Agent**
   - **Role:** Technical Blogger
   - **Goal:** Write engaging, clear Medium-style articles
   - **Backstory:** Popular Medium technical writer with a gift for explaining complex concepts

4. **Editor Agent**
   - **Role:** Technical Editor
   - **Goal:** Ensure accuracy, clarity, and Medium-appropriate style
   - **Backstory:** Former editor at major tech publications

5. **Code Specialist Agent**
   - **Role:** Hands-on Developer
   - **Goal:** Create practical, runnable mini-projects
   - **Backstory:** Full-stack ML engineer who loves teaching through code

#### Tasks:

1. **deep_research**
   - Input: Selected topic + skill level
   - Research: Papers, tutorials, implementations, real-world applications
   - Output: Comprehensive research summary with key concepts, code examples, resources

2. **create_outline**
   - Adapt structure based on skill level:

   **BEGINNER Structure:**
   - Hook: Relatable real-world analogy
   - What is it? (Simple explanation, no jargon)
   - Why should you care? (Personal/professional benefits)
   - How it works (High-level, intuitive)
   - Getting started (Tools, first steps)
   - Mini-project: Copy-paste runnable example
   - Resources to learn more

   **INTERMEDIATE Structure:**
   - Hook: Technical problem it solves
   - Concept explanation (with some technical depth)
   - Why it matters (Industry applications)
   - Core fundamentals (Key algorithms/mechanisms)
   - Step-by-step implementation guide
   - Mini-project: Modify/extensible code example
   - Common pitfalls and best practices
   - Resources and next steps

   **EXPERT Structure:**
   - Hook: Cutting-edge research angle
   - Deep technical dive (architecture, mathematics)
   - State-of-the-art performance analysis
   - Implementation details and optimizations
   - Advanced techniques and variants
   - Mini-project: Production-ready implementation
   - Open research questions and opportunities
   - Citations and further reading

3. **write_article**
   - Generate complete article following outline
   - Include all required sections
   - Write in Medium style: conversational but informative
   - Add code blocks with explanations

4. **edit_article**
   - Review for clarity and flow
   - Verify technical accuracy
   - Ensure appropriate reading level
   - Check code correctness

5. **create_project**
   - Develop practical mini-project:
     - **Beginner:** Complete working example (~50 lines)
     - **Intermediate:** Extensible template with exercises (~100-150 lines)
     - **Expert:** Full implementation with tests, documentation (~200+ lines)
   - Include: README, requirements, step-by-step instructions

#### Output:
- `article.md` - Full article in markdown
- `code/` - Project files
- `metadata.json` - Title, tags, reading time, etc.

---

## Phase 3: Publishing Preparation

### Crew: PublishCrew

**Purpose:** Prepare article for Medium publication

#### Agents:

1. **SEO Optimizer Agent**
   - **Role:** SEO Specialist
   - **Goal:** Create optimized title, tags, and description
   - **Backstory:** Expert in Medium SEO and content discoverability

2. **Formatter Agent**
   - **Role:** Publication Formatter
   - **Goal:** Format article for Medium's editor
   - **Backstory:** Knows all Medium formatting quirks and best practices

3. **LinkedIn Content Creator Agent**
   - **Role:** Social Media Content Strategist
   - **Goal:** Create engaging LinkedIn post content to promote the Medium article
   - **Backstory:** Expert LinkedIn content creator who knows how to craft posts that drive engagement, use appropriate hashtags, and include compelling hooks that make professionals want to click and read

#### Tasks:

1. **optimize_metadata**
   - Generate 3 title options (catchy, descriptive, SEO-focused)
   - Extract keywords for tags (5-7 tags)
   - Create TL;DR (2-3 sentence summary)
   - Suggest featured image description

2. **format_for_medium**
   - Convert markdown to Medium-compatible format
   - Ensure proper heading hierarchy
   - Format code blocks for Medium
   - Handle image placeholders
   - Create import instructions

3. **create_linkedin_content**
   - Generate 3 LinkedIn post variations:
     - **Hook-focused:** Attention-grabbing opening with clear value proposition
     - **Story-focused:** Personal angle or journey sharing the insight
     - **Question-focused:** Thought-provoking question to spark discussion
   - Include:
     - Compelling opening hook (first 2 lines critical)
     - Brief summary of key insight from article
     - Clear call-to-action to read on Medium
     - Relevant hashtags (3-5 targeted tags)
     - Suggested emojis for visual appeal
   - Keep each post between 150-300 words for optimal LinkedIn engagement
   - Ensure tone matches skill level (beginner-friendly language vs. expert technical depth)

#### Output:
- `article_medium_ready.md` - Formatted article
- `metadata.json` - All publishing metadata
- `image_prompts.txt` - DALL-E/Midjourney prompts for featured image
- `publishing_instructions.txt` - Step-by-step upload guide
- `linkedin_posts.txt` - Three ready-to-copy LinkedIn post variations

---

## Implementation Plan

### Project Structure:

```
content_creator/
├── src/
│   └── content_creator/
│       ├── __init__.py
│       ├── main.py                           # Entry points
│       ├── flows/
│       │   ├── __init__.py
│       │   ├── research_flow.py              # Phase 1 flow
│       │   ├── article_flow.py               # Phase 2 flow
│       │   └── publish_flow.py               # Phase 3 flow
│       ├── crews/
│       │   ├── __init__.py
│       │   ├── research_crew/
│       │   │   ├── __init__.py
│       │   │   ├── config/
│       │   │   │   ├── agents.yaml
│       │   │   │   └── tasks.yaml
│       │   │   └── research_crew.py
│       │   ├── article_crew/
│       │   │   ├── __init__.py
│       │   │   ├── config/
│       │   │   │   ├── agents.yaml
│       │   │   │   └── tasks.yaml
│       │   │   └── article_crew.py
│       │   └── publish_crew/
│       │       ├── __init__.py
│       │       ├── config/
│       │       │   ├── agents.yaml
│       │       │   └── tasks.yaml
│       │       └── publish_crew.py
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── search_tools.py              # Web search, arXiv
│       │   ├── storage_tools.py             # Database operations
│       │   └── code_tools.py                # Code validation
│       └── database/
│           ├── __init__.py
│           └── topic_db.py                   # Topic storage
├── data/
│   └── topics.db                             # SQLite database
├── articles/                                 # Generated articles
├── outputs/                                  # Final publish-ready files
└── pyproject.toml
```

### Data Models:

```python
# State models for flows

class ResearchState(BaseModel):
    discovered_topics: List[Topic] = []
    curated_topics: List[Topic] = []

class ArticleState(BaseModel):
    selected_topic: Topic = None
    skill_level: str = "intermediate"  # beginner/intermediate/expert
    research_notes: str = ""
    outline: str = ""
    article_draft: str = ""
    final_article: str = ""
    project_code: str = ""
    review_status: str = "pending"  # pending/approved/revisions_needed

class PublishState(BaseModel):
    article: str = ""
    metadata: ArticleMetadata = None
    formatted_article: str = ""

class Topic(BaseModel):
    id: str
    title: str
    summary: str
    category: str
    impact_score: float
    difficulty_estimate: str
    sources: List[str]
    discovered_at: datetime
    status: str  # pending_selection/selected/in_progress/completed

class ArticleMetadata(BaseModel):
    title_options: List[str]
    tags: List[str]
    tldr: str
    reading_time: int
    featured_image_prompt: str
```

### CLI Interface:

```python
# Commands:

# Run continuous research (store results)
$ crewai run research

# Display topics and start article creation
$ crewai run create-article
  # Interactive: shows topic list, user selects + skill level

# Review pending articles
$ crewai run review
  # Shows articles awaiting approval
  # Options: approve, request revisions, reject

# Prepare approved articles for publishing
$ crewai run publish
  # Formats and generates metadata for Medium

# Run full workflow (with interactive checkpoints)
$ crewai run full-workflow
```

### Key Features:

1. **Checkpoint System:**
   - Flow pauses after Phase 1 (topic selection)
   - Flow pauses after Phase 2 (article review)
   - User input required to proceed

2. **Topic Storage:**
   - SQLite database for persistence
   - Topics accumulate over time
   - User can browse historical discoveries

3. **Skill Level Adaptation:**
   - Different writing personas per level
   - Adjusted technical depth
   - Appropriate code complexity

4. **Quality Gates:**
   - Editor review before user sees article
   - User approval before publishing prep

5. **Medium Integration:**
   - Proper markdown formatting
   - SEO-optimized metadata
   - Image generation prompts

### Tools Required:

1. **SearchTools:**
   - `search_arxiv()` - Query arXiv API
   - `search_news()` - Web search for AI news
   - `search_github()` - Find trending repos

2. **StorageTools:**
   - `save_topic()` - Store discovered topic
   - `get_pending_topics()` - Retrieve topics for selection
   - `update_topic_status()` - Mark selected/completed

3. **CodeTools:**
   - `validate_code()` - Check if code runs
   - `format_code()` - Apply code style

4. **UITools:**
   - `present_topics()` - Display interactive topic list
   - `get_user_selection()` - Capture user choice
   - `present_article()` - Show article for review

### Scheduling:

- **Research Phase:** Run every 6 hours via cron or `loop` skill
- **Article Creation:** On-demand or triggered by topic accumulation threshold
- **Publishing:** On-demand after user approval

---

## Success Criteria

1. Research discovers 5-10 high-quality topics per run
2. Articles are accurate, well-structured, and appropriate for skill level
3. Mini-projects are runnable and educational
4. Medium-ready output requires minimal manual editing
5. User can complete full workflow with <5 minutes of interaction

---

## Next Steps

1. Review and approve this plan
2. Set up database models and storage
3. Implement ResearchCrew
4. Implement ArticleCrew
5. Implement PublishCrew
6. Build CLI interface with checkpoints
7. Add scheduling for continuous research
8. Test end-to-end workflow
