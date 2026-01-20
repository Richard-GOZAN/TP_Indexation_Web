"""
Search Engine for TP3 - Web Indexing
Implements filtering, ranking, and search capabilities using pre-built indexes
"""

import json
import math
import string
from collections import defaultdict
from typing import Dict, List, Tuple, Set, Any


# NLTK English Stopwords 
# Generated using:
#   import nltk
#   from nltk.corpus import stopwords
#   nltk.download("stopwords")
#   STOPWORDS = set(stopwords.words("english"))
STOPWORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'ain', 'all', 'am', 'an', 
    'and', 'any', 'are', 'aren', "aren't", 'as', 'at', 'be', 'because', 'been', 
    'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can', 'couldn', 
    "couldn't", 'd', 'did', 'didn', "didn't", 'do', 'does', 'doesn', "doesn't", 
    'doing', 'don', "don't", 'down', 'during', 'each', 'few', 'for', 'from', 
    'further', 'had', 'hadn', "hadn't", 'has', 'hasn', "hasn't", 'have', 'haven', 
    "haven't", 'having', 'he', "he'd", "he'll", 'her', 'here', 'hers', 'herself', 
    "he's", 'him', 'himself', 'his', 'how', 'i', "i'd", 'if', "i'll", "i'm", 'in', 
    'into', 'is', 'isn', "isn't", 'it', "it'd", "it'll", "it's", 'its', 'itself', 
    "i've", 'just', 'll', 'm', 'ma', 'me', 'mightn', "mightn't", 'more', 'most', 
    'mustn', "mustn't", 'my', 'myself', 'needn', "needn't", 'no', 'nor', 'not', 
    'now', 'o', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'our', 'ours', 
    'ourselves', 'out', 'over', 'own', 're', 's', 'same', 'shan', "shan't", 'she', 
    "she'd", "she'll", "she's", 'should', 'shouldn', "shouldn't", "should've", 'so', 
    'some', 'such', 't', 'than', 'that', "that'll", 'the', 'their', 'theirs', 
    'them', 'themselves', 'then', 'there', 'these', 'they', "they'd", "they'll", 
    "they're", "they've", 'this', 'those', 'through', 'to', 'too', 'under', 'until', 
    'up', 've', 'very', 'was', 'wasn', "wasn't", 'we', "we'd", "we'll", "we're", 
    'were', 'weren', "weren't", "we've", 'what', 'when', 'where', 'which', 'while', 
    'who', 'whom', 'why', 'will', 'with', 'won', "won't", 'wouldn', "wouldn't", 
    'y', 'you', "you'd", "you'll", 'your', "you're", 'yours', 'yourself', 
    'yourselves', "you've"
}

# Total: 198 NLTK English stopwords 


def load_json(filepath: str) -> Dict:
    """
    Load JSON file
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        Loaded JSON data
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_jsonl(filepath: str) -> List[Dict]:
    """
    Load JSONL file
    
    Args:
        filepath: Path to JSONL file
        
    Returns:
        List of document dictionaries
    """
    documents = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                documents.append(json.loads(line))
    return documents


def tokenize(text: str) -> List[str]:
    """
    Tokenize text (identical to TP2)
    
    Args:
        text: Text to tokenize
        
    Returns:
        List of tokens
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Split by whitespace
    tokens = text.split()
    
    # Remove stopwords
    tokens = [token for token in tokens if token not in STOPWORDS]
    
    return tokens


def load_synonyms(filepath: str) -> Dict[str, List[str]]:
    """
    Load synonyms from JSON file
    
    Args:
        filepath: Path to synonyms JSON file
        
    Returns:
        Dictionary mapping terms to their synonyms
    """
    return load_json(filepath)


def expand_query_with_synonyms(tokens: List[str], synonyms: Dict[str, List[str]]) -> List[str]:
    """
    Expand query tokens with synonyms
    
    Args:
        tokens: Original query tokens
        synonyms: Synonym dictionary
        
    Returns:
        Expanded list of tokens including synonyms
    """
    expanded = list(tokens)
    
    for token in tokens:
        # Check if token is a key (original term)
        if token in synonyms:
            expanded.extend(synonyms[token])
        
        # Check if token appears in any synonym list
        for key, syn_list in synonyms.items():
            if token in syn_list and key not in expanded:
                expanded.append(key)
    
    return expanded


def filter_documents_any_token(query_tokens: List[str], 
                               title_index: Dict, 
                               description_index: Dict) -> Set[str]:
    """
    Filter documents containing at least one query token
    
    Args:
        query_tokens: List of query tokens
        title_index: Title inverted index
        description_index: Description inverted index
        
    Returns:
        Set of document URLs matching the filter
    """
    matching_urls = set()
    
    for token in query_tokens:
        # Check title index
        if token in title_index:
            matching_urls.update(title_index[token].keys())
        
        # Check description index
        if token in description_index:
            matching_urls.update(description_index[token].keys())
    
    return matching_urls


