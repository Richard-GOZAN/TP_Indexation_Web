# TP2 - Web Indexing: Inverted Index Builder

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Status](https://img.shields.io/badge/status-completed-green.svg)

Indexer system for e-commerce product data, creating inverted indexes to enable efficient search capabilities.


## Table of Contents

- [Overview](#overview)
- [Index Structures](#index-structures)
- [Additional Indexes (Bonus Features)](#additional-indexes-bonus-features)
- [Technical Choices](#technical-choices)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
- [Code Structure](#code-structure)

## Overview

This project creates multiple inverted indexes from crawled e-commerce product data (JSONL format). The indexes enable efficient search, filtering, and ranking of products based on:
- Textual content (title, description)
- Product features (brand, origin, etc.)
- Review statistics (ratings, review counts)

### Input Data

JSONL file containing 150+ product documents with:
- URL
- Title
- Description
- Product features (brand, material, size, etc.)
- Reviews (date, rating, text)
- Internal links

### Output Indexes

The system generates the following indexes:

**Required indexes (5):**
1. **title_index.json** - Inverted index with position information
2. **description_index.json** - Inverted index with position information
3. **brand_index.json** - Feature-based inverted index
4. **origin_index.json** - Feature-based inverted index
5. **reviews_index.json** - Aggregated review statistics

**Additional indexes (4) - Bonus features:**
6. **material_index.json** - Material-based filtering
7. **colors_index.json** - Color-based filtering
8. **sizes_index.json** - Size-based filtering
9. **flavors_index.json** - Flavor-based filtering

## Index Structures

### 1. Title Index (with Positions)

**Structure**:
```json
{
  "token": {
    "url": [position1, position2, ...]
  }
}
```

**Example**:
```json
{
  "box": {
    "https://web-scraping.dev/product/1": [0],
    "https://web-scraping.dev/product/13": [0],
    "https://web-scraping.dev/product/25": [0]
  },
  "chocolate": {
    "https://web-scraping.dev/product/1": [2],
    "https://web-scraping.dev/product/13": [2]
  }
}
```

**Purpose**: 
- Quick lookup of documents containing specific terms in titles
- Position information enables phrase matching and proximity queries
- Essential for title-based search ranking

### 2. Description Index (with Positions)

**Structure**: Same as title index

**Example**:
```json
{
  "delicious": {
    "https://web-scraping.dev/product/1": [45, 89],
    "https://web-scraping.dev/product/16": [12]
  }
}
```

**Purpose**:
- Full-text search in product descriptions
- Position tracking for advanced query features
- Enables snippet generation and highlighting

### 3. Reviews Index (Statistics)

**Structure**:
```json
{
  "url": {
    "total_reviews": int,
    "mean_mark": float,
    "last_rating": int
  }
}
```

**Example**:
```json
{
  "https://web-scraping.dev/product/1": {
    "total_reviews": 5,
    "mean_mark": 4.6,
    "last_rating": 4
  }
}
```

**Purpose**:
- Ranking boost for well-reviewed products
- Filter products by review count/quality
- Display review statistics in search results

**Note**: This is NOT an inverted index - it's a direct mapping for ranking purposes.

### 4. Brand Index

**Structure**:
```json
{
  "brand_name": ["url1", "url2", ...]
}
```

**Example**:
```json
{
  "chocodelight": [
    "https://web-scraping.dev/product/1",
    "https://web-scraping.dev/product/1?variant=cherry-large",
    "https://web-scraping.dev/product/13"
  ],
  "gamefuel": [
    "https://web-scraping.dev/product/2",
    "https://web-scraping.dev/product/3"
  ]
}
```

**Purpose**:
- Filter products by brand
- Brand-based faceted search
- Multi-brand comparison

### 5. Origin Index

**Structure**: Same as brand index

**Example**:
```json
{
  "italy": [
    "https://web-scraping.dev/product/11",
    "https://web-scraping.dev/product/23"
  ],
  "usa": [
    "https://web-scraping.dev/product/12",
    "https://web-scraping.dev/product/24"
  ]
}
```

**Purpose**:
- Filter by country of origin
- "Made in" filters
- Geographic product search

**Note**: Maps to the "made in" feature in product data.

---

## Additional Indexes (Bonus Features)

Beyond the required 5 indexes, we implemented 4 additional feature indexes to enhance search capabilities. These were chosen based on their relevance to e-commerce search and the availability of data.

### 6. Material Index

**Structure**: Same as brand index

**Example**:
```json
{
  "premiumqualitychocolate": [
    "https://web-scraping.dev/product/1",
    "https://web-scraping.dev/product/13"
  ],
  "premiumgenuineleather": [
    "https://web-scraping.dev/product/11",
    "https://web-scraping.dev/product/23"
  ]
}
```

**Purpose**:
- Filter products by material composition
- Essential for shoppers with material preferences (vegan leather, organic fabrics)
- Quality indication (premium, synthetic, genuine)

**Coverage**: 93 documents (60% of catalog)

**Justification**: Material is a key decision factor in e-commerce, especially for:
- Footwear (leather vs. synthetic)
- Apparel (cotton, polyester, blends)
- Food products (organic, natural ingredients)

### 7. Colors Index

**Structure**: Feature-based inverted index

**Example**:
```json
{
  "black": [
    "https://web-scraping.dev/product/11",
    "https://web-scraping.dev/product/11?variant=black40"
  ],
  "red": [
    "https://web-scraping.dev/product/10",
    "https://web-scraping.dev/product/10?variant=red-5"
  ]
}
```

**Purpose**:
- Color-based product filtering
- One of the most common search filters in fashion e-commerce
- Enables visual search preferences

**Coverage**: 62 documents (40% of catalog)

**Justification**: Color is critical for:
- Fashion and apparel searches
- Personal preference matching
- Gift shopping (favorite colors)
- Inventory management by color variants

### 8. Sizes Index

**Structure**: Feature-based inverted index

**Example**:
```json
{
  "availablesmall": [...],
  "medium": [...],
  "largeboxes": [...]
}
```

**Purpose**:
- Size availability filtering
- Prevents showing out-of-stock sizes
- Critical for clothing and shoes

**Coverage**: 61 documents (39% of catalog)

**Justification**: Size filtering is essential for:
- Clothing and footwear purchases
- Gift sizing (kids aged 4-10, adult sizes 6-15)
- Reducing returns due to size mismatch
- Product packaging options (small, medium, large boxes)

### 9. Flavors Index

**Structure**: Feature-based inverted index

**Example**:
```json
{
  "availableorange": [
    "https://web-scraping.dev/product/1",
    "https://web-scraping.dev/product/1?variant=orange-small"
  ],
  "cherryflavors": [
    "https://web-scraping.dev/product/1",
    "https://web-scraping.dev/product/1?variant=cherry-medium"
  ]
}
```

**Purpose**:
- Flavor-based filtering for food/beverage products
- Taste preference matching
- Dietary restrictions (sugar-free, mint-free)

**Coverage**: 21 documents (13% of catalog - food/beverage category)

**Justification**: Flavor is crucial for:
- Food and beverage products
- Energy drinks (berry, citrus, mint)
- Confectionery (chocolate, cherry, orange)
- Personal taste preferences
- Dietary needs (avoiding certain flavors)

### Summary of Additional Indexes

| Index | Documents | Unique Values | Primary Use Case |
|-------|-----------|---------------|------------------|
| material | 93 (60%) | 7 | Material preference, quality filtering |
| colors | 62 (40%) | 13 | Visual search, fashion filtering |
| sizes | 61 (39%) | 9 | Size availability, fit matching |
| flavors | 21 (13%) | 8 | Taste preference, food/beverage filtering |

**Total Enhancement**: These 4 indexes cover 237 additional data points across the catalog, significantly improving search precision and user experience.

---

## Technical Choices

### Text Processing

#### Tokenization
```python
def tokenize(text: str) -> List[str]:
    """
    1. Convert to lowercase
    2. Remove punctuation
    3. Split by whitespace
    4. Remove stopwords
    """
```

**Stopwords Removed**: 
Common English words (a, an, the, is, of, etc.) - 38 total

**Rationale**:
- Reduces index size by ~30%
- Improves search precision
- Standard practice for English text

#### Case Normalization
All text converted to lowercase for case-insensitive matching.

#### Punctuation Handling
All punctuation removed to normalize tokens:
- "Box!" → "box"
- "High-quality" → "highquality"

### Feature Processing

#### Brand & Origin
```python
# Concatenate tokens to preserve brand names
"ChocoDelight" → tokenize → ["choco", "delight"] → join → "chocodelight"
```

**Rationale**: Brand names should be treated as single entities, not split words.

### URL Handling

#### Product ID Extraction
```python
extract_product_id("https://web-scraping.dev/product/1?variant=blue")
# Returns: ("1", "blue")
```

**Components**:
- Product ID: Numeric identifier from URL path
- Variant: Optional query parameter for product variations

### Position Tracking

Positions are 0-indexed within each document:
```
"Box of Chocolate Candy" → ["box", "chocolate", "candy"]
Positions: box=0, chocolate=1, candy=2
```

## Installation

### Prerequisites
- Python 3.8+
- Standard library only (no external dependencies)

### Setup
```bash
# Clone or download the project
git clone https://github.com/Richard-GOZAN/TP_Indexation_Web.git
cd TP2
```

## Usage

### Basic Usage

```bash
# Create all indexes from input/products.jsonl
python indexer.py 
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input` | Input JSONL file path | `products.jsonl` |
| `--output-dir` | Output directory for indexes | `output/` |

### Examples

```bash
# Use custom input file
python indexer.py --input ../TP1/output/crawled_products.jsonl

# Save indexes to specific directory
python indexer.py --output-dir ./indexes

# Full custom command
python indexer.py --input input/products.jsonl --output-dir ./output/
```

## Examples

### Example 1: Loading and Using Title Index

```python
import json

# Load the title index
with open('output/title_index.json', 'r') as f:
    title_index = json.load(f)

# Search for documents containing "sneakers"
if 'sneakers' in title_index:
    urls = title_index['sneakers'].keys()
    print(f"Found 'sneakers' in {len(urls)} documents:")
    for url in urls:
        positions = title_index['sneakers'][url]
        print(f"  {url} (positions: {positions})")
```

### Example 2: Filtering by Brand

```python
import json

# Load the brand index
with open('output/brand_index.json', 'r') as f:
    brand_index = json.load(f)

# Get all products from GameFuel
gamefuel_products = brand_index.get('gamefuel', [])
print(f"GameFuel has {len(gamefuel_products)} products:")
for url in gamefuel_products[:5]:
    print(f"  {url}")
```

### Example 3: Finding Highly-Rated Products

```python
import json

# Load the reviews index
with open('output/reviews_index.json', 'r') as f:
    reviews_index = json.load(f)

# Find products with mean rating >= 4.5 and at least 3 reviews
highly_rated = [
    (url, data)
    for url, data in reviews_index.items()
    if data['mean_mark'] >= 4.5 and data['total_reviews'] >= 3
]

print(f"Found {len(highly_rated)} highly-rated products:")
for url, data in highly_rated[:5]:
    print(f"  {url}: {data['mean_mark']:.1f}/5 ({data['total_reviews']} reviews)")
```



## Code Structure

```
indexer.py
├── STOPWORDS                           # English stopwords set
├── load_jsonl()                        # Load JSONL documents
├── extract_product_id()                # Parse URL for product ID
├── tokenize()                          # Text tokenization
├── create_inverted_index_with_positions()  # Title/description indexes
├── create_reviews_index()              # Reviews statistics
├── create_feature_index()              # Feature-based indexes
├── extract_all_features()              # Feature discovery
├── save_index()                        # Save index to JSON
├── build_all_indexes()                 # Main index builder
└── main()                              # CLI entry point
```


---


