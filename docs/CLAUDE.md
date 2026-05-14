# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start

### Installation & Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env to add at least one LLM API key (DeepSeek, Qwen, Kimi, or Claude)
```

### Common Commands
```bash
# Test configuration
python main.py --test

# Run collection and analysis only
python main.py --collect

# Generate weekly report only
python main.py --report

# Full pipeline (collect + analyze + generate + distribute)
python main.py

# Schedule mode (runs on configured day/time)
python main.py --schedule

# Rebuild RAG knowledge base indexes
python build_index.py --reset

# Test RSS sources
python verify_rss_sources.py

# Test web collector targets
python test_web_urls.py
```

## Architecture Overview

This is a **4-stage intelligence pipeline** for telecom equipment industry monitoring:

### Stage 1: Multi-Source Collection
Concurrent data collection from three sources:
- **RSSCollector** (`collectors/rss_collector.py`): 10+ RSS feeds (ITmedia, Ars Technica, industry publications)
- **WebCollector** (`collectors/web_collector.py`): 75+ target company websites (Huawei, Ericsson, Nokia, etc.)
- **SearchCollector** (`collectors/search_collector.py`): 21 keyword searches via Bing with fallback to Jina Reader API

Each collector:
- Returns `CollectorResult` with list of `RawIntelData` items
- Implements retry logic and timeout handling
- Uses realistic browser headers to avoid blocking

### Stage 2: AI Analysis & Processing
Located in `processors/`:

**Analyzer** (`analyzer.py`):
- URL & title deduplication before LLM analysis
- LLM-based analysis using Router pattern for multi-model fallback (DeepSeek → Qwen → Kimi → Claude)
- Classifies into 5 categories: company_dynamics, patent_status, new_technology, investment_acquisition, downstream_industry
- Scores importance (1-5) and decides if decision-valuable
- Stores analyzed items in SQLite database

**RAG System** (`rag.py`):
- Uses ChromaDB for vector similarity search
- Enhances analysis with domain-specific technical knowledge from `knowledge_base/technical_keywords.yaml`
- Returns top-k similar documents for LLM context
- Similarity threshold: 0.7 (adjustable in config)

### Stage 3: Report Generation
`reporters/report_generator.py`:
- Queries week's data from database
- Applies multi-layer filtering (freshness, importance ≥4, max 5 per company, total 25 items)
- Structures into decision insights → competitive landscape → R&D progress �� downstream applications
- Generates both Markdown and HTML formats
- Saves to `data/reports/`

### Stage 4: Distribution
`reporters/distribution.py`:
- **Email**: SMTP-based distribution to configured recipients
- **WeChat**: Enterprise WeChat webhook integration
- Can send collection summaries via `--collect` mode

## Data Model

**RawIntelData** (raw from collectors):
```python
title: str           # Article title
url: str             # Source URL
summary: str         # Brief excerpt/description
source: str          # Collector type (RSS/Web/Search)
source_detail: str   # Specific RSS feed URL, website, etc.
collected_at: datetime
```

**IntelItem** (analyzed, stored in DB):
```python
title: str
source_url: str
category: str        # Enum: company_dynamics, patent_status, new_technology, investment_acquisition, downstream_industry
importance: int      # 1-5 scale
decision_value: bool # Whether decision-valuable
tech_domain: str     # Enum: wireless, optical, core_network, transmission, access, terminal
industry: str        # Downstream industry affected
rag_context: str     # RAG-retrieved knowledge context
created_at: datetime
```

## Configuration

### Environment Variables (`.env`)

**LLM Configuration** (at least one required):
```env
LLM__DEEPSEEK_API_KEY=your_key
LLM__DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

LLM__QWEN_API_KEY=your_key
LLM__QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

LLM__KIMI_API_KEY=your_key
LLM__KIMI_BASE_URL=https://api.moonshot.cn/v1

