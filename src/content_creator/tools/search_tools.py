from typing import List, Dict, Any
import urllib.request
import urllib.parse
import json
from crewai.tools import tool


@tool("search_ai_news")
def search_ai_news(query: str) -> str:
    """
    Search for AI news, blog posts, and announcements using DuckDuckGo.

    Args:
        query: Search query string (e.g., "LangChain new features", "AI agent framework")

    Returns:
        JSON string containing search results with title, URL, and snippet
    """
    try:
        from duckduckgo_search import DDGS

        results = DDGS().text(
            keywords=f"{query} AI machine learning news",
            max_results=8
        )

        formatted = []
        for r in results:
            formatted.append({
                'title': r.get('title', ''),
                'url': r.get('href', ''),
                'snippet': r.get('body', ''),
                'source': 'Web Search'
            })

        return json.dumps(formatted, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to search: {str(e)}", "results": []})


@tool("search_github_trending")
def search_github_trending(query: str) -> str:
    """
    Search for popular recent GitHub repositories related to AI/ML tools and frameworks.

    Args:
        query: Search query string (e.g., "AI agent", "LLM framework", "RAG")

    Returns:
        JSON string containing repositories with name, description, stars, and URL
    """
    try:
        from datetime import datetime, timedelta

        since_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

        encoded_query = urllib.parse.quote(f"{query} AI ML")
        url = f"https://api.github.com/search/repositories?q={encoded_query}+language:python+created:>{since_date}&sort=stars&order=desc&per_page=10"
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'AI-Content-Creator/1.0'
        }

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))

        repos = []
        for item in data.get('items', [])[:10]:
            repos.append({
                'name': item.get('full_name', ''),
                'url': item.get('html_url', ''),
                'description': item.get('description', 'No description') or 'No description',
                'stars': item.get('stargazers_count', 0),
                'language': item.get('language', 'python'),
                'topics': item.get('topics', [])[:5]
            })

        return json.dumps(repos, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to get trending repos: {str(e)}"})


@tool("search_topic_info")
def search_topic_info(topic: str) -> str:
    """
    Search for tutorials, guides, and practical information about a specific AI/ML topic.

    Args:
        topic: Topic to search for (e.g., "LangChain RAG tutorial", "CrewAI agents")

    Returns:
        String containing search results with titles, snippets, and URLs
    """
    try:
        from duckduckgo_search import DDGS

        results = DDGS().text(
            keywords=f"{topic} tutorial guide how to use",
            max_results=8
        )

        formatted = []
        for r in results:
            title = r.get('title', '')
            snippet = r.get('body', '')
            url = r.get('href', '')
            if title and snippet:
                formatted.append(f"**{title}**\n{snippet}\nURL: {url}")

        return "\n\n---\n\n".join(formatted) if formatted else "No results found for this topic."
    except Exception as e:
        return f"Error searching for topic: {str(e)}"


@tool("search_trending_topics")
def get_trending_ai_topics() -> str:
    """
    Find currently trending AI/ML tools, frameworks, and practical topics from news and web sources.
    Takes no arguments.

    Returns:
        JSON string with trending topics including name, category, URL, and snippet
    """
    try:
        from duckduckgo_search import DDGS

        trending = []
        seen_titles = set()

        # Search for new AI tools and framework news
        news_results = DDGS().news(
            keywords="new AI tools frameworks release tutorial",
            max_results=15
        )
        for r in news_results:
            title = r.get('title', '')
            if title and title.lower() not in seen_titles:
                seen_titles.add(title.lower())
                trending.append({
                    'name': title,
                    'category': 'AI/ML',
                    'url': r.get('url', ''),
                    'snippet': r.get('body', '')[:200],
                    'source': r.get('source', 'News')
                })

        # Search for trending frameworks and tools
        text_results = DDGS().text(
            keywords="trending AI ML frameworks tools LangChain CrewAI new release 2026",
            max_results=10
        )
        for r in text_results:
            title = r.get('title', '')
            if title and title.lower() not in seen_titles:
                seen_titles.add(title.lower())
                trending.append({
                    'name': title,
                    'category': 'AI/ML',
                    'url': r.get('href', ''),
                    'snippet': r.get('body', '')[:200],
                    'source': 'Web'
                })

        if trending:
            return json.dumps(trending[:20], indent=2)

        # Minimal fallback only if all searches fail
        fallback = [
            {"name": "Building RAG Pipelines with LangChain", "category": "AI/ML", "url": "", "snippet": "Fallback: live search unavailable", "source": "static_fallback"},
            {"name": "Multi-Agent Systems with CrewAI", "category": "Agentic Systems", "url": "", "snippet": "Fallback: live search unavailable", "source": "static_fallback"},
            {"name": "Local LLMs with Ollama", "category": "AI/ML", "url": "", "snippet": "Fallback: live search unavailable", "source": "static_fallback"},
        ]
        return json.dumps(fallback, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to get trending topics: {str(e)}"})


@tool("search_ai_tools_and_frameworks")
def search_ai_tools_and_frameworks(query: str) -> str:
    """
    Search specifically for AI/ML framework tutorials, tool guides, and how-to articles.

    Args:
        query: Search query (e.g., "LangChain", "AI agent framework", "RAG tutorial")

    Returns:
        JSON string containing tutorials and guides with title, URL, and snippet
    """
    try:
        from duckduckgo_search import DDGS

        results = DDGS().text(
            keywords=f"{query} tutorial framework guide how to build",
            max_results=10
        )

        formatted = []
        for r in results:
            formatted.append({
                'title': r.get('title', ''),
                'url': r.get('href', ''),
                'snippet': r.get('body', ''),
                'source': 'Tutorial Search'
            })

        return json.dumps(formatted, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to search tools/frameworks: {str(e)}", "results": []})
