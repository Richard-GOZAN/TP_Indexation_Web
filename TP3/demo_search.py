"""
Simple Usage for Search Engine
Shows basic usage with formatted output
"""

from search_engine import SearchEngine
import json


def print_results(results: dict):
    """
    Pretty print search results
    
    Args:
        results: Search results dictionary
    """
    print(f"\n{'='*70}")
    print(f"SEARCH QUERY: '{results['query']}'")
    print("="*70)
    
    # Metadata
    meta = results['metadata']
    print(f"\nMetadata:")
    print(f"  Total documents in corpus: {meta['total_documents']}")
    print(f"  Filtered documents: {meta['documents_filtered']}")
    print(f"  Results returned: {meta['documents_returned']}")
    print(f"  Filter mode: {meta['filter_mode']}")
    print(f"  Ranking mode: {meta['ranking_mode']}")

    # Results
    print(f"\nResults:")
    print("-"*70)
    
    if not results['results']:
        print("  No results found.")
    else:
        for i, result in enumerate(results['results'], 1):
            print(f"\n{i}. {result['title']}")
            print(f"   Score: {result['score']:.2f}")
            
            # Reviews
            if result['review_stats'].get('total_reviews', 0) > 0:
                reviews = result['review_stats']
                print(f"   Reviews: ⭐ {reviews['mean_mark']:.1f}/5 ({reviews['total_reviews']} reviews)")
            
            # Description
            desc = result['description']
            if desc:
                desc_short = desc[:100] + "..." if len(desc) > 100 else desc
                print(f"   {desc_short}")
            
            print(f"   🔗 {result['url']}")


def main():
    """Main demo function"""
    
    print("="*70)
    print("E-COMMERCE SEARCH ENGINE")
    print("="*70)
    print("\nInitializing search engine...")
    
    # Initialize engine
    engine = SearchEngine(
        title_index_path='input/title_index.json',
        description_index_path='input/description_index.json',
        reviews_index_path='input/reviews_index.json',
        brand_index_path='input/brand_index.json',
        origin_index_path='input/origin_index.json',
        documents_path='input/rearranged_products.jsonl',
        synonyms_path='input/origin_synonyms.json'
    )
    
    print("Search engine initialized successfully!")
    
    # Example searches
    examples = [
        {
            'query': 'chocolate candy',
            'description': 'Simple product search'
        },
        {
            'query': 'leather sneakers',
            'description': 'Search by material and product type'
        },
        {
            'query': 'made in italy',
            'description': 'Search by origin (with synonyms)'
        }
    ]
    
    for example in examples:
        print(f"\n\n{'='*70}")
        print(f"EXAMPLE: {example['description']}")
        
        # Perform search
        results = engine.search(
            query=example['query'],
            filter_mode='any',
            ranking_mode='linear',
            use_synonyms=True,
            top_k=5
        )
        
        # Print results
        print_results(results)
    
    # Save one result as example
    print(f"\n\n{'='*70}")
    print("SAVING AN EXAMPLE RESULT")
    print("="*70)
    
    example_results = engine.search("chocolate candy", top_k=3)
    
    with open('output/example_search_result.json', 'w', encoding='utf-8') as f:
        json.dump(example_results, f, indent=2, ensure_ascii=False)
    
    print("Example saved to: output/example_search_result.json")

if __name__ == '__main__':
    main()
