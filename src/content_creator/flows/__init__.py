"""
Flows for the Content Creator workflow.
Each flow manages a phase of the process with checkpoint support.
"""
from pydantic import BaseModel
from crewai.flow import Flow, listen, start, router
from typing import List, Optional
import json
from datetime import datetime
from pathlib import Path

from content_creator.crews.research_crew.research_crew import ResearchCrew
from content_creator.crews.article_crew.article_crew import ArticleCrew
from content_creator.crews.publish_crew.publish_crew import PublishCrew
from content_creator.database.topic_db import TopicDatabase, Topic


# ─── State Models ─────────────────────────────────────────────

class ResearchState(BaseModel):
    discovered_topics: List[dict] = []
    curated_topics: List[dict] = []
    status: str = "idle"


class ArticleState(BaseModel):
    selected_topic: Optional[dict] = None
    skill_level: str = "intermediate"
    research_notes: str = ""
    outline: str = ""
    article_draft: str = ""
    final_article: str = ""
    project_code: str = ""
    status: str = "idle"
    review_status: str = "pending"


class PublishState(BaseModel):
    article: str = ""
    metadata: dict = {}
    formatted_article: str = ""
    linkedin_posts: str = ""
    status: str = "idle"


class ContentCreationState(BaseModel):
    """State for the unified end-to-end flow."""
    # Input configuration
    mode: str = "auto"  # "auto" (research-driven) or "custom" (user-provided topic)
    custom_topic: Optional[str] = None
    custom_summary: Optional[str] = None

    # Research phase
    research_completed: bool = False

    # Selection phase
    selected_topic: Optional[dict] = None
    skill_level: str = "intermediate"

    # Article phase
    article_content: str = ""
    project_code: str = ""
    article_approved: bool = False

    # Publish phase
    medium_article: str = ""
    linkedin_posts: str = ""

    # Status
    current_phase: str = "init"
    error: Optional[str] = None


# ─── Individual Phase Flows (backward compatibility) ──────────

class ResearchFlow(Flow[ResearchState]):
    """Flow for Phase 1: Continuous Research"""

    def __init__(self):
        super().__init__()
        self.db = TopicDatabase()

    @start()
    def start_research(self):
        print("\n" + "="*60)
        print("PHASE 1: CONTINUOUS RESEARCH")
        print("="*60)
        print("Discovering trending AI/ML topics...\n")
        self.state.status = "running"

    @listen(start_research)
    def discover_and_curate(self):
        try:
            result = ResearchCrew().crew().kickoff()
            print("\n" + "="*60)
            print("Research Complete!")
            print("="*60)
            self.state.status = "completed"
            return result
        except Exception as e:
            print(f"\nError during research: {e}")
            self.state.status = "error"
            return None


class ArticleFlow(Flow[ArticleState]):
    """Flow for Phase 2: Article Creation"""

    def __init__(self, topic: dict, skill_level: str = "intermediate"):
        super().__init__()
        self.state.selected_topic = topic
        self.state.skill_level = skill_level
        self.db = TopicDatabase()

    @start()
    def start_article_creation(self):
        topic = self.state.selected_topic
        print("\n" + "="*60)
        print("PHASE 2: ARTICLE CREATION")
        print("="*60)
        print(f"Topic: {topic.get('title', 'Unknown')}")
        print(f"Skill Level: {self.state.skill_level}")
        print("="*60 + "\n")
        self.state.status = "running"

        if topic and 'id' in topic:
            self.db.update_topic_status(topic['id'], 'in_progress')

    @listen(start_article_creation)
    def create_article(self):
        try:
            inputs = {
                'topic_title': self.state.selected_topic.get('title', ''),
                'topic_summary': self.state.selected_topic.get('summary', ''),
                'skill_level': self.state.skill_level
            }

            result = ArticleCrew().crew().kickoff(inputs=inputs)

            project_root = Path(__file__).parent.parent.parent.parent
            article_path = project_root / "articles" / f"draft_{self.state.selected_topic.get('title', 'article').replace(' ', '_')[:30]}.md"
            project_path = project_root / "articles" / f"project_{self.state.selected_topic.get('title', 'article').replace(' ', '_')[:30]}.md"

            if article_path.exists():
                with open(article_path, 'r') as f:
                    self.state.final_article = f.read()

            if project_path.exists():
                with open(project_path, 'r') as f:
                    self.state.project_code = f.read()

            print("\n" + "="*60)
            print("Article Creation Complete!")
            print("="*60)
            self.state.status = "completed"
            return result

        except Exception as e:
            print(f"\nError during article creation: {e}")
            self.state.status = "error"
            return None


