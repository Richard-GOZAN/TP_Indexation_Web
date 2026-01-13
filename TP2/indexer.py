"""
Indexer for TP2
Creates inverted indexes from crawled e-commerce product data
"""

import json
import re
import string
from collections import defaultdict
from typing import Dict, List, Tuple, Any
from urllib.parse import urlparse, parse_qs


# English stopwords commonly used in e-commerce
STOPWORDS = {
    'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
    'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
    'to', 'was', 'will', 'with', 'you', 'your', 'our', 'this', 'these',
    'those', 'or', 'but', 'not', 'can', 'have', 'we', 'they', 'if'
}


def load_jsonl(filepath: str) -> List[Dict]:
    """
    Load documents from JSONL file
    
    Args:
        filepath: Path to the JSONL file
        
    Returns:
        List of document dictionaries
    """
    documents = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                documents.append(json.loads(line))
    return documents


def extract_product_id(url: str) -> Tuple[str, str]:
    """
    Extract product ID and variant from URL
    
    Args:
        url: Product URL
        
    Returns:
        Tuple of (product_id, variant)
        
    Examples:
        'https://web-scraping.dev/product/1' → ('1', '')
        'https://web-scraping.dev/product/1?variant=blue' → ('1', 'blue')
    """
    parsed = urlparse(url)
    path_parts = parsed.path.strip('/').split('/')
    
    # Extract product ID from path
    product_id = ''
    if len(path_parts) > 1 and path_parts[0] == 'product':
        product_id = path_parts[1]
    
    # Extract variant from query parameters
    variant = ''
    if parsed.query:
        params = parse_qs(parsed.query)
        if 'variant' in params:
            variant = params['variant'][0]
    
    return product_id, variant