def filter_documents_all_tokens(query_tokens: List[str], 
                                title_index: Dict, 
                                description_index: Dict) -> Set[str]:
    """
    Filter documents containing all query tokens (excluding stopwords)
    
    Args:
        query_tokens: List of query tokens (already filtered from stopwords)
        title_index: Title inverted index
        description_index: Description inverted index
        
    Returns:
        Set of document URLs matching the filter
    """
    if not query_tokens:
        return set()
    
    # Get documents for first token
    first_token = query_tokens[0]
    matching_urls = set()
    
    if first_token in title_index:
        matching_urls.update(title_index[first_token].keys())
    if first_token in description_index:
        matching_urls.update(description_index[first_token].keys())
    
    # Intersect with documents for remaining tokens
    for token in query_tokens[1:]:
        token_urls = set()
        
        if token in title_index:
            token_urls.update(title_index[token].keys())
        if token in description_index:
            token_urls.update(description_index[token].keys())
        
        matching_urls &= token_urls
    
    return matching_urls


def calculate_term_frequency(token: str, url: str, 
                             title_index: Dict, 
                             description_index: Dict) -> Tuple[int, int]:
    """
    Calculate term frequency in title and description
    
    Args:
        token: Query token
        url: Document URL
        title_index: Title inverted index
        description_index: Description inverted index
        
    Returns:
        Tuple of (title_tf, description_tf)
    """
    title_tf = 0
    description_tf = 0
    
    if token in title_index and url in title_index[token]:
        title_tf = len(title_index[token][url])
    
    if token in description_index and url in description_index[token]:
        description_tf = len(description_index[token][url])
    
    return title_tf, description_tf


def calculate_bm25_score(query_tokens: List[str], 
                         url: str, 
                         title_index: Dict, 
                         description_index: Dict,
                         total_docs: int,
                         k1: float = 1.2, 
                         b: float = 0.75) -> float:
    """
    Calculate BM25 score for a document
    
    Args:
        query_tokens: List of query tokens
        url: Document URL
        title_index: Title inverted index
        description_index: Description inverted index
        total_docs: Total number of documents
        k1: Term frequency saturation (default: 1.2)
        b: Length normalization (default: 0.75)
        
    Returns:
        BM25 score
    """
    score = 0.0
    
    # Average document length (approximation)
    avg_doc_length = 50  
    
    # Calculate document length
    doc_length = 0
    for token in set(query_tokens):
        if token in title_index and url in title_index[token]:
            doc_length += len(title_index[token][url])
        if token in description_index and url in description_index[token]:
            doc_length += len(description_index[token][url])
    
    for token in query_tokens:
        # Calculate document frequency
        df = 0
        if token in title_index:
            df += len(title_index[token])
        if token in description_index:
            df += len(description_index[token])
        
        if df == 0:
            continue
        
        # Calculate IDF
        idf = math.log((total_docs - df + 0.5) / (df + 0.5) + 1.0)
        
        # Calculate term frequency
        tf_title, tf_desc = calculate_term_frequency(token, url, title_index, description_index)
        tf = tf_title + tf_desc
        
        # BM25 formula
        numerator = tf * (k1 + 1)
        denominator = tf + k1 * (1 - b + b * (doc_length / avg_doc_length))
        
        score += idf * (numerator / denominator)
    
    return score


def check_exact_match(query_tokens: List[str], 
                     url: str, 
                     title_index: Dict, 
                     description_index: Dict) -> Tuple[bool, bool]:
    """
    Check if query appears as exact phrase in title or description
    
    Args:
        query_tokens: List of query tokens (in order)
        url: Document URL
        title_index: Title inverted index
        description_index: Description inverted index
        
    Returns:
        Tuple of (title_exact_match, description_exact_match)
    """
    if not query_tokens:
        return False, False
    
    title_match = False
    description_match = False
    
    # Check title
    if len(query_tokens) == 1:
        title_match = query_tokens[0] in title_index and url in title_index[query_tokens[0]]
    else:
        # Check consecutive positions
        first_token = query_tokens[0]
        if first_token in title_index and url in title_index[first_token]:
            positions = title_index[first_token][url]
            for start_pos in positions:
                match = True
                for i, token in enumerate(query_tokens[1:], 1):
                    if token not in title_index or url not in title_index[token]:
                        match = False
                        break
                    if (start_pos + i) not in title_index[token][url]:
                        match = False
                        break
                if match:
                    title_match = True
                    break
    
    # Check description (similar logic)
    if len(query_tokens) == 1:
        description_match = query_tokens[0] in description_index and url in description_index[query_tokens[0]]
    else:
        first_token = query_tokens[0]
        if first_token in description_index and url in description_index[first_token]:
            positions = description_index[first_token][url]
            for start_pos in positions:
                match = True
                for i, token in enumerate(query_tokens[1:], 1):
                    if token not in description_index or url not in description_index[token]:
                        match = False
                        break
                    if (start_pos + i) not in description_index[token][url]:
                        match = False
                        break
                if match:
                    description_match = True
                    break
    
    return title_match, description_match


