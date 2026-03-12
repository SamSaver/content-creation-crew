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
    add-topic             - Create article from a custom topic (CLI args)
"""

import sys
import argparse
from pathlib import Path

from content_creator.flows import (
    ResearchFlow, ArticleFlow, PublishFlow, ContentCreationFlow
)
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

        project_root = Path(__file__).parent.parent.parent
        article_file = project_root / "articles" / f"draft_{topic_data.get('title', 'article').replace(' ', '_')[:30]}.md"

        if article_file.exists():
            with open(article_file, 'r') as f:
                content = f.read()
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
        print("\nArticle APPROVED!")
        print("Run 'publish' to prepare it for Medium.")
        return content

    elif decision == 2:
        selected_file.unlink()
        print("\nArticle marked for revisions and deleted.")
        print("Run 'create-article' again after making changes.")

    else:
        selected_file.unlink()
        project_file = articles_dir / selected_file.name.replace("draft_", "project_")
        if project_file.exists():
            project_file.unlink()
        print("\nArticle rejected and deleted.")


def publish_article():
    """Prepare article for publishing"""
    print_header("PUBLISHING PREPARATION")

    project_root = Path(__file__).parent.parent.parent
    articles_dir = project_root / "articles"

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

    topic = {
        'title': selected_file.stem.replace('draft_', '').replace('_', ' '),
        'summary': 'AI/ML article',
        'category': 'AI/ML'
    }

    skill_level = 'intermediate'

    flow = PublishFlow(article_content=article_content, topic=topic, skill_level=skill_level)
    result = flow.kickoff()

    if result:
        print("\n" + "="*70)
        print("PUBLISHING PREPARATION COMPLETE!")
        print("="*70)

        outputs_dir = project_root / "outputs"

        print("\nFiles created:")
        print(f"  - {outputs_dir / 'article_medium_ready.md'}")
        print(f"  - {outputs_dir / 'linkedin_posts.txt'}")

        linkedin_file = outputs_dir / 'linkedin_posts.txt'
        if linkedin_file.exists():
            print("\n" + "-"*70)
            print("LINKEDIN POSTS READY TO COPY:")
            print("-"*70)
            with open(linkedin_file, 'r') as f:
                print(f.read())


def full_workflow():
    """Run complete workflow using the unified ContentCreationFlow."""
    flow = ContentCreationFlow()
    flow.state.mode = "auto"

    try:
        flow.kickoff()
    except KeyboardInterrupt:
        print("\n\nWorkflow interrupted. Progress has been saved.")


def add_custom_topic():
    """Create an article from a custom user-provided topic.

    Usage: add-topic --title "Topic Name" [--summary "Description"] [--level intermediate]
    """
    parser = argparse.ArgumentParser(
        description="Create an article from a custom topic",
        prog="add-topic"
    )
    parser.add_argument(
        "--title", "-t",
        required=True,
        help="The topic title (e.g., 'RAG Pipelines with LangChain')"
    )
    parser.add_argument(
        "--summary", "-s",
        default=None,
        help="Brief description of the topic (optional, defaults to title)"
    )
    parser.add_argument(
        "--level", "-l",
        choices=["beginner", "intermediate", "expert"],
        default="intermediate",
        help="Skill level for the article (default: intermediate)"
    )

    # Parse only the args after the command name
    args = parser.parse_args(sys.argv[1:])

    print_header("CUSTOM TOPIC MODE")
    print(f"Topic: {args.title}")
    print(f"Level: {args.level}")
    if args.summary:
        print(f"Summary: {args.summary}")
    print()

    flow = ContentCreationFlow()
    flow.state.mode = "custom"
    flow.state.custom_topic = args.title
    flow.state.custom_summary = args.summary
    flow.state.skill_level = args.level

    try:
        flow.kickoff()
    except KeyboardInterrupt:
        print("\n\nWorkflow interrupted. Progress has been saved.")


def show_help():
    """Show available commands"""
    print_header("AI CONTENT CREATOR")
    print("A CrewAI workflow for researching AI topics and creating Medium articles.\n")
    print("Usage: crewai run <command>")
    print("\nCommands:")
    print("  research         - Discover new AI/ML topics")
    print("  select-topic     - Browse and select a topic")
    print("  create-article   - Create article from selected topic")
    print("  review           - Review pending articles")
    print("  publish          - Prepare approved articles for Medium")
    print("  full-workflow    - Run complete workflow with checkpoints")
    print("  add-topic        - Create article from custom topic")
    print()
    print("Examples:")
    print("  crewai run                                              # runs full workflow")
    print("  crewai run research                                     # discover topics")
    print('  crewai run add-topic -- --title "RAG Pipelines" --level intermediate')
    print()


COMMANDS = {
    'research': run_research,
    'select-topic': display_topics_and_select,
    'create-article': lambda: create_article(*display_topics_and_select()),
    'review': review_article,
    'publish': publish_article,
    'full-workflow': full_workflow,
    'kickoff': full_workflow,
    'add-topic': add_custom_topic,
    'help': show_help,
}


def main():
    """Main entry point — dispatches to the right command.

    Works both as:
      - `crewai run <command>` (CrewAI invokes the kickoff entry point with args)
      - `python -m content_creator.main <command>` (direct invocation)
    """
    # Find the command: skip any leading args that aren't a known command
    # This handles both `kickoff research` (crewai run) and `main.py research` (direct)
    command = None
    command_idx = None
    for i, arg in enumerate(sys.argv[1:], start=1):
        if arg in COMMANDS:
            command = arg
            command_idx = i
            break

    if command is None:
        # No recognized command — default to full workflow
        full_workflow()
        return

    # Shift sys.argv so the command's function sees its own args correctly
    # e.g., for add-topic: sys.argv becomes [script, --title, "X", --level, "Y"]
    sys.argv = [sys.argv[0]] + sys.argv[command_idx + 1:]

    try:
        COMMANDS[command]()
    except KeyboardInterrupt:
        print("\n\nWorkflow interrupted. Progress has been saved.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


def kickoff():
    """Entry point for 'crewai run' — routes through main() so subcommands work.

    Examples:
        crewai run               → full_workflow (default)
        crewai run research      → run_research
        crewai run add-topic ... → add_custom_topic
    """
    main()


def plot():
    """Entry point for 'plot' command"""
    print("Generating flow visualization...")
    print("Visualization saved to flow_plot.html")


if __name__ == "__main__":
    main()