class PublishFlow(Flow[PublishState]):
    """Flow for Phase 3: Publishing Preparation"""

    def __init__(self, article_content: str, topic: dict, skill_level: str):
        super().__init__()
        self.state.article = article_content
        self.topic = topic
        self.skill_level = skill_level

    @start()
    def start_publish_prep(self):
        print("\n" + "="*60)
        print("PHASE 3: PUBLISHING PREPARATION")
        print("="*60)
        print("Preparing article for Medium...")
        print("Creating LinkedIn content...\n")
        self.state.status = "running"

    @listen(start_publish_prep)
    def prepare_for_publishing(self):
        try:
            inputs = {
                'article_content': self.state.article,
                'article_title': self.topic.get('title', ''),
                'article_summary': self.topic.get('summary', ''),
                'skill_level': self.skill_level,
                'category': self.topic.get('category', 'AI/ML')
            }

            result = PublishCrew().crew().kickoff(inputs=inputs)

            project_root = Path(__file__).parent.parent.parent.parent

            article_path = project_root / "outputs" / "article_medium_ready.md"
            linkedin_path = project_root / "outputs" / "linkedin_posts.txt"

            if article_path.exists():
                with open(article_path, 'r') as f:
                    self.state.formatted_article = f.read()

            if linkedin_path.exists():
                with open(linkedin_path, 'r') as f:
                    self.state.linkedin_posts = f.read()

            print("\n" + "="*60)
            print("Publishing Preparation Complete!")
            print("="*60)
            print(f"Medium-ready article: {article_path}")
            print(f"LinkedIn posts: {linkedin_path}")

            self.state.status = "completed"
            return result

        except Exception as e:
            print(f"\nError during publishing prep: {e}")
            self.state.status = "error"
            return None


# ─── Unified Content Creation Flow ────────────────────────────