def calculate_linear_score(query_tokens: List[str],
                           url: str,
                           title_index: Dict,
                           description_index: Dict,
                           reviews_index: Dict,
                           brand_index: Dict,
                           origin_index: Dict,
                           documents_map: Dict[str, Dict],
                           weights: Dict[str, float]) -> float:
    """
    Calculate linear scoring combining multiple signals
    
    Args:
        query_tokens: List of query tokens
        url: Document URL
        title_index: Title inverted index
        description_index: Description inverted index
        reviews_index: Reviews statistics index
        brand_index: Brand inverted index
        origin_index: Origin inverted index
        documents_map: Map of URL to document data
        weights: Dictionary of feature weights
        
    Returns:
        Linear score
    """
    score = 0.0
    
    # Signal 1: Term frequency in title (higher weight)
    title_tf_total = 0
    for token in query_tokens:
        tf_title, _ = calculate_term_frequency(token, url, title_index, description_index)
        title_tf_total += tf_title
    score += weights.get('title_tf', 3.0) * title_tf_total
    
    # Signal 2: Term frequency in description
    desc_tf_total = 0
    for token in query_tokens:
        _, tf_desc = calculate_term_frequency(token, url, title_index, description_index)
        desc_tf_total += tf_desc
    score += weights.get('description_tf', 1.0) * desc_tf_total
    
    # Signal 3: Exact match bonus
    title_exact, desc_exact = check_exact_match(query_tokens, url, title_index, description_index)
    if title_exact:
        score += weights.get('title_exact_match', 10.0)
    if desc_exact:
        score += weights.get('description_exact_match', 5.0)
    
    # Signal 4: Review score
    if url in reviews_index:
        review_data = reviews_index[url]
        if review_data['total_reviews'] > 0:
            # Boost by average rating
            score += weights.get('review_score', 1.0) * review_data['mean_mark']
            # Boost by number of reviews (with diminishing returns)
            score += weights.get('review_count', 0.5) * math.log(review_data['total_reviews'] + 1)
    
    # Signal 5: Position in title (earlier positions are better)
    for token in query_tokens:
        if token in title_index and url in title_index[token]:
            positions = title_index[token][url]
            if positions:
                # Bonus for appearing early in title
                min_position = min(positions)
                position_bonus = weights.get('early_position', 1.0) * (1.0 / (min_position + 1))
                score += position_bonus
    
    # Signal 6: Brand match (if query contains brand name)
    doc_data = documents_map.get(url, {})
    doc_brand = doc_data.get('product_features', {}).get('brand', '').lower()
    query_text = ' '.join(query_tokens)
    if doc_brand and doc_brand in query_text:
        score += weights.get('brand_match', 5.0)
    
    # Signal 7: Document length penalty (avoid very short docs)
    doc_length = len(tokenize(doc_data.get('title', '') + ' ' + doc_data.get('description', '')))
    if doc_length < 10:
        score *= 0.7  # Penalty for very short documents
    
    return score


