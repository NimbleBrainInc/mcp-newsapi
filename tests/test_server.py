"""Unit tests for the NewsAPI MCP server."""

from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import Client

from mcp_newsapi.api_models import Article, SearchNewsResponse, TopHeadlinesResponse
from mcp_newsapi.server import mcp


def _make_article(**kwargs: object) -> Article:
    """Create a test article with defaults."""
    defaults = {
        "title": "Test Article",
        "description": "A test article description",
        "url": "https://example.com/article",
        "source_name": "Test Source",
        "author": "Test Author",
        "published_at": "2025-01-15T12:00:00Z",
        "content": "Article content preview...",
    }
    defaults.update(kwargs)
    return Article(**defaults)  # type: ignore[arg-type]


@pytest.fixture
def mock_headlines_response() -> TopHeadlinesResponse:
    """Create a mock top headlines response."""
    return TopHeadlinesResponse(
        query=None,
        country="us",
        category=None,
        articles=[
            _make_article(
                title="Breaking News",
                url="https://example.com/breaking",
                source_name="CNN",
            ),
            _make_article(
                title="Tech Update",
                url="https://example.org/tech",
                source_name="TechCrunch",
                author=None,
            ),
        ],
        total_results=2,
    )


@pytest.fixture
def mock_search_response() -> SearchNewsResponse:
    """Create a mock search news response."""
    return SearchNewsResponse(
        query="artificial intelligence",
        articles=[
            _make_article(
                title="AI Breakthrough",
                url="https://example.com/ai",
                source_name="Wired",
            ),
            _make_article(
                title="Machine Learning Trends",
                url="https://example.org/ml",
                source_name="Ars Technica",
                content=None,
            ),
        ],
        total_results=2,
    )


@pytest.mark.asyncio
async def test_tools_list() -> None:
    """Test that tools are properly registered."""
    async with Client(mcp) as client:
        tools = await client.list_tools()

        assert len(tools) == 2
        tool_names = [tool.name for tool in tools]
        assert "get_top_headlines" in tool_names
        assert "search_news" in tool_names


@pytest.mark.asyncio
async def test_get_top_headlines_tool(mock_headlines_response: TopHeadlinesResponse) -> None:
    """Test get_top_headlines tool returns results."""
    with patch("mcp_newsapi.server.get_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.get_top_headlines.return_value = mock_headlines_response
        mock_get_client.return_value = mock_client

        async with Client(mcp) as client:
            result = await client.call_tool("get_top_headlines", {})

        mock_client.get_top_headlines.assert_called_once_with(
            query=None,
            country="us",
            category=None,
            page_size=10,
        )
        assert result is not None


@pytest.mark.asyncio
async def test_get_top_headlines_with_params(
    mock_headlines_response: TopHeadlinesResponse,
) -> None:
    """Test get_top_headlines tool with all parameters."""
    with patch("mcp_newsapi.server.get_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.get_top_headlines.return_value = mock_headlines_response
        mock_get_client.return_value = mock_client

        async with Client(mcp) as client:
            await client.call_tool(
                "get_top_headlines",
                {
                    "query": "technology",
                    "country": "gb",
                    "category": "technology",
                    "page_size": 5,
                },
            )

        mock_client.get_top_headlines.assert_called_once_with(
            query="technology",
            country="gb",
            category="technology",
            page_size=5,
        )


@pytest.mark.asyncio
async def test_search_news_tool(mock_search_response: SearchNewsResponse) -> None:
    """Test search_news tool returns results."""
    with patch("mcp_newsapi.server.get_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.search_news.return_value = mock_search_response
        mock_get_client.return_value = mock_client

        async with Client(mcp) as client:
            result = await client.call_tool("search_news", {"query": "artificial intelligence"})

        mock_client.search_news.assert_called_once_with(
            query="artificial intelligence",
            sources=None,
            domains=None,
            from_date=None,
            to_date=None,
            language="en",
            sort_by="publishedAt",
            page_size=10,
        )
        assert result is not None


@pytest.mark.asyncio
async def test_search_news_with_params(mock_search_response: SearchNewsResponse) -> None:
    """Test search_news tool with all parameters."""
    with patch("mcp_newsapi.server.get_client") as mock_get_client:
        mock_client = AsyncMock()
        mock_client.search_news.return_value = mock_search_response
        mock_get_client.return_value = mock_client

        async with Client(mcp) as client:
            await client.call_tool(
                "search_news",
                {
                    "query": "climate change",
                    "sources": "bbc-news,cnn",
                    "domains": "bbc.co.uk",
                    "from_date": "2025-01-01",
                    "to_date": "2025-01-31",
                    "language": "en",
                    "sort_by": "relevancy",
                    "page_size": 20,
                },
            )

        mock_client.search_news.assert_called_once_with(
            query="climate change",
            sources="bbc-news,cnn",
            domains="bbc.co.uk",
            from_date="2025-01-01",
            to_date="2025-01-31",
            language="en",
            sort_by="relevancy",
            page_size=20,
        )


def test_article_model() -> None:
    """Test Article model creation."""
    article = Article(
        title="Test",
        description="A description",
        url="https://example.com",
        source_name="Test Source",
        author="John Doe",
        published_at="2025-01-15T12:00:00Z",
        content="Content preview...",
    )
    assert article.title == "Test"
    assert article.url == "https://example.com"
    assert article.source_name == "Test Source"
    assert article.author == "John Doe"
    assert article.published_at == "2025-01-15T12:00:00Z"


def test_article_model_optional_fields() -> None:
    """Test Article model with optional fields as None."""
    article = Article(
        title="Test",
        url="https://example.com",
        source_name="Test Source",
        published_at="2025-01-15T12:00:00Z",
        description=None,
        author=None,
        content=None,
    )
    assert article.description is None
    assert article.author is None
    assert article.content is None


def test_top_headlines_response_model() -> None:
    """Test TopHeadlinesResponse model creation."""
    response = TopHeadlinesResponse(
        query=None,
        country="us",
        category=None,
        articles=[],
        total_results=0,
    )
    assert response.query is None
    assert response.country == "us"
    assert response.articles == []
    assert response.total_results == 0


def test_search_news_response_model() -> None:
    """Test SearchNewsResponse model creation."""
    response = SearchNewsResponse(
        query="test",
        articles=[],
        total_results=0,
    )
    assert response.query == "test"
    assert response.articles == []
    assert response.total_results == 0
