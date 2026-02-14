"""Pydantic models for NewsAPI MCP Server responses."""

from pydantic import BaseModel, Field


class Article(BaseModel):
    """A single news article."""

    title: str = Field(..., description="Article headline")
    description: str | None = Field(None, description="Short description or snippet")
    url: str = Field(..., description="URL to the full article")
    source_name: str = Field(..., description="Name of the news source")
    author: str | None = Field(None, description="Author of the article")
    published_at: str = Field(..., description="ISO 8601 publication date")
    content: str | None = Field(None, description="Truncated article content preview")


class TopHeadlinesResponse(BaseModel):
    """Response model for get_top_headlines tool."""

    query: str | None = Field(None, description="The search query (if provided)")
    country: str = Field(..., description="Country code used for the request")
    category: str | None = Field(None, description="Category filter (if provided)")
    articles: list[Article] = Field(default_factory=list, description="Top headline articles")
    total_results: int = Field(0, description="Total number of results available")


class SearchNewsResponse(BaseModel):
    """Response model for search_news tool."""

    query: str = Field(..., description="The search query")
    articles: list[Article] = Field(default_factory=list, description="Matching news articles")
    total_results: int = Field(0, description="Total number of results available")