class ContentCreationFlow(Flow[ContentCreationState]):
    """
    Unified flow that orchestrates the entire content creation pipeline.
    Supports two modes:
    - "auto": Research trending topics → select → create → review → publish
    - "custom": User provides topic → create → review → publish
    """

    def __init__(self):
        super().__init__()
        self.db = TopicDatabase()
        self._project_root = Path(__file__).parent.parent.parent.parent

    @start()
    def initialize(self):
        """Entry point - sets up the flow and routes based on mode."""
        print("\n" + "="*70)
        print("AI CONTENT CREATOR".center(70))
        print("="*70)
        self.state.current_phase = "routing"
        return self.state.mode

    @router(initialize)
    def route_mode(self):
        """Route to research path or custom topic path."""
        if self.state.mode == "custom":
            return "custom_path"
        return "research_path"

    # ── Research Path ──

    @listen("research_path")
    def run_research(self):
        """Execute the research crew to discover trending topics."""
        print("\n" + "="*60)
        print("PHASE 1: RESEARCHING TRENDING AI/ML TOPICS")
        print("="*60 + "\n")
        self.state.current_phase = "research"

        try:
            ResearchCrew().crew().kickoff()
            self.state.research_completed = True
            print("\nResearch complete! Topics saved to database.")
        except Exception as e:
            print(f"\nError during research: {e}")
            self.state.error = str(e)

    @listen(run_research)
    def select_topic(self):
        """Present discovered topics and let user select one."""
        self.state.current_phase = "selection"

        topics = self.db.get_pending_topics(limit=15)
        if not topics:
            print("\nNo topics found. Research may have failed.")
            self.state.error = "No topics discovered"
            return

        print("\n" + "="*60)
        print("TOPIC SELECTION")
        print("="*60)
        print(f"\nFound {len(topics)} topic(s):\n")

        for i, topic in enumerate(topics, 1):
            print(f"  [{i}] {topic.title}")
            print(f"      Category: {topic.category} | Impact: {topic.impact_score:.1f}/10 | Level: {topic.difficulty_estimate}")
            print(f"      {topic.summary[:100]}...")
            print()

        # Get user selection
        while True:
            try:
                choice = input("Select a topic (number) or 'q' to quit: ").strip()
                if choice.lower() == 'q':
                    self.state.error = "User cancelled"
                    return
                choice = int(choice)
                if 1 <= choice <= len(topics):
                    break
                print(f"Please enter 1-{len(topics)}")
            except ValueError:
                print("Please enter a valid number")

        selected = topics[choice - 1]
        self.state.selected_topic = selected.model_dump()

        # Get skill level
        print("\nSkill level:")
        print("  [1] Beginner  [2] Intermediate  [3] Expert")
        while True:
            try:
                level = int(input("Choose (1-3): ").strip())
                if 1 <= level <= 3:
                    break
            except ValueError:
                pass
            print("Please enter 1, 2, or 3")

        self.state.skill_level = ["beginner", "intermediate", "expert"][level - 1]
        print(f"\nSelected: {selected.title} ({self.state.skill_level})")

    # ── Custom Topic Path ──

    @listen("custom_path")
    def setup_custom_topic(self):
        """Set up a user-provided custom topic."""
        self.state.current_phase = "custom_setup"

        title = self.state.custom_topic
        summary = self.state.custom_summary or title

        print(f"\nCustom topic: {title}")
        print(f"Skill level: {self.state.skill_level}")

        self.state.selected_topic = {
            'id': f"custom_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'title': title,
            'summary': summary,
            'category': 'Custom',
            'impact_score': 0,
            'difficulty_estimate': self.state.skill_level,
            'sources': '[]',
            'discovered_at': datetime.now().isoformat(),
            'status': 'selected'
        }

    # ── Article Creation (converges both paths) ──

    @listen(select_topic)
    def create_article_from_research(self):
        """Create article after research-based topic selection."""
        if self.state.error:
            return
        self._create_article()

    @listen(setup_custom_topic)
    def create_article_from_custom(self):
        """Create article from custom topic."""
        self._create_article()

    def _create_article(self):
        """Shared article creation logic."""
        topic = self.state.selected_topic
        if not topic:
            self.state.error = "No topic selected"
            return

        print("\n" + "="*60)
        print("PHASE 2: CREATING ARTICLE")
        print("="*60)
        print(f"Topic: {topic.get('title')}")
        print(f"Level: {self.state.skill_level}")
        print("="*60 + "\n")
        self.state.current_phase = "article_creation"

        try:
            inputs = {
                'topic_title': topic.get('title', ''),
                'topic_summary': topic.get('summary', ''),
                'skill_level': self.state.skill_level
            }

            ArticleCrew().crew().kickoff(inputs=inputs)

            # Read generated files
            safe_title = topic.get('title', 'article').replace(' ', '_')[:30]
            article_path = self._project_root / "articles" / f"draft_{safe_title}.md"
            project_path = self._project_root / "articles" / f"project_{safe_title}.md"

            if article_path.exists():
                with open(article_path, 'r') as f:
                    self.state.article_content = f.read()

            if project_path.exists():
                with open(project_path, 'r') as f:
                    self.state.project_code = f.read()

            print("\nArticle creation complete!")

        except Exception as e:
            print(f"\nError creating article: {e}")
            self.state.error = str(e)

    # ── Review ──

    @listen(create_article_from_research)
    def review_from_research(self):
        """Review checkpoint after research-path article creation."""
        self._review_article()

    @listen(create_article_from_custom)
    def review_from_custom(self):
        """Review checkpoint after custom-path article creation."""
        self._review_article()

    def _review_article(self):
        """Shared review logic."""
        if self.state.error or not self.state.article_content:
            return

        self.state.current_phase = "review"
        print("\n" + "="*60)
        print("ARTICLE REVIEW")
        print("="*60)

        # Show preview
        preview = self.state.article_content[:2000]
        print(preview)
        if len(self.state.article_content) > 2000:
            print("... [truncated for preview]")

        print("\n" + "-"*60)
        print("  [1] APPROVE - proceed to publishing")
        print("  [2] REJECT  - discard article")

        while True:
            try:
                choice = int(input("Your decision (1-2): ").strip())
                if choice in (1, 2):
                    break
            except ValueError:
                pass
            print("Please enter 1 or 2")

        if choice == 1:
            self.state.article_approved = True
            print("\nArticle approved!")
        else:
            self.state.article_approved = False
            print("\nArticle rejected.")

    # ── Publishing ──

    @listen(review_from_research)
    def publish_from_research(self):
        """Publish after research-path review."""
        self._publish()

    @listen(review_from_custom)
    def publish_from_custom(self):
        """Publish after custom-path review."""
        self._publish()

    def _publish(self):
        """Shared publishing logic."""
        if not self.state.article_approved or self.state.error:
            if not self.state.article_approved:
                print("\nSkipping publishing (article not approved).")
            return

        self.state.current_phase = "publishing"
        print("\n" + "="*60)
        print("PHASE 3: PUBLISHING PREPARATION")
        print("="*60)
        print("Preparing for Medium + LinkedIn...\n")

        try:
            topic = self.state.selected_topic
            inputs = {
                'article_content': self.state.article_content,
                'article_title': topic.get('title', ''),
                'article_summary': topic.get('summary', ''),
                'skill_level': self.state.skill_level,
                'category': topic.get('category', 'AI/ML')
            }

            PublishCrew().crew().kickoff(inputs=inputs)

            # Read generated files
            article_path = self._project_root / "outputs" / "article_medium_ready.md"
            linkedin_path = self._project_root / "outputs" / "linkedin_posts.txt"

            if article_path.exists():
                with open(article_path, 'r') as f:
                    self.state.medium_article = f.read()
                print(f"Medium-ready article: {article_path}")

            if linkedin_path.exists():
                with open(linkedin_path, 'r') as f:
                    self.state.linkedin_posts = f.read()
                print(f"LinkedIn posts: {linkedin_path}")

            print("\n" + "="*60)
            print("WORKFLOW COMPLETE!")
            print("="*60)
            self.state.current_phase = "completed"

        except Exception as e:
            print(f"\nError during publishing: {e}")
            self.state.error = str(e)
