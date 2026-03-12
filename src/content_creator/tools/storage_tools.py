from typing import List, Optional
from crewai.tools import tool
from content_creator.database.topic_db import TopicDatabase, Topic
import json


# Initialize database instance
db = TopicDatabase()


@tool("save_topic")
def save_topic(
    topic_id: str,
    title: str,
    summary: str,
    category: str,
    impact_score: float,
    difficulty_estimate: str,
    sources: str,  # JSON string
    discovered_at: str
) -> str:
    """
    Save a discovered topic to the database.

    Args:
        topic_id: Unique identifier for the topic
        title: Topic title
        summary: Brief summary of the topic
        category: Category (AI, ML, DL, Agentic Systems, Emerging)
        impact_score: Impact score from 1-10
        difficulty_estimate: Estimated difficulty (beginner/intermediate/expert)
        sources: JSON string array of source URLs
        discovered_at: ISO timestamp

    Returns:
        Success or error message
    """
    try:
        topic = Topic(
            id=topic_id,
            title=title,
            summary=summary,
            category=category,
            impact_score=impact_score,
            difficulty_estimate=difficulty_estimate,
            sources=json.loads(sources),
            discovered_at=discovered_at,
            status="pending_selection"
        )

        if db.save_topic(topic):
            return f"Successfully saved topic: {title}"
        else:
            return f"Failed to save topic: {title}"
    except Exception as e:
        return f"Error saving topic: {str(e)}"


@tool("get_pending_topics")
def get_pending_topics(limit: int = 15) -> str:
    """
    Get topics waiting for user selection.

    Args:
        limit: Maximum number of topics to return

    Returns:
        JSON string containing list of pending topics
    """
    try:
        topics = db.get_pending_topics(limit)
        return json.dumps([t.model_dump() for t in topics], indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool("get_topic_by_id")
def get_topic_by_id(topic_id: str) -> str:
    """
    Get a specific topic by its ID.

    Args:
        topic_id: The topic ID

    Returns:
        JSON string containing topic details or error
    """
    try:
        topic = db.get_topic_by_id(topic_id)
        if topic:
            return json.dumps(topic.model_dump(), indent=2)
        else:
            return json.dumps({"error": f"Topic {topic_id} not found"})
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool("update_topic_status")
def update_topic_status(topic_id: str, status: str) -> str:
    """
    Update the status of a topic.

    Args:
        topic_id: The topic ID
        status: New status (pending_selection, selected, in_progress, completed)

    Returns:
        Success or error message
    """
    try:
        if db.update_topic_status(topic_id, status):
            return f"Updated topic {topic_id} status to {status}"
        else:
            return f"Failed to update topic {topic_id}"
    except Exception as e:
        return f"Error updating topic: {str(e)}"


@tool("get_all_topics")
def get_all_topics() -> str:
    """
    Get all topics from the database.

    Returns:
        JSON string containing all topics
    """
    try:
        topics = db.get_all_topics()
        return json.dumps([t.model_dump() for t in topics], indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})