class SearchEngine:
    """Main search engine class"""
    
    def __init__(self, 
                 title_index_path: str,
                 description_index_path: str,
                 reviews_index_path: str,
                 brand_index_path: str,
                 origin_index_path: str,
                 documents_path: str,
                 synonyms_path: str):
        """
        Initialize search engine with indexes
        
        Args:
            title_index_path: Path to title index JSON
            description_index_path: Path to description index JSON
            reviews_index_path: Path to reviews index JSON
            brand_index_path: Path to brand index JSON
            origin_index_path: Path to origin index JSON
            documents_path: Path to documents JSONL
            synonyms_path: Path to synonyms JSON
        """
        print("Loading indexes...")
        self.title_index = load_json(title_index_path)
        self.description_index = load_json(description_index_path)
        self.reviews_index = load_json(reviews_index_path)
        self.brand_index = load_json(brand_index_path)
        self.origin_index = load_json(origin_index_path)
        self.synonyms = load_synonyms(synonyms_path)
        
        print("Loading documents...")
        self.documents = load_jsonl(documents_path)
        self.documents_map = {doc['url']: doc for doc in self.documents}
        
        self.total_docs = len(self.documents)
        
        print(f"Search engine initialized with {self.total_docs} documents")
    
    def search(self, 
               query: str, 
               filter_mode: str = 'any',
               ranking_mode: str = 'linear',
               use_synonyms: bool = True,
               top_k: int = 10,
               weights: Dict[str, float] = None) -> Dict:
        """
        Perform search
        
        Args:
            query: Search query string
            filter_mode: 'any' (at least one token) or 'all' (all tokens)
            ranking_mode: 'bm25' or 'linear'
            use_synonyms: Whether to expand query with synonyms
            top_k: Number of top results to return
            weights: Custom weights for linear scoring
            
        Returns:
            Search results dictionary
        """
        # Default weights for linear scoring
        if weights is None:
            weights = {
                'title_tf': 3.0,
                'description_tf': 1.0,
                'title_exact_match': 10.0,
                'description_exact_match': 5.0,
                'review_score': 1.5,
                'review_count': 0.5,
                'early_position': 1.0,
                'brand_match': 5.0
            }
        
        # Step 1: Tokenize query
        original_tokens = tokenize(query)
        
        # Step 2: Expand with synonyms if requested
        if use_synonyms:
            query_tokens = expand_query_with_synonyms(original_tokens, self.synonyms)
        else:
            query_tokens = original_tokens
        
        # Step 3: Filter documents
        if filter_mode == 'any':
            filtered_urls = filter_documents_any_token(
                query_tokens, self.title_index, self.description_index
            )
        else:  # 'all'
            filtered_urls = filter_documents_all_tokens(
                original_tokens, self.title_index, self.description_index
            )
        
        # Step 4: Rank documents
        ranked_results = []
        
        for url in filtered_urls:
            if ranking_mode == 'bm25':
                score = calculate_bm25_score(
                    query_tokens, url, 
                    self.title_index, self.description_index,
                    self.total_docs
                )
            else:  # 'linear'
                score = calculate_linear_score(
                    original_tokens, url,
                    self.title_index, self.description_index,
                    self.reviews_index, self.brand_index, self.origin_index,
                    self.documents_map, weights
                )
            
            # Get document data
            doc_data = self.documents_map.get(url, {})
            
            ranked_results.append({
                'url': url,
                'title': doc_data.get('title', ''),
                'description': doc_data.get('description', ''),
                'score': score,
                'review_stats': self.reviews_index.get(url, {})
            })
        
        # Sort by score descending, then by URL for deterministic ordering
        # This ensures consistent results when multiple documents have the same score
        ranked_results.sort(key=lambda x: (-x['score'], x['url']))
        
        # Take top K
        top_results = ranked_results[:top_k]
        
        # Format output
        return {
            'query': query,
            'query_tokens': original_tokens,
            'expanded_tokens': query_tokens if use_synonyms else None,
            'metadata': {
                'total_documents': self.total_docs,
                'documents_filtered': len(filtered_urls),
                'documents_returned': len(top_results),
                'filter_mode': filter_mode,
                'ranking_mode': ranking_mode,
                'use_synonyms': use_synonyms
            },
            'results': top_results
        }


def main():
    """Main function with example searches"""
    
    # Initialize search engine
    engine = SearchEngine(
        title_index_path='input/title_index.json',
        description_index_path='input/description_index.json',
        reviews_index_path='input/reviews_index.json',
        brand_index_path='input/brand_index.json',
        origin_index_path='input/origin_index.json',
        documents_path='input/rearranged_products.jsonl',
        synonyms_path='input/origin_synonyms.json'
    )
    
    # Example searches
    test_queries = [
        "chocolate candy",
        "leather sneakers",
        "energy drink",
        "made in italy",
        "kids shoes"
    ]
    
    print("\n" + "="*70)
    print("SEARCH ENGINE DEMONSTRATION")
    print("="*70)
    
    for query in test_queries:
        print(f"\n\n{'='*70}")
        print(f"Query: '{query}'")
        print("="*70)
        
        # Perform search
        results = engine.search(query, filter_mode='any', ranking_mode='linear', top_k=5)
        
        print(f"\nMetadata:")
        print(f"  Total documents: {results['metadata']['total_documents']}")
        print(f"  Filtered documents: {results['metadata']['documents_filtered']}")
        print(f"  Results returned: {results['metadata']['documents_returned']}")
        
        print(f"\nTop {len(results['results'])} Results:")
        for i, result in enumerate(results['results'], 1):
            print(f"\n{i}. {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   Score: {result['score']:.2f}")
            if result['review_stats'].get('total_reviews', 0) > 0:
                print(f"   Reviews: {result['review_stats']['mean_mark']:.1f}/5 ({result['review_stats']['total_reviews']} reviews)")
            desc = result['description'][:100] + "..." if len(result['description']) > 100 else result['description']
            print(f"   Description: {desc}")
    
    print("\n" + "="*70)
    print("Demo completed!")
    print("="*70)


if __name__ == '__main__':
    main()