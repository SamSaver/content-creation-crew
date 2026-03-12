"""
Flows for the Content Creator workflow.
Each flow manages a phase of the process with checkpoint support.
"""
from pydantic import BaseModel
from crewai.flow import Flow, listen, start, router
from typing import List, Optional
import json
from datetime import datetime

from content_creator.crews.research_crew.research_crew import ResearchCrew
from content_creator.crews.article_crew.article_crew import ArticleCrew
from content_creator.crews.publish_crew.publish_crew import PublishCrew
from content_creator.database.topic_db import TopicDatabase, Topic


class ResearchState(BaseModel):
    discovered_topics: List[dict] = []
    curated_topics: List[dict] = []
    status: str = "idle"  # idle/running/completed/error


class ArticleState(BaseModel):
    selected_topic: Optional[dict] = None
    skill_level: str = "intermediate"
    research_notes: str = ""
    outline: str = ""
    article_draft: str = ""
    final_article: str = ""
    project_code: str = ""
    status: str = "idle"
    review_status: str = "pending"  # pending/approved/revisions_needed/rejected


class PublishState(BaseModel):
    article: str = ""
    metadata: dict = {}
    formatted_article: str = ""
    linkedin_posts: str = ""
    status: str = "idle"


class ResearchFlow(Flow[ResearchState]):
    """Flow for Phase 1: Continuous Research"""

    def __init__(self):
        super().__init__()
        self.db = TopicDatabase()

    @start()
    def start_research(self):
        """Start the research phase"""
        print("\n" + "="*60)
        print("PHASE 1: CONTINUOUS RESEARCH")
        print("="*60)
        print("Discovering trending AI/ML topics...\n")
        self.state.status = "running"

    @listen(start_research)
    def discover_and_curate(self):
        """Run the research crew to discover topics"""
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
        """Start the article creation phase"""
        topic = self.state.selected_topic
        print("\n" + "="*60)
        print("PHASE 2: ARTICLE CREATION")
        print("="*60)
        print(f"Topic: {topic.get('title', 'Unknown')}")
        print(f"Skill Level: {self.state.skill_level}")
        print("="*60 + "\n")
        self.state.status = "running"

        # Update topic status
        if topic and 'id' in topic:
            self.db.update_topic_status(topic['id'], 'in_progress')

    @listen(start_article_creation)
    def create_article(self):
        """Run the article crew to create the content"""
        try:
            inputs = {
                'topic_title': self.state.selected_topic.get('title', ''),
                'topic_summary': self.state.selected_topic.get('summary', ''),
                'skill_level': self.state.skill_level
            }

            result = ArticleCrew().crew().kickoff(inputs=inputs)

            # Read the generated files
            import os
            from pathlib import Path

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
            print(f"Article saved to: {article_path}")
            print(f"Project saved to: {project_path}")

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
        """Start the publishing preparation phase"""
        print("\n" + "="*60)
        print("PHASE 3: PUBLISHING PREPARATION")
        print("="*60)
        print("Preparing article for Medium...")
        print("Creating LinkedIn content...\n")
        self.state.status = "running"

    @listen(start_publish_prep)
    def prepare_for_publishing(self):
        """Run the publish crew"""
        try:
            inputs = {
                'article_content': self.state.article,
                'article_title': self.topic.get('title', ''),
                'article_summary': self.topic.get('summary', ''),
                'skill_level': self.skill_level,
                'category': self.topic.get('category', 'AI/ML')
            }

            result = PublishCrew().crew().kickoff(inputs=inputs)

            # Read the generated files
            from pathlib import Path
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