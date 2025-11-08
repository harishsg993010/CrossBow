"""
Web Search Tools using DuckDuckGo
Real implementation for web searching capabilities
"""

from typing import Optional, List
from duckduckgo_search import DDGS


def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web using DuckDuckGo.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return
    
    Returns:
        str: Search results formatted as text
    """
    try:
        ddgs = DDGS()
        results = ddgs.text(query, max_results=max_results)
        
        if not results:
            return f"No results found for: {query}"
        
        output = f"Search Results for: {query}\n\n"
        for i, result in enumerate(results, 1):
            output += f"{i}. {result.get('title', 'No title')}\n"
            output += f"   URL: {result.get('href', 'No URL')}\n"
            output += f"   {result.get('body', 'No description')}\n\n"
        
        return output
    except Exception as e:
        return f"Error performing web search: {str(e)}"


def web_news_search(query: str, max_results: int = 5) -> str:
    """
    Search for news articles using DuckDuckGo.
    
    Args:
        query: News search query
        max_results: Maximum number of results to return
    
    Returns:
        str: News results formatted as text
    """
    try:
        ddgs = DDGS()
        results = ddgs.news(query, max_results=max_results)
        
        if not results:
            return f"No news found for: {query}"
        
        output = f"News Results for: {query}\n\n"
        for i, result in enumerate(results, 1):
            output += f"{i}. {result.get('title', 'No title')}\n"
            output += f"   Source: {result.get('source', 'Unknown')}\n"
            output += f"   Date: {result.get('date', 'Unknown date')}\n"
            output += f"   URL: {result.get('url', 'No URL')}\n"
            output += f"   {result.get('body', 'No description')}\n\n"
        
        return output
    except Exception as e:
        return f"Error performing news search: {str(e)}"


def get_web_search_tools():
    """Get web search tools as a list."""
    return [web_search, web_news_search]
