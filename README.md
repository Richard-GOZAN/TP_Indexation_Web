# Web Indexing - ENSAI 2026

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Status](https://img.shields.io/badge/status-completed-green.svg)


Complete implementation of a web indexing system: crawling, indexing, and search engine.

---

## Project Structure

```
.
├── TP1/                          # Web Crawler
│   ├── crawler.py                # Main crawler implementation
│   ├── README.md                 # TP1 documentation
│   └── output/
│   │     └── crawled_pages.jsonl   # Crawler output 
│   └── requirements.txt          # Required python dependencies
│
├── TP2/                          # Indexer
│   ├── indexer.py                # Main indexer implementation
│   ├── README.md                 # TP2 documentation
|   └── intput/
│   │    ├── products.jsonl      # The documents
│   └── output/
│       ├── title_index.json      # Title inverted index
│       ├── description_index.json # Description inverted index
│       ├── brand_index.json      # Brand index
│       ├── origin_index.json     # Origin index
│       └── reviews_index.json    # Reviews index
│
└── TP3/                          # Search Engine
    ├── search_engine.py          # Main search engine
    ├── test_search.py            # Automated testing
    ├── demo_search.py            # Usage demonstration
    ├── README.md                 # TP3 technical documentation
    ├── analysis/                    # Input data
    │   ├── ANALYSIS_OBSERVATIONS.md  # Detailed analysis and observations
    ├── input/                    # Input data
    │   ├── rearranged_products.jsonl  # Enhanced product data
    │   ├── title_index.json
    │   ├── description_index.json
    │   ├── brand_index.json
    │   ├── origin_index.json
    │   ├── reviews_index.json
    │   └── origin_synonyms.json  # Country synonyms
    └── output/
    │   └── search_analysis_results.json  # Test results (28 tests)
    │   └── example_search_result.json    # Example search result
    └── requirements.txt          # Required python dependencies
```

---

## TP1 - Web Crawler

### Description
Python web crawler that extracts product information from web pages.


**See [TP1/README.md](TP1/README.md) for details**

---

## TP2 - Indexer

### Description
Creates inverted indexes from crawled data for efficient search.


**See [TP2/README.md](TP2/README.md) for details**

---

## TP3 - Search Engine

### Description
Complete search engine using indexes from TP2 to filter and rank results.


**See [TP3/README.md](TP3/README.md) and [TP3/analysis/ANALYSIS_OBSERVATIONS.md](TP3/analysis/ANALYSIS_OBSERVATIONS.md) for details**

---

## Data Flow

```
TP1: Web Pages → Crawler → crawled_pages.jsonl (156 documents)
                                    ↓
TP2: crawled_pages.jsonl → Indexer → 5 Inverted Indexes
                                    ↓
TP3: Indexes + Synonyms → Search Engine → Ranked Results
```

---



### Quick Start

```bash
# Clone repository
git clone https://github.com/Richard-GOZAN/TP_Indexation_Web.git
cd TP_Indexation_Web

# Run TP1 - Crawler
cd TP1
python crawler.py
cd ..

# Run TP2 - Indexer
cd TP2
python indexer.py
cd ..

# Run TP3 - Search Engine
cd TP3
python demo_search.py
```

---

## Author

- **Richard GOZAN**: ENSAI Student

## References

- [BeautifulSoup Documentation](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [NLTK Documentation](https://www.nltk.org/)
- [BM25 Algorithm](https://en.wikipedia.org/wiki/Okapi_BM25)
- [Test Site](https://web-scraping.dev/products)
