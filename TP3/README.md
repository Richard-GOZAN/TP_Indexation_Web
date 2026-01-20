# TP3 - E-Commerce Search Engine

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Status](https://img.shields.io/badge/status-completed-green.svg)

Complete search engine using inverted indexes created in TP2 to return and rank relevant results.

## Overview

This search engine implements a complete information retrieval system including:
- **Document Filtering**: With "any" (OR logic) and "all" (AND logic) modes
- **Query Expansion**: Via synonyms (particularly for origins)
- **Multi-criteria Ranking**: BM25 and custom linear scoring
- **Index Exploitation**: Optimal use of positions and metadata

### Input Data

**Indexes**:
- `title_index.json` - Inverted title index with positions
- `description_index.json` - Inverted description index with positions
- `brand_index.json`, `origin_index.json`, `reviews_index.json`

**Additional data**:
- `rearranged_products.jsonl` - Modified product documents
- `origin_synonyms.json` - Country synonyms for query expansion

### Output Format

```json
{
  "query": "chocolate candy",
  "metadata": {
    "total_documents": 156,
    "documents_filtered": 21,
    "documents_returned": 5
  },
  "results": [
    {
      "title": "Box of Chocolate Candy",
      "url": "https://...",
      "description": "...",
      "score": 33.63,
      "review_stats": {...}
    }
  ]
}
```

## Usage

### Basic Usage

```python
from search_engine import SearchEngine

# Initialize
engine = SearchEngine(
    title_index_path='title_index.json',
    description_index_path='description_index.json',
    reviews_index_path='reviews_index.json',
    brand_index_path='brand_index.json',
    origin_index_path='origin_index.json',
    documents_path='rearranged_products.jsonl',
    synonyms_path='origin_synonyms.json'
)

# Search
results = engine.search(
    query="chocolate candy",
    filter_mode='any',      # 'any' or 'all'
    ranking_mode='linear',  # 'linear' or 'bm25'
    use_synonyms=True,
    top_k=10
)
```

### Quick Demo

```bash
cd TP3
python demo_search.py    # Run demo
python test_search.py    # Run full analysis
```

## Key Features

### 1. Stopwords (NLTK)

Complete NLTK English stopwords list (198 words):


### 2. Document Filtering

**ANY Mode** (OR Logic): At least one token present
```python
Query: "chocolate candy" → 21 documents
```

**ALL Mode** (AND Logic): All tokens present (except stopwords)
```python
Query: "leather sneakers italy" → 3 documents
```

### 3. Synonym Expansion

Automatic enrichment for origins:
```json
{
  "usa": ["united states", "america"],
  "germany": ["deutschland"],
  "switzerland": ["swiss"]
}
```

Example:
```python
Query: "swiss chocolate"
→ Expanded: ["swiss", "switzerland", "chocolate"]
```

## Ranking Algorithms

### 1. BM25 (Baseline)

Classic IR algorithm with parameters:
- `k1 = 1.5` (term frequency saturation)
- `b = 0.75` (length normalization)

### 2. Linear Scoring (Default)

Multi-signal approach combining:

| Signal | Weight | Description |
|--------|--------|-------------|
| Title TF | 3.0 | Term frequency in title |
| Description TF | 1.0 | Term frequency in description |
| Title Exact | 10.0 | Exact phrase match in title |
| Description Exact | 5.0 | Exact phrase match in description |
| Review Score | 1.5 | Average product rating |
| Review Count | 0.5 | log(review_count + 1) |
| Early Position | 1.0 | 1/(position + 1) bonus |
| Brand Match | 5.0 | Query matches brand name |
| Length Penalty | -0.3 | Penalty for very short docs |

**Total**: 9 signals, 4 original (position, exact match, log reviews, length penalty)

## Original Signals

### 1. Position in Title
```python
bonus = 1.0 / (min_position + 1)
# "Chocolate Candy" → position 0 → bonus = 1.0
# "Box of Chocolate" → position 2 → bonus = 0.33
```

### 2. Exact Phrase Match
Uses position information to detect consecutive tokens:
```python
"Classic Leather Sneakers" → MATCH ✓
"Leather Goods and Sneakers" → NO MATCH ✗
```

### 3. Logarithmic Review Count
```python
score += 0.5 × log(review_count + 1)
# Diminishing returns: 1→10 reviews more important than 90→100
```

### 4. Document Length Penalty
```python
if doc_length < 10: score *= 0.7  # 30% penalty
```

## Testing & Analysis

### Test Queries (7)

1. `chocolate candy` - Simple 2-word
2. `leather sneakers` - Material + product
3. `energy drink` - Category
4. `made in italy` - Origin (synonyms)
5. `kids light up shoes` - Long query
6. `premium quality` - Common terms
7. `gamefuel` - Brand name

### Configurations (4)

1. **Linear (Default)** - All signals, balanced weights
2. **BM25** - Academic baseline
3. **Strict (ALL)** - AND filtering, reduces noise
4. **Review-Focused** - Increased review weights (×3)

**Total**: 7 queries × 4 configs = 28 tests documented in `search_analysis_results.json`

### Key Results

| Query | Best Config | Docs Filtered | Observation |
|-------|-------------|---------------|-------------|
| "chocolate candy" | Linear | 21 | All configs perform well |
| "made in italy" | Linear + Synonyms | 20 | Synonyms ESSENTIAL |
| "premium quality" | Strict (ALL) | 12 | Reduces noise effectively |
| "gamefuel" | Linear | 39 | Brand match signal crucial |

## Technical Choices

### Why Two Algorithms?

- **BM25**: baseline for comparison
- **Linear**: Exploits all available signals

### Why Title > Description Weight (3:1)?

Users write queries similar to titles. Empirical testing shows 3:1 ratio optimal.

### Why Logarithm for Reviews?

Avoids excessive bias toward very popular products. Implements diminishing returns naturally.

### Why ANY Filtering by Default?

Better user experience (high recall). Strict filtering available for precision.

---