def tokenize(text: str) -> List[str]:
    """
    Tokenize text by removing punctuation and converting to lowercase
    
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


def create_inverted_index_with_positions(documents: List[Dict], field: str) -> Dict[str, Dict[str, List[int]]]:
    """
    Create an inverted index with position information for a specific field
    
    Args:
        documents: List of document dictionaries
        field: Field name to index ('title' or 'description')
        
    Returns:
        Inverted index: {token: {url: [positions]}}
    """
    index = defaultdict(lambda: defaultdict(list))
    
    for doc in documents:
        url = doc.get('url', '')
        text = doc.get(field, '')
        
        if not text:
            continue
        
        # Tokenize and record positions
        tokens = tokenize(text)
        
        for position, token in enumerate(tokens):
            # Store position for this token in this document
            index[token][url].append(position)
    
    # Convert defaultdict to regular dict for JSON serialization
    result = {}
    for token, urls in index.items():
        result[token] = dict(urls)
    
    return result


def create_inverted_index_simple(documents: List[Dict], field: str) -> Dict[str, List[str]]:
    """
    Create a simple inverted index without position information
    
    Args:
        documents: List of document dictionaries
        field: Field name to index
        
    Returns:
        Inverted index: {token: [urls]}
    """
    index = defaultdict(set)
    
    for doc in documents:
        url = doc.get('url', '')
        text = doc.get(field, '')
        
        if not text:
            continue
        
        # Tokenize
        tokens = tokenize(text)
        
        for token in tokens:
            index[token].add(url)
    
    # Convert sets to sorted lists
    result = {}
    for token, urls in index.items():
        result[token] = sorted(list(urls))
    
    return result


def create_reviews_index(documents: List[Dict]) -> Dict[str, Dict[str, Any]]:
    """
    Create reviews index with aggregated review statistics
    
    Args:
        documents: List of document dictionaries
        
    Returns:
        Reviews index: {url: {total_reviews, mean_mark, last_rating}}
    """
    index = {}
    
    for doc in documents:
        url = doc.get('url', '')
        reviews = doc.get('product_reviews', [])
        
        # Calculate statistics
        total_reviews = len(reviews)
        
        if total_reviews > 0:
            ratings = [review.get('rating', 0) for review in reviews]
            mean_mark = sum(ratings) / len(ratings)
            last_rating = reviews[-1].get('rating', 0)  # Last review
        else:
            mean_mark = 0
            last_rating = 0
        
        index[url] = {
            'total_reviews': total_reviews,
            'mean_mark': mean_mark,
            'last_rating': last_rating
        }
    
    return index


def create_feature_index(documents: List[Dict], feature_name: str) -> Dict[str, List[str]]:
    """
    Create an inverted index for a specific product feature
    
    Args:
        documents: List of document dictionaries
        feature_name: Name of the feature to index (e.g., 'brand', 'origin', 'material')
        
    Returns:
        Feature index: {feature_value: [urls]}
    """
    index = defaultdict(set)
    
    # Map feature names to their variations in the data
    feature_mappings = {
        'origin': ['made in'],
        'sizes': ['sizes', 'size'],
        'flavors': ['flavors', 'flavor'],
        'care_instructions': ['care_instructions', 'care instructions']
    }
    
    for doc in documents:
        url = doc.get('url', '')
        features = doc.get('product_features', {})
        
        # Get the feature value(s) - check variations
        feature_keys = feature_mappings.get(feature_name, [feature_name])
        feature_value = ''
        
        for key in feature_keys:
            if key in features:
                feature_value = features[key]
                break
        
        if feature_value:
            # Tokenize the feature value to handle multi-word features
            tokens = tokenize(feature_value)
            
            # Different handling based on feature type
            if feature_name in ['brand', 'origin']:
                # Concatenate all tokens for brand/origin to keep them as single entities
                key = ''.join(tokens)
            elif feature_name in ['colors', 'sizes', 'flavors']:
                # For multi-value features, split by common separators and index each value
                # Handle patterns like "Available in Red and Blue" or "Sizes: S, M, L"
                values = feature_value.lower()
                # Split by 'and', 'or', commas
                import re
                values = re.split(r'\s+and\s+|\s+or\s+|,\s*', values)
                
                for value in values:
                    value_tokens = tokenize(value)
                    if value_tokens:
                        # For colors/sizes, keep individual words or concatenate
                        key = ''.join(value_tokens) if len(value_tokens) <= 2 else ' '.join(value_tokens)
                        if key:
                            index[key].add(url)
                continue  # Already processed, skip the default handling
            else:
                # For other features, concatenate tokens
                key = ''.join(tokens)
            
            if key:
                index[key].add(url)
    
    # Convert sets to sorted lists
    result = {}
    for key, urls in index.items():
        result[key] = sorted(list(urls))
    
    return result


def extract_all_features(documents: List[Dict]) -> List[str]:
    """
    Extract all unique feature names from documents
    
    Args:
        documents: List of document dictionaries
        
    Returns:
        List of unique feature names
    """
    features = set()
    
    for doc in documents:
        product_features = doc.get('product_features', {})
        features.update(product_features.keys())
    
    return sorted(list(features))


def save_index(index: Dict, filepath: str):
    """
    Save index to JSON file
    
    Args:
        index: Index dictionary to save
        filepath: Path to output file
    """
    # Create parent directory if it doesn't exist
    import os
    os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"Index saved to: {filepath}")


def build_all_indexes(input_file: str, output_dir: str = '.'):
    """
    Build all required indexes from JSONL input file
    
    Args:
        input_file: Path to input JSONL file
        output_dir: Directory to save output indexes
    """
    print("="*60)
    print("INDEXER - TP2 Web Indexing")
    print("="*60)
    
    # Load documents
    print(f"\nLoading documents from {input_file}...")
    documents = load_jsonl(input_file)
    print(f"Loaded {len(documents)} documents")
    
    # Extract all features
    print("\nExtracting features...")
    all_features = extract_all_features(documents)
    print(f"Found {len(all_features)} unique features: {', '.join(all_features[:10])}")
    
    # Create title index with positions
    print("\n" + "-"*60)
    print("Creating title index (with positions)...")
    title_index = create_inverted_index_with_positions(documents, 'title')
    save_index(title_index, f"{output_dir}/title_index.json")
    print(f"  Tokens indexed: {len(title_index)}")
    
    # Create description index with positions
    print("\n" + "-"*60)
    print("Creating description index (with positions)...")
    description_index = create_inverted_index_with_positions(documents, 'description')
    save_index(description_index, f"{output_dir}/description_index.json")
    print(f"  Tokens indexed: {len(description_index)}")
    
    # Create reviews index
    print("\n" + "-"*60)
    print("Creating reviews index...")
    reviews_index = create_reviews_index(documents)
    save_index(reviews_index, f"{output_dir}/reviews_index.json")
    print(f"  Documents indexed: {len(reviews_index)}")
    
    # Create feature indexes
    print("\n" + "-"*60)
    print("Creating feature indexes...")
    
    # Required indexes: brand and origin
    for feature in ['brand', 'origin']:
        print(f"\n  Creating {feature} index...")
        feature_index = create_feature_index(documents, feature)
        save_index(feature_index, f"{output_dir}/{feature}_index.json")
        print(f"    Unique values: {len(feature_index)}")
    
    # Additional indexes (bonus features for better search capabilities)
    print("\n" + "-"*60)
    print("Creating additional feature indexes (bonus)...")
    
    additional_indexes = [
        ('material', 'Material filter (leather, fabric, chocolate, etc.)'),
        ('colors', 'Color filter (red, blue, black, etc.)'),
        ('sizes', 'Size filter (small, medium, large, numeric sizes)'),
        ('flavors', 'Flavor filter (for food and beverages)')
    ]
    
    for feature, description in additional_indexes:
        # Check if feature exists in data
        feature_count = sum(1 for doc in documents if feature in doc.get('product_features', {}))
        
        if feature_count > 0:
            print(f"\n  Creating {feature} index...")
            print(f"    Purpose: {description}")
            feature_index = create_feature_index(documents, feature)
            save_index(feature_index, f"{output_dir}/{feature}_index.json")
            print(f"    Unique values: {len(feature_index)}")
            print(f"    Documents: {feature_count}")
        else:
            print(f"\n  Skipping {feature} index (no data found)")
    
    print("\n" + "="*60)
    print("INDEXING COMPLETE")
    print("="*60)
    
    # Summary
    print("\nIndex Summary:")
    print("  Required indexes: 5 (title, description, brand, origin, reviews)")
    print("  Additional indexes: 4 (material, colors, sizes, flavors)")
    print("  Total: 9 indexes")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Create inverted indexes from JSONL product data - TP2 ENSAI 2026'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='input/products.jsonl',
        help='Input JSONL file (default: input/products.jsonl)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='output',
        help='Output directory for index files (default: output/)'
    )
    
    args = parser.parse_args()
    
    # Build all indexes
    build_all_indexes(args.input, args.output_dir)


if __name__ == '__main__':
    main()
