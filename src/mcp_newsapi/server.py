"""NewsAPI MCP Server - FastMCP Implementation."""

import logging
import os
import sys
from typing import Literal

from dotenv import load_dotenv
from fastmcp import Context, FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from .api_client import APIError, NewsAPIClient
from .api_models import SearchNewsResponse, TopHeadlinesResponse

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("mcp_newsapi")

load_dotenv()

mcp = FastMCP("NewsAPI")

_client: NewsAPIClient | None = None


def get_client() -> NewsAPIClient:
    """Get or create the NewsAPI client."""
    global _client
    if _client is None:
        api_key = os.environ.get("NEWS_API_KEY")
        if not api_key:
            raise ValueError(
                "NEWS_API_KEY is required. Get your API key from https://newsapi.org/register"
            )
        _client = NewsAPIClient(api_key=api_key)
    return _client


@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint for monitoring."""
    return JSONResponse({"status": "healthy", "service": "mcp-newsapi"})


@mcp.tool()
async def get_top_headlines(
    query: str | None = None,
    country: str = "us",
    category: Literal[
        "business", "entertainment", "general", "health", "science", "sports", "technology"
    ]
    | None = None,
    page_size: int = 10,
    ctx: Context | None = None,
) -> TopHeadlinesResponse:
    """Get top news headlines by country and category.

    Args:
        query: Keywords to search in article headlines.
        country: 2-letter ISO 3166-1 country code (default: "us").
        category: News category: "business", "entertainment", "general", "health", "science", "sports", or "technology".
        page_size: Number of results to return (default: 10, max: 100).
        ctx: MCP context.

    Returns:
        Top headlines with article titles, descriptions, URLs, and source info.
    """
    client = get_client()

    if ctx:
        label = f"country={country}"
        if query:
            label += f", query={query[:50]}"
        if category:
            label += f", category={category}"
        await ctx.info(f"Fetching top headlines: {label}")

    try:
        return await client.get_top_headlines(
            query=query,
            country=country,
            category=category,
            page_size=page_size,
        )
    except APIError as e:
        if ctx:
            await ctx.error(f"NewsAPI error: {e.message}")
        raise


@mcp.tool()
async def search_news(
    query: str,
    sources: str | None = None,
    domains: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    language: str = "en",
    sort_by: Literal["relevancy", "popularity", "publishedAt"] = "publishedAt",
    page_size: int = 10,
    ctx: Context | None = None,
) -> SearchNewsResponse:
    """Search news articles from the past 30 days.

    Note: The free tier of NewsAPI only returns articles from the last 30 days.

    Args:
        query: Search keywords or phrase (required).
        sources: Comma-separated source IDs (e.g. "bbc-news,cnn").
        domains: Comma-separated domains to restrict search (e.g. "bbc.co.uk,techcrunch.com").
        from_date: Oldest article date in ISO 8601 format (e.g. "2025-01-01").
        to_date: Newest article date in ISO 8601 format (e.g. "2025-01-31").
        language: 2-letter ISO 639-1 language code (default: "en").
        sort_by: Sort order: "relevancy", "popularity", or "publishedAt" (default: "publishedAt").
        page_size: Number of results to return (default: 10, max: 100).
        ctx: MCP context.

    Returns:
        News articles with titles, descriptions, URLs, source info, and content previews.
    """
    client = get_client()

    if ctx:
        await ctx.info(f"Searching news for: {query[:80]}...")

    try:
        return await client.search_news(
            query=query,
            sources=sources,
            domains=domains,
            from_date=from_date,
            to_date=to_date,
            language=language,
            sort_by=sort_by,
            page_size=page_size,
        )
    except APIError as e:
        if ctx:
            await ctx.error(f"NewsAPI error: {e.message}")
        raise


# ASGI entrypoint (nimbletools-core container deployment)
app = mcp.http_app()

# Stdio entrypoint (mpak / Claude Desktop)
if __name__ == "__main__":
    logger.info("Running in stdio mode")
    mcp.run()
