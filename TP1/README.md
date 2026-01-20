# TP1 - Web Crawler

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Status](https://img.shields.io/badge/status-completed-green.svg)

## Overview

Python web crawler for extracting product information. Prioritizes product pages and respects web politeness rules.

## Features

- Title, description, and link extraction
- Product feature extraction
- Product review extraction
- URL prioritization ('product' in path)
- robots.txt compliance
- Configurable request delay
- JSONL output format

## Installation

```bash
cd TP1
pip install -r requirements.txt
```

## Usage

### Basic

```bash
python crawler.py
```

### Custom Parameters

```bash
python crawler.py --url URL --max-pages N --delay SECONDS --output FILE
```

**Arguments**:
- `--url`: Starting URL (default: https://web-scraping.dev/products)
- `--max-pages`: Maximum pages (default: 50)
- `--delay`: Request delay in seconds (default: 1.0)
- `--output`: Output file (default: output/crawled_pages.jsonl)

### Examples

```bash
# Crawl 100 pages with 2-second delay
python crawler.py --max-pages 100 --delay 2

# Custom starting URL
python crawler.py --url https://web-scraping.dev/product/1
```

## Output Format

JSONL format (one JSON object per line):

```json
{
  "url": "https://web-scraping.dev/product/1",
  "title": "Box of Chocolate Candy",
  "description": "Indulge your sweet tooth...",
  "product_features": {
    "material": "Premium quality chocolate",
    "flavors": "Available in Orange and Cherry flavors"
  },
  "links": ["https://...", "https://..."],
  "product_reviews": [
    {
      "date": "2022-07-22",
      "id": "chocolate-candy-box-1",
      "rating": 5,
      "text": "Absolutely delicious!"
    }
  ]
}
```

## Architecture

### Classes

**RobotsChecker**: robots.txt verification
- `can_fetch(url, user_agent)`: Check crawl permission

**WebCrawler**: Main crawler
- `__init__(start_url, max_pages, delay)`: Initialize
- `is_product_url(url)`: Check if product page
- `crawl()`: Execute crawling
- `save_results(output_file)`: Save to file

### Functions

- `fetch_page(url, timeout)`: Fetch HTML
- `extract_title(soup)`: Extract title
- `extract_description(soup)`: Extract description
- `extract_product_features(soup)`: Extract features
- `extract_product_reviews(soup)`: Extract reviews
- `extract_links(soup, base_url)`: Extract links

## Technical Details

### URL Prioritization
- Priority 0: URLs with "product" (high)
- Priority 1: Other URLs (low)

### Politeness
- robots.txt verification
- Configurable delay (default: 1s)
- User-Agent: `ENSAI-Crawler/1.0`

### Error Handling
- HTTP timeout (10s)
- Content-Type check (HTML only)
- URL normalization
- Domain filtering


