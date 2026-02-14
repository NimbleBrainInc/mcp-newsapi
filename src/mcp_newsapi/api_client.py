"""NewsAPI client."""

import os
from typing import Any

import aiohttp
from aiohttp import ClientError

from .api_models import Article, SearchNewsResponse, TopHeadlinesResponse


class APIError(Exception):
    """NewsAPI error."""

    def __init__(self, status: int, message: str, details: dict[str, Any] | None = None) -> None:
        self.status = status
        self.message = message
        self.details = details
        super().__init__(f"NewsAPI Error {status}: {message}")


class NewsAPIClient:
    """Async client for the NewsAPI."""

    BASE_URL = "https://newsapi.org/v2"

    def __init__(self, api_key: str | None = None, timeout: float = 30.0) -> None:
        self.api_key = api_key or os.environ.get("NEWS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "NEWS_API_KEY is required. Get your API key from https://newsapi.org/register"
            )
        self.timeout = timeout
        self._session: aiohttp.ClientSession | None = None

    async def _ensure_session(self) -> None:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers={
                    "Accept": "application/json",
                },
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            )

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    def _parse_articles(self, raw_articles: list[dict[str, Any]]) -> list[Article]:
        """Parse raw article data into Article models."""
        return [
            Article(
                title=a.get("title", ""),
                description=a.get("description"),
                url=a.get("url", ""),
                source_name=a.get("source", {}).get("name", ""),
                author=a.get("author"),
                published_at=a.get("publishedAt", ""),
                content=a.get("content"),
            )
            for a in raw_articles
        ]

    async def _handle_response(self, response: aiohttp.ClientResponse) -> dict[str, Any]:
        """Handle API response and raise errors for non-success status codes."""
        data: dict[str, Any] = await response.json()

        if response.status == 401:
            raise APIError(401, "Invalid API key. Check your NEWS_API_KEY.")
        if response.status == 429:
            raise APIError(429, "Rate limit exceeded. Please wait before retrying.")
        if response.status >= 400:
            msg = data.get("message", f"HTTP {response.status}")
            raise APIError(response.status, msg, data)

        return data

    async def get_top_headlines(
        self,
        query: str | None = None,
        country: str = "us",
        category: str | None = None,
        page_size: int = 10,
    ) -> TopHeadlinesResponse:
        """Get top headlines.

        Args:
            query: Keywords to search in headlines.
            country: 2-letter country code (default: "us").
            category: Category filter (business, entertainment, general, health, science, sports, technology).
            page_size: Number of results (max 100).

        Returns:
            TopHeadlinesResponse with articles.
        """
        await self._ensure_session()
        assert self._session is not None

        params: dict[str, str] = {
            "apiKey": self.api_key or "",
            "country": country,
            "pageSize": str(min(page_size, 100)),
        }
        if query:
            params["q"] = query
        if category:
            params["category"] = category

        try:
            async with self._session.get(
                f"{self.BASE_URL}/top-headlines", params=params
            ) as response:
                data = await self._handle_response(response)

                raw_articles = data.get("articles", [])
                articles = self._parse_articles(raw_articles)

                return TopHeadlinesResponse(
                    query=query,
                    country=country,
                    category=category,
                    articles=articles,
                    total_results=data.get("totalResults", len(articles)),
                )
        except ClientError as e:
            raise APIError(500, f"Network error: {e}") from e

    async def search_news(
        self,
        query: str,
        sources: str | None = None,
        domains: str | None = None,
        from_date: str | None = None,
        to_date: str | None = None,
        language: str = "en",
        sort_by: str = "publishedAt",
        page_size: int = 10,
    ) -> SearchNewsResponse:
        """Search all news articles.

        Note: Only returns articles from the last 30 days.

        Args:
            query: Search keywords.
            sources: Comma-separated source IDs.
            domains: Comma-separated domains to restrict search.
            from_date: ISO 8601 start date (e.g. "2025-01-01").
            to_date: ISO 8601 end date (e.g. "2025-01-31").
            language: 2-letter language code (default: "en").
            sort_by: Sort order: "relevancy", "popularity", or "publishedAt" (default).
            page_size: Number of results (max 100).

        Returns:
            SearchNewsResponse with articles.
        """
        await self._ensure_session()
        assert self._session is not None

        params: dict[str, str] = {
            "apiKey": self.api_key or "",
            "q": query,
            "language": language,
            "sortBy": sort_by,
            "pageSize": str(min(page_size, 100)),
        }
        if sources:
            params["sources"] = sources
        if domains:
            params["domains"] = domains
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        try:
            async with self._session.get(f"{self.BASE_URL}/everything", params=params) as response:
                data = await self._handle_response(response)

                raw_articles = data.get("articles", [])
                articles = self._parse_articles(raw_articles)

                return SearchNewsResponse(
                    query=query,
                    articles=articles,
                    total_results=data.get("totalResults", len(articles)),
                )
        except ClientError as e:
            raise APIError(500, f"Network error: {e}") from e

    async def test_connection(self) -> dict[str, Any]:
        """Test the API connection with a simple headlines request.

        Returns:
            Dict with success status and optional error.
        """
        try:
            result = await self.get_top_headlines(page_size=1)
            return {"success": True, "results": result.total_results}
        except APIError as e:
            return {"success": False, "error": e.message}