LLM__CLAUDE_API_KEY=your_key
LLM__CLAUDE_BASE_URL=https://api.anthropic.com/v1
```

**Collection Configuration**:
```env
COLLECTOR__JINA_API_KEY=your_key          # Fallback for web content extraction
COLLECTOR__REQUEST_TIMEOUT=60             # Seconds
COLLECTOR__MAX_RETRIES=5
```

**Distribution**:
```env
# Email (optional)
DISTRIBUTION__SMTP_SERVER=smtp.example.com
DISTRIBUTION__SMTP_PORT=587
DISTRIBUTION__SMTP_USER=your_email@example.com
DISTRIBUTION__SMTP_PASSWORD=your_password
DISTRIBUTION__EMAIL_RECIPIENTS=recipient1@example.com,recipient2@example.com
DISTRIBUTION__ENABLE_EMAIL=true

# Enterprise WeChat (optional)
DISTRIBUTION__WECHAT_WEBHOOK_URL=https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=...
DISTRIBUTION__ENABLE_WECHAT=true
```

**Scheduling**:
```env
SCHEDULE__DAY_OF_WEEK=fri  # mon,tue,wed,thu,fri,sat,sun
SCHEDULE__HOUR=9
SCHEDULE__MINUTE=0
```

### Config File (`config.py`)

Uses Pydantic Settings pattern with nested configuration classes:
- `LLMSettings`: Multi-model fallback chain
- `CollectorSettings`: RSS feeds, target companies, request parameters
- `DistributionSettings`: Email & WeChat configuration
- `ScheduleSettings`: Cron scheduling
- `Settings`: Global configuration with project paths

**Key modification points**:
- Add RSS feeds to `CollectorSettings.rss_feeds`
- Add company names to `CollectorSettings.target_companies`
- Update knowledge base in `knowledge_base/technical_keywords.yaml` and rebuild with `python build_index.py --reset`

## Code Organization

### Key Modules

| File | Purpose |
|------|---------|
| `main.py` | Entry point with CLI modes (test/collect/report/schedule) |
| `config.py` | Pydantic-based configuration management |
| `llm.py` | LLM router with multi-model fallback strategy |
| `database.py` | SQLite operations for storing analyzed items |
| `collectors/base.py` | Abstract base class for all collectors with HTTP client management |
| `processors/analyzer.py` | LLM-based analysis pipeline with deduplication |
| `processors/rag.py` | ChromaDB-based vector retrieval enhancement |
| `reporters/report_generator.py` | Weekly report generation logic |
| `reporters/distribution.py` | Email and WeChat distribution handlers |

### Directory Structure

```
telecom-equipment-intel/
├── main.py                          # CLI entry point
├── config.py                        # Configuration management
├── database.py                      # SQLite operations
├── llm.py                           # LLM routing
├── build_index.py                   # RAG index builder
├── collectors/                      # Data collection
│   ├── base.py                      # Abstract base + HTTP client
│   ├── rss_collector.py             # RSS feed collection
│   ├── web_collector.py             # Website scraping
│   ├── search_collector.py          # Search engine scraping
│   └── web_sites_config.py          # Company website URLs
├── processors/                      # Analysis
│   ├── analyzer.py                  # LLM analysis pipeline
│   └── rag.py                       # Vector search enhancement
├── reporters/                       # Report generation
│   ├── report_generator.py          # Report creation
│   └── distribution.py              # Email/WeChat sending
├── models/                          # Data models
├── knowledge_base/                  # Domain knowledge
│   └── technical_keywords.yaml      # Telecom concepts & keywords
├── data/                            # Runtime data
│   ├── intel.db                     # SQLite database
│   ├── chroma_db/                   # Vector index
│   ├── reports/                     # Generated reports
│   └── telecom_intel.log            # Application logs
├── requirements.txt
├── .env                             # Local configuration (git-ignored)
└── .env.example                     # Configuration template
```

## Important Patterns

### Async/Await Pattern
- All collectors use `async`/`await` for concurrent operations
- Main pipeline in `TelecomIntelAgent` orchestrates async tasks
- Use `asyncio.run()` for sync entry point

### Multi-Model Fallback Strategy
In `llm.py`:
```python
# Default chain: DeepSeek → Qwen → Kimi → Claude
# If primary model fails, automatically tries next in chain
# Requires at least one API key configured
```

### Configuration via Environment
- No hardcoded config values
- All settings loaded from `.env` via Pydantic Settings
- Prefix-based environment variable grouping (`LLM__`, `COLLECTOR__`, etc.)

### Collector Result Pattern
All collectors implement:
```python
async def collect(self) -> CollectorResult:
    # Returns: CollectorResult(items=[], success=bool, message=str, total_found=int)
