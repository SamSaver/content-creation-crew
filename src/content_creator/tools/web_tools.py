import urllib.request
import re
from crewai.tools import tool


@tool("read_webpage")
def read_web_content(url: str) -> str:
    """
    Fetch and extract readable text content from a web page URL.
    Strips scripts, styles, and navigation to return the main article text.

    Args:
        url: The full URL of the web page to read

    Returns:
        Extracted text content from the page (truncated to 4000 characters)
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=20) as response:
            html = response.read().decode('utf-8', errors='ignore')

        # Extract page title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else 'Unknown'

        # Remove script and style blocks
        html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<nav[^>]*>.*?</nav>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<footer[^>]*>.*?</footer>', '', html, flags=re.DOTALL | re.IGNORECASE)
        html = re.sub(r'<header[^>]*>.*?</header>', '', html, flags=re.DOTALL | re.IGNORECASE)

        # Try to extract from article or main tags first
        content = ''
        for tag in ['article', 'main', 'div[role="main"]']:
            tag_name = tag.split('[')[0]
            match = re.search(
                rf'<{tag_name}[^>]*>(.*?)</{tag_name}>',
                html, re.DOTALL | re.IGNORECASE
            )
            if match and len(match.group(1)) > 200:
                content = match.group(1)
                break

        # Fall back to body
        if not content:
            body_match = re.search(r'<body[^>]*>(.*?)</body>', html, re.DOTALL | re.IGNORECASE)
            content = body_match.group(1) if body_match else html

        # Strip all remaining HTML tags
        text = re.sub(r'<[^>]+>', ' ', content)

        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()

        # Truncate to 4000 characters
        if len(text) > 4000:
            text = text[:4000] + '... [truncated]'

        return f"Title: {title}\n\n{text}"

    except urllib.error.HTTPError as e:
        return f"Error: HTTP {e.code} when fetching {url}"
    except urllib.error.URLError as e:
        return f"Error: Could not reach {url} - {str(e.reason)}"
    except Exception as e:
        return f"Error reading web content: {str(e)}"
