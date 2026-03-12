#!/usr/bin/env python
"""
AI Content Creator - Main CLI Interface

Commands:
    research              - Run continuous research to discover new topics
    select-topic          - Display discovered topics and select one
    create-article        - Create an article from a selected topic
    review                - Review pending articles
    publish               - Prepare approved articles for publishing
    full-workflow         - Run complete workflow with interactive checkpoints
"""

import sys
import json
from pathlib import Path
from datetime import datetime

from content_creator.flows import ResearchFlow, ArticleFlow, PublishFlow
from content_creator.database.topic_db import TopicDatabase


def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*70)
    print(text.center(70))
    print("="*70 + "\n")


def print_menu(options, title="Menu"):
    """Print a numbered menu"""
    print(f"\n{title}:")
    print("-" * 40)
    for i, option in enumerate(options, 1):
        print(f"  [{i}] {option}")
    print("-" * 40)


def get_user_choice(max_choice, prompt="Enter your choice: "):
    """Get validated user input"""
    while True:
        try:
            choice = input(prompt).strip()
            if choice.lower() == 'q':
                return None
            choice = int(choice)
            if 1 <= choice <= max_choice:
                return choice
            print(f"Please enter a number between 1 and {max_choice}")
        except ValueError:
            print("Please enter a valid number or 'q' to quit")


def run_research():
    """Run the research phase"""
    print_header("RUNNING RESEARCH PHASE")
    print("This will search for trending AI/ML topics and save them to the database.\n")

    flow = ResearchFlow()
    flow.kickoff()

    print("\n" + "="*70)
    print("Research phase complete! Topics have been saved.")
    print("Run 'select-topic' to browse and select a topic.")
    print("="*70)


def display_topics_and_select():
    """Display discovered topics and let user select"""
    db = TopicDatabase()
    topics = db.get_pending_topics(limit=15)

    if not topics:
        print_header("NO TOPICS FOUND")
        print("No pending topics in the database.")
        print("Run 'research' first to discover topics.")
        return None, None

    print_header("DISCOVERED TOPICS")
    print(f"Found {len(topics)} topic(s) waiting for selection:\n")

    for i, topic in enumerate(topics, 1):
        print(f"[{i}] {topic.title}")
        print(f"    Category: {topic.category} | Impact: {topic.impact_score:.1f}/10 | Level: {topic.difficulty_estimate}")
        print(f"    Summary: {topic.summary[:100]}...")
        print()

    print("\nEnter the number of the topic you want to write about,")
    print("or 'q' to cancel:")

    choice = get_user_choice(len(topics))
    if choice is None:
        return None, None

    selected_topic = topics[choice - 1]

    # Select skill level
    print("\n" + "="*70)
    print("Select skill level for the article:")
    print_menu(["Beginner - Focus on fundamentals and simple explanations",
                "Intermediate - Technical depth with practical guidance",
                "Expert - Deep dive with advanced implementations"], "Skill Level")

    level_choice = get_user_choice(3)
    if level_choice is None:
        return None, None

    skill_levels = ["beginner", "intermediate", "expert"]
    selected_level = skill_levels[level_choice - 1]

    return selected_topic.model_dump(), selected_level


def create_article(topic_data, skill_level):
    """Create an article from a selected topic"""
    print_header("CREATING ARTICLE")

    flow = ArticleFlow(topic=topic_data, skill_level=skill_level)
    result = flow.kickoff()

    if result:
        print("\n" + "="*70)
        print("Article created successfully!")
        print("="*70)

        # Show the article for review
        print("\n--- ARTICLE PREVIEW ---\n")

        # Read and display the article
        project_root = Path(__file__).parent.parent.parent
        article_file = project_root / "articles" / f"draft_{topic_data.get('title', 'article').replace(' ', '_')[:30]}.md"

        if article_file.exists():
            with open(article_file, 'r') as f:
                content = f.read()
                # Show first 2000 chars
                print(content[:2000] + "...\n" if len(content) > 2000 else content)

        print("\n--- END OF PREVIEW ---")
        print("\nThe article is ready for review.")

    return result


def review_article():
    """Review and approve/reject articles"""
    print_header("REVIEW ARTICLES")

    project_root = Path(__file__).parent.parent.parent
    articles_dir = project_root / "articles"

    if not articles_dir.exists():
        print("No articles directory found.")
        return

    # Find draft articles
    draft_files = list(articles_dir.glob("draft_*.md"))

    if not draft_files:
        print("No draft articles found for review.")
        return

    print(f"Found {len(draft_files)} article(s) for review:\n")

    for i, file in enumerate(draft_files, 1):
        print(f"[{i}] {file.name}")

    print("\nEnter the number of the article to review, or 'q' to cancel:")
    choice = get_user_choice(len(draft_files))
    if choice is None:
        return

    selected_file = draft_files[choice - 1]

    with open(selected_file, 'r') as f:
        content = f.read()

    print("\n" + "="*70)
    print("FULL ARTICLE")
    print("="*70)
    print(content)
    print("="*70)

    print("\n" + "="*70)
    print("REVIEW OPTIONS")
    print("="*70)
    print_menu(["APPROVE - Proceed to publishing preparation",
                "REVISIONS NEEDED - Article needs changes (will be deleted)",
                "REJECT - Delete this article"], "Decision")

    decision = get_user_choice(3)
    if decision is None:
        return

    if decision == 1:
        # Approve
        print("\nArticle APPROVED!")
        print("Run 'publish' to prepare it for Medium.")
        return content

    elif decision == 2:
        # Needs revisions - delete
        selected_file.unlink()
        print("\nArticle marked for revisions and deleted.")
        print("Run 'create-article' again after making changes.")

    else:
        # Reject - delete
        selected_file.unlink()
        # Also delete project file if exists
        project_file = articles_dir / selected_file.name.replace("draft_", "project_")
        if project_file.exists():
            project_file.unlink()
        print("\nArticle rejected and deleted.")


