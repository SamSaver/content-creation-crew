from typing import List, Dict, Any
import urllib.request
import urllib.parse
import json
from crewai.tools import tool


@tool("Search arXiv for papers")
def search_arxiv(query: str, max_results: int = 10) -> str:
    """
    Search arXiv for papers related to AI/ML topics.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default 10)

    Returns:
        JSON string containing paper titles, abstracts, authors, and URLs
    """
    try:
        # Encode query for URL
        encoded_query = urllib.parse.quote(query)
        url = f"http://export.arxiv.org/api/query?search_query=all:{encoded_query}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"

        with urllib.request.urlopen(url, timeout=30) as response:
            data = response.read().decode('utf-8')

        # Simple XML parsing to extract entries
        import xml.etree.ElementTree as ET
        root = ET.fromstring(data)

        # Namespace handling
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
    Search for AI news and blog posts using web search.

    Args:
        query: Search query string

    Returns:
        JSON string containing search results
    """
    try:
        # Use DuckDuckGo search
        encoded_query = urllib.parse.quote(f"{query} AI machine learning news")
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8')

        # Simple parsing of results
        results = []
        # Look for result links and titles
        import re
        result_blocks = re.findall(r'<a rel="nofollow" class="result__a"[^>]*>(.*?)</a>', html)

        for i, block in enumerate(result_blocks[:5]):
            # Clean HTML tags
            clean_text = re.sub(r'<[^>]+>', '', block)
            if clean_text:
                results.append({
                    'title': clean_text,
                    'source': 'Web Search'
                })

        return json.dumps(results, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to search: {str(e)}", "results": []})


@tool("Get GitHub trending repositories")
def search_github_trending(language: str = "python", period: str = "daily") -> str:
    """
    Get trending GitHub repositories related to AI/ML.

    Args:
        language: Programming language filter (default: python)
        period: Time period - daily, weekly, or monthly (default: daily)

    Returns:
        JSON string containing trending repositories
    """
    try:
        url = f"https://github.com/trending/{language}?since={period}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8')

        import re
        repos = []

        # Parse trending repos
        repo_matches = re.findall(r'<h2[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>\s*([^<]+)', html)

        for match in repo_matches[:10]:
            repo_path = match[0].strip()
            repo_name = match[1].strip().replace('\n', '').replace(' ', '')
            if repo_path and repo_name:
                repos.append({
                    'name': repo_name,
                    'url': f"https://github.com{repo_path}",
                    'description': f"Trending {language} repository"
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
        String containing search results with explanations and resources
    """
    try:
        # Search for tutorials and explanations
        encoded_query = urllib.parse.quote(f"{topic} tutorial explanation machine learning")
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8')

        import re
        results = []

        # Extract titles and snippets
        title_matches = re.findall(r'<a rel="nofollow" class="result__a"[^>]*>(.*?)</a>', html)
        snippet_matches = re.findall(r'<a class="result__snippet"[^>]*>(.*?)</a>', html)

        for i in range(min(len(title_matches), len(snippet_matches), 5)):
            title = re.sub(r'<[^>]+>', '', title_matches[i])
            snippet = re.sub(r'<[^>]+>', '', snippet_matches[i])
            if title and snippet:
                results.append(f"{title}: {snippet}")

        return "\n\n".join(results) if results else "No results found"
    except Exception as e:
        return f"Error searching for topic: {str(e)}"


@tool("Get current trending AI topics")
def get_trending_ai_topics() -> str:
    """
    Get a list of currently trending AI/ML topics.

    Returns:
        JSON string with trending topics and their categories
    """
    # Curated list of high-impact AI topics that are currently relevant
    trending = [
        {"name": "Large Language Models (LLMs)", "category": "AI/ML"},
        {"name": "Retrieval-Augmented Generation (RAG)", "category": "AI/ML"},
        {"name": "Multimodal AI", "category": "AI/ML"},
        {"name": "Agentic AI Systems", "category": "Agentic Systems"},
        {"name": "Mixture of Experts (MoE)", "category": "Deep Learning"},
        {"name": "Test-Time Compute Scaling", "category": "AI/ML"},
        {"name": "Neural Architecture Search", "category": "Deep Learning"},
        {"name": "Vision Transformers", "category": "Deep Learning"},
        {"name": "Diffusion Models", "category": "Deep Learning"},
        {"name": "Reinforcement Learning from Human Feedback", "category": "RL"},
        {"name": "Quantization and Model Compression", "category": "ML Engineering"},
        {"name": "Federated Learning", "category": "ML"},
        {"name": "Graph Neural Networks", "category": "Deep Learning"},
        {"name": "Neural Radiance Fields (NeRF)", "category": "Computer Vision"},
        {"name": "Constitutional AI", "category": "AI Safety"}
    ]

    return json.dumps(trending, indent=2)