```

### Data Flow in Analyzer
1. Deduplicates URLs across all collectors
2. For each unique item:
   - Retrieves RAG context from knowledge base
   - Calls LLM with template prompt + RAG context
   - Parses LLM response for enum validation
   - Stores to SQLite
3. Returns list of successfully analyzed items

### Report Generation Filters
- **Freshness**: Only items from current week
- **Importance**: importance ≥ 4 (5-point scale)
- **Deduplication**: Single company max 5 items
- **Total Cap**: Report limited to 25 items

## Testing & Debugging

### Configuration Verification
```bash
python main.py --test
```
Outputs available LLM providers, collector configuration, distribution setup.

### Test Individual Collectors
```bash
# Verify RSS source accessibility
python verify_rss_sources.py

# Test web collector targets
python test_web_urls.py

# Test search improvements
python test_search_improvements.py
```

### Logs
Application logs to:
- Console (on stderr)
- `data/telecom_intel.log` (rotated every 500MB, retained 30 days)

View recent logs:
```bash
tail -f data/telecom_intel.log
```

### Database Inspection
```bash
# SQLite shell
sqlite3 data/intel.db

# Common queries
SELECT COUNT(*) FROM intel_items;
SELECT category, COUNT(*) FROM intel_items GROUP BY category;
SELECT * FROM intel_items ORDER BY created_at DESC LIMIT 10;
```

## Common Development Tasks

### Add a New RSS Source
1. Edit `config.py`, `CollectorSettings.rss_feeds` list
2. Test with `python verify_rss_sources.py`
3. Commit with explanation of why source is valuable

### Add Target Company for Monitoring
1. Edit `config.py`, `CollectorSettings.target_companies` list
2. If adding website scraping, add entry to `collectors/web_sites_config.py`
3. Test with `python test_web_urls.py`

### Update Knowledge Base
1. Edit `knowledge_base/technical_keywords.yaml` with new concepts
2. Rebuild indexes: `python build_index.py --reset`
3. Next analysis will use updated knowledge

### Modify Report Structure
In `reporters/report_generator.py`, method `generate_weekly_report()`:
- Adjust filtering logic in section generation
- Modify HTML template in `_format_section_html()`
- Change importance thresholds or company limits

### Add Distribution Channel
1. Create handler in `reporters/distribution.py` (e.g., `DingTalkSender`)
2. Add configuration in `config.py` under `DistributionSettings`
3. Call from `Distributor.distribute_report()` method
4. Add environment variable documentation

## Performance Considerations

- **Concurrent Collection**: All three collectors run in parallel via `asyncio`
- **Deduplication**: URL-based first pass, then LLM-based title deduplication (fast)
- **RAG**: Vector search is efficient for top-5 retrieval (ChromaDB indexed)
- **LLM Calls**: ~1-2 seconds per item analysis (uses streaming where possible)
- **Typical Runtime**: 500-1000 items from collectors → 100-300 unique after dedup → 15-30 min for full analysis

## Troubleshooting

**Issue: No data collected**
- Check proxy settings if behind corporate firewall
- Verify RSS feeds are accessible: `python verify_rss_sources.py`
- Check LLM provider configuration: `python main.py --test`

**Issue: LLM analysis fails**
- Ensure at least one API key is configured
- Check API key validity and rate limits
- Check `data/telecom_intel.log` for specific error
- LLM router will automatically fallback to next provider

**Issue: Email/WeChat distribution fails**
- Verify SMTP or webhook credentials
- Check firewall/proxy settings
- Look in logs for connection errors
- Run `python setup_email_config.py` for email configuration help

**Issue: Duplicate reports in weekly schedule**
- Verify scheduler is not running multiple instances
- Check `python main.py --schedule` is only invoked once
- Use process manager (systemd, supervisor) to manage single instance