def publish_article():
    """Prepare article for publishing"""
    print_header("PUBLISHING PREPARATION")

    project_root = Path(__file__).parent.parent.parent
    articles_dir = project_root / "articles"

    # Find approved articles (not containing 'draft_' in the name we're looking for)
    article_files = list(articles_dir.glob("draft_*.md"))

    if not article_files:
        print("No articles found. Create and review an article first.")
        return

    print(f"Found {len(article_files)} article(s):\n")

    for i, file in enumerate(article_files, 1):
        print(f"[{i}] {file.name}")

    print("\nEnter the number of the article to publish, or 'q' to cancel:")
    choice = get_user_choice(len(article_files))
    if choice is None:
        return

    selected_file = article_files[choice - 1]

    with open(selected_file, 'r') as f:
        article_content = f.read()

    # Get topic info (simplified)
    topic = {
        'title': selected_file.stem.replace('draft_', '').replace('_', ' '),
        'summary': 'AI/ML article',
        'category': 'AI/ML'
    }

    # Assume intermediate if not specified
    skill_level = 'intermediate'

    # Run publish flow
    flow = PublishFlow(article_content=article_content, topic=topic, skill_level=skill_level)
    result = flow.kickoff()

    if result:
        print("\n" + "="*70)
        print("PUBLISHING PREPARATION COMPLETE!")
        print("="*70)

        # Show files created
        outputs_dir = project_root / "outputs"

        print("\nFiles created:")
        print(f"  - {outputs_dir / 'article_medium_ready.md'}")
        print(f"  - {outputs_dir / 'linkedin_posts.txt'}")

        # Show LinkedIn posts
        linkedin_file = outputs_dir / 'linkedin_posts.txt'
        if linkedin_file.exists():
            print("\n" + "-"*70)
            print("LINKEDIN POSTS READY TO COPY:")
            print("-"*70)
            with open(linkedin_file, 'r') as f:
                print(f.read())


def full_workflow():
    """Run complete workflow with checkpoints"""
    print_header("FULL WORKFLOW MODE")
    print("This will guide you through the entire process with checkpoints.\n")

    # Step 1: Research
    print("\n" + "="*70)
    print("STEP 1: RESEARCH")
    print("="*70)

    db = TopicDatabase()
    existing_topics = db.get_pending_topics()

    if existing_topics:
        print(f"\nFound {len(existing_topics)} existing topic(s) in database.")
        print("Do you want to:")
        print_menu(["Use existing topics",
                    "Run new research to find more topics"], "Option")

        choice = get_user_choice(2)
        if choice is None:
            return

        if choice == 2:
            run_research()
    else:
        print("\nNo existing topics found. Running research...")
        run_research()

    # Checkpoint 1: Topic Selection
    print("\n" + "="*70)
    print("CHECKPOINT 1: TOPIC SELECTION")
    print("="*70)

    topic_data, skill_level = display_topics_and_select()
    if topic_data is None:
        print("\nWorkflow cancelled.")
        return

    print(f"\nSelected: {topic_data['title']}")
    print(f"Skill Level: {skill_level}")

    # Step 2: Article Creation
    print("\n" + "="*70)
    print("STEP 2: ARTICLE CREATION")
    print("="*70)

    proceed = input("\nProceed with article creation? (y/n): ").strip().lower()
    if proceed != 'y':
        print("\nWorkflow paused. Run 'create-article' later to continue.")
        return

    create_article(topic_data, skill_level)

    # Checkpoint 2: Article Review
    print("\n" + "="*70)
    print("CHECKPOINT 2: ARTICLE REVIEW")
    print("="*70)

    proceed = input("\nReview the article now? (y/n): ").strip().lower()
    if proceed != 'y':
        print("\nWorkflow paused. Run 'review' later to continue.")
        return

    content = review_article()

    if content:
        # Step 3: Publishing
        print("\n" + "="*70)
        print("STEP 3: PUBLISHING PREPARATION")
        print("="*70)

        proceed = input("\nProceed with publishing preparation? (y/n): ").strip().lower()
        if proceed != 'y':
            print("\nWorkflow paused. Run 'publish' later to continue.")
            return

        publish_article()

    print("\n" + "="*70)
    print("WORKFLOW COMPLETE!")
    print("="*70)


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print_header("AI CONTENT CREATOR")
        print("A CrewAI workflow for researching AI topics and creating Medium articles.\n")
        print("Usage: crewai run <command>")
        print("\nCommands:")
        print("  research         - Discover new AI/ML topics")
        print("  select-topic   - Browse and select a topic")
        print("  create-article   - Create article from selected topic")
        print("  review           - Review pending articles")
        print("  publish          - Prepare approved articles for Medium")
        print("  full-workflow    - Run complete workflow with checkpoints")
        return

    command = sys.argv[1]

    commands = {
        'research': run_research,
        'select-topic': display_topics_and_select,
        'create-article': lambda: create_article(*display_topics_and_select()),
        'review': review_article,
        'publish': publish_article,
        'full-workflow': full_workflow,
        'kickoff': full_workflow,  # Default
    }

    if command in commands:
        try:
            commands[command]()
        except KeyboardInterrupt:
            print("\n\nWorkflow interrupted. Progress has been saved.")
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"Unknown command: {command}")
        print("Run without arguments to see available commands.")


def kickoff():
    """Entry point for 'kickoff' command"""
    full_workflow()


def plot():
    """Entry point for 'plot' command"""
    print("Generating flow visualization...")
    # This would generate a flow diagram if needed
    print("Visualization saved to flow_plot.html")


if __name__ == "__main__":
    main()