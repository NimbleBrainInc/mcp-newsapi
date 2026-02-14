# NewsAPI MCP Server

[![mpak](https://img.shields.io/badge/mpak-registry-blue)](https://mpak.dev/packages/@nimblebraininc/newsapi?utm_source=github&utm_medium=readme&utm_campaign=mcp-newsapi)
[![NimbleBrain](https://img.shields.io/badge/NimbleBrain-nimblebrain.ai-purple)](https://nimblebrain.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp-newsapi)
[![Discord](https://img.shields.io/badge/Discord-community-5865F2)](https://nimblebrain.ai/discord?utm_source=github&utm_medium=readme&utm_campaign=mcp-newsapi)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A [Model Context Protocol](https://modelcontextprotocol.io) (MCP) server that provides news search and headline retrieval using [NewsAPI](https://newsapi.org/). Get top headlines by country and category, or search articles across thousands of sources.

**[View on mpak registry](https://mpak.dev/packages/@nimblebraininc/newsapi?utm_source=github&utm_medium=readme&utm_campaign=mcp-newsapi)** | **Built by [NimbleBrain](https://nimblebrain.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp-newsapi)**

## Install

Install with [mpak](https://mpak.dev?utm_source=github&utm_medium=readme&utm_campaign=mcp-newsapi):

```bash
mpak install @nimblebraininc/newsapi
```

### Configuration

Get your API key from [NewsAPI](https://newsapi.org/register), then configure:

```bash
mpak config set @nimblebraininc/newsapi api_key YOUR_API_KEY
```

### Claude Code

```bash
claude mcp add newsapi -- mpak run @nimblebraininc/newsapi
```

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "newsapi": {
      "command": "mpak",
      "args": ["run", "@nimblebraininc/newsapi"]
    }
  }
}
```

See the [mpak registry page](https://mpak.dev/packages/@nimblebraininc/newsapi?utm_source=github&utm_medium=readme&utm_campaign=mcp-newsapi) for full install options.

## Tools

### get_top_headlines

Get top news headlines by country and category.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | `string` | No | Keywords to search in article headlines |
| `country` | `string` | No | 2-letter country code (default: `"us"`) |
| `category` | `string` | No | One of: `"business"`, `"entertainment"`, `"general"`, `"health"`, `"science"`, `"sports"`, `"technology"` |
| `page_size` | `integer` | No | Number of results, max 100 (default: `10`) |

**Example call:**

```json
{
  "name": "get_top_headlines",
  "arguments": {
    "country": "us",
    "category": "technology",
    "page_size": 5
  }
}
```

**Example response:**

```json
{
  "articles": [
    {
      "title": "New AI breakthrough announced",
      "description": "Researchers have developed a new approach...",
      "url": "https://example.com/article",
      "source": "TechCrunch",
      "author": "Jane Smith",
      "published_at": "2026-02-13T10:00:00Z"
    }
  ],
  "total_results": 5
}
```

### search_news

Search news articles across all sources. **Note:** Only returns articles from the last 30 days (NewsAPI free tier limitation).

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `query` | `string` | Yes | Search keywords or phrase |
| `sources` | `string` | No | Comma-separated source IDs (e.g. `"bbc-news,cnn"`) |
| `domains` | `string` | No | Comma-separated domains (e.g. `"bbc.co.uk,techcrunch.com"`) |
| `from_date` | `string` | No | Oldest article date, ISO 8601 (e.g. `"2026-01-01"`) |
| `to_date` | `string` | No | Newest article date, ISO 8601 (e.g. `"2026-01-31"`) |
| `language` | `string` | No | 2-letter language code (default: `"en"`) |
| `sort_by` | `string` | No | `"relevancy"`, `"popularity"`, or `"publishedAt"` (default: `"publishedAt"`) |
| `page_size` | `integer` | No | Number of results, max 100 (default: `10`) |

**Example call:**

```json
{
  "name": "search_news",
  "arguments": {
    "query": "artificial intelligence",
    "sort_by": "relevancy",
    "page_size": 5
  }
}
```

**Example response:**

```json
{
  "query": "artificial intelligence",
  "articles": [
    {
      "title": "The State of AI in 2026",
      "description": "A comprehensive look at how AI has evolved...",
      "url": "https://example.com/ai-2026",
      "source": "Wired",
      "author": "John Doe",
      "published_at": "2026-02-10T14:30:00Z",
      "content": "First 200 characters of the article content..."
    }
  ],
  "total_results": 127
}
```

## Quick Start

### Local Development

```bash
git clone https://github.com/NimbleBrainInc/mcp-newsapi.git
cd mcp-newsapi

# Install dependencies
uv sync

# Set API key
cp .env.example .env
# Edit .env with your API key

# Run the server (stdio mode)
uv run python -m mcp_newsapi.server
```

The server supports HTTP transport with:
- Health check: `GET /health`
- MCP endpoint: `POST /mcp`

## Development

```bash
# Install with dev dependencies
uv sync --group dev

# Run all checks (format, lint, typecheck, unit tests)
make check

# Run unit tests
make test

# Run with coverage
make test-cov
```

## About

NewsAPI MCP Server is published on the [mpak registry](https://mpak.dev?utm_source=github&utm_medium=readme&utm_campaign=mcp-newsapi) and built by [NimbleBrain](https://nimblebrain.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp-newsapi). mpak is an open registry for [Model Context Protocol](https://modelcontextprotocol.io) servers.

- [mpak registry](https://mpak.dev?utm_source=github&utm_medium=readme&utm_campaign=mcp-newsapi)
- [NimbleBrain](https://nimblebrain.ai?utm_source=github&utm_medium=readme&utm_campaign=mcp-newsapi)
- [MCP specification](https://modelcontextprotocol.io)
- [Discord community](https://nimblebrain.ai/discord?utm_source=github&utm_medium=readme&utm_campaign=mcp-newsapi)

## License

MIT
