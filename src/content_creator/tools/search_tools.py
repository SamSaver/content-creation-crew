from typing import List, Dict, Any
import urllib.request
import urllib.parse
import json
from crewai.tools import tool


@tool("Search arXiv for papers")
def search_arxiv(query: str, max_results: int = 5) -> str:
    """
    Search arXiv for papers related to AI/ML topics.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default 5)

    Returns:
        JSON string containing paper titles, abstracts, authors, and URLs
    """
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"

        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read().decode('utf-8')

        import xml.etree.ElementTree as ET
        root = ET.fromstring(data)

        ns = {'atom': 'http://www.w3.org/2005/Atom'}

        papers = []
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns)
            summary = entry.find('atom:summary', ns)
            link = entry.find('atom:link[@rel="alternate"]', ns)
            published = entry.find('atom:published', ns)

            if title is not None and summary is not None:
                papers.append({
                    'title': title.text.strip().replace('\n', ' '),
                    'summary': summary.text.strip()[:500] + '...' if len(summary.text) > 500 else summary.text.strip(),
                    'url': link.get('href') if link is not None else '',
                    'published': published.text[:10] if published is not None else ''
                })

        return json.dumps(papers, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to search arXiv: {str(e)}"})


@tool("Search AI news and blogs")
def search_ai_news(query: str) -> str:
    """
    Search for AI news and blog posts using DuckDuckGo.

    Args:
        query: Search query string

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


@tool("Get GitHub trending repositories")
def search_github_trending(language: str = "python", period: str = "daily") -> str:
    """
    Get trending GitHub repositories related to AI/ML using the GitHub Search API.

    Args:
        language: Programming language filter (default: python)
        period: Time period - daily, weekly, or monthly (default: daily)

    Returns:
        JSON string containing trending repositories with name, description, stars, and URL
    """
    try:
        from datetime import datetime, timedelta

        days_map = {"daily": 1, "weekly": 7, "monthly": 30}
        days = days_map.get(period, 7)
        since_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

        url = f"https://api.github.com/search/repositories?q=language:{language}+topic:machine-learning+created:>{since_date}&sort=stars&order=desc&per_page=10"
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
                'language': item.get('language', language),
                'topics': item.get('topics', [])[:5]
            })

        return json.dumps(repos, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to get trending repos: {str(e)}"})


@tool("Search for specific topic information")
def search_topic_info(topic: str) -> str:
    """
    Search for detailed information about a specific AI/ML topic.

    Args:
        topic: Topic to search for

    Returns:
        String containing search results with titles, snippets, and URLs
    """
    try:
        from duckduckgo_search import DDGS

        results = DDGS().text(
            keywords=f"{topic} tutorial explanation machine learning",
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


@tool("Get current trending AI topics")
def get_trending_ai_topics() -> str:
    """
    Get a list of currently trending AI/ML topics by searching real-time news and web sources.

    Returns:
        JSON string with trending topics, their categories, and source URLs
    """
    try:
        from duckduckgo_search import DDGS

        trending = []
        seen_titles = set()

        # Search recent AI/ML news
        news_results = DDGS().news(
            keywords="artificial intelligence machine learning breakthrough",
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

        # Also search for trending topics
        text_results = DDGS().text(
            keywords="trending AI ML topics tools 2025 2026",
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
            {"name": "Large Language Models (LLMs)", "category": "AI/ML", "url": "", "snippet": "Fallback: live search unavailable", "source": "static_fallback"},
            {"name": "Retrieval-Augmented Generation (RAG)", "category": "AI/ML", "url": "", "snippet": "Fallback: live search unavailable", "source": "static_fallback"},
            {"name": "Agentic AI Systems", "category": "Agentic Systems", "url": "", "snippet": "Fallback: live search unavailable", "source": "static_fallback"},
        ]
        return json.dumps(fallback, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Failed to get trending topics: {str(e)}"})
