"""
Search Engine Analysis and Testing Script
Tests different configurations and documents the results
"""

import json
from search_engine import SearchEngine, tokenize


def save_results(results: dict, filename: str):
    """Save results to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Results saved to: {filename}")


def analyze_query_results(engine: SearchEngine, 
                          query: str, 
                          configurations: list) -> dict:
    """
    Test a query with different configurations
    
    Args:
        engine: SearchEngine instance
        query: Query string
        configurations: List of configuration dicts
        
    Returns:
        Analysis results dictionary
    """
    analysis = {
        'query': query,
        'configurations': []
    }
    
    for config in configurations:
        print(f"\n  Testing: {config['name']}")
        
        results = engine.search(
            query,
            filter_mode=config.get('filter_mode', 'any'),
            ranking_mode=config.get('ranking_mode', 'linear'),
            use_synonyms=config.get('use_synonyms', True),
            top_k=config.get('top_k', 10),
            weights=config.get('weights')
        )
        
        config_result = {
            'name': config['name'],
            'settings': config,
            'metadata': results['metadata'],
            'top_5_results': [
                {
                    'rank': i+1,
                    'title': r['title'],
                    'url': r['url'],
                    'score': round(r['score'], 2),
                    'reviews': r['review_stats']
                }
                for i, r in enumerate(results['results'][:5])
            ]
        }
        
        analysis['configurations'].append(config_result)
    
    return analysis


def main():
    """Main testing and analysis function"""
    
    print("="*70)
    print("SEARCH ENGINE TESTING AND ANALYSIS")
    print("="*70)
    
    # Initialize engine
    engine = SearchEngine(
        title_index_path='input/title_index.json',
        description_index_path='input/description_index.json',
        reviews_index_path='input/reviews_index.json',
        brand_index_path='input/brand_index.json',
        origin_index_path='input/origin_index.json',
        documents_path='rearranged_products.jsonl',
        synonyms_path='input/origin_synonyms.json'
    )
    
    # Define test queries
    test_queries = [
        {
            'query': 'chocolate candy',
            'description': 'Simple 2-word product query'
        },
        {
            'query': 'leather sneakers',
            'description': 'Material + product type'
        },
        {
            'query': 'energy drink',
            'description': 'Product category'
        },
        {
            'query': 'made in italy',
            'description': 'Origin filter (should use synonyms)'
        },
        {
            'query': 'kids light up shoes',
            'description': 'Long query with multiple tokens'
        },
        {
            'query': 'premium quality',
            'description': 'Quality descriptor (common across products)'
        },
        {
            'query': 'gamefuel',
            'description': 'Brand name search'
        }
    ]
    
    # Define configurations to test
    configurations = [
        {
            'name': 'Linear Scoring (Default)',
            'filter_mode': 'any',
            'ranking_mode': 'linear',
            'use_synonyms': True,
            'top_k': 10
        },
        {
            'name': 'BM25 Scoring',
            'filter_mode': 'any',
            'ranking_mode': 'bm25',
            'use_synonyms': True,
            'top_k': 10
        },
        {
            'name': 'Strict Filtering (All Tokens)',
            'filter_mode': 'all',
            'ranking_mode': 'linear',
            'use_synonyms': True,
            'top_k': 10
        },
        {
            'name': 'Review-Focused',
            'filter_mode': 'any',
            'ranking_mode': 'linear',
            'use_synonyms': True,
            'top_k': 10,
            'weights': {
                'title_tf': 2.0,
                'description_tf': 1.0,
                'title_exact_match': 10.0,
                'description_exact_match': 5.0,
                'review_score': 5.0,  # Increased
                'review_count': 2.0,  # Increased
                'early_position': 1.0,
                'brand_match': 5.0
            }
        }
    ]
    
    all_analyses = []
    
    # Test each query
    for test_query in test_queries:
        print(f"\n{'='*70}")
        print(f"Query: '{test_query['query']}'")
        print(f"Description: {test_query['description']}")
        print("="*70)
        
        analysis = analyze_query_results(
            engine, 
            test_query['query'],
            configurations
        )
        
        all_analyses.append(analysis)
    
    # Save all results
    output = {
        'test_date': '2026-01-14',
        'total_queries': len(test_queries),
        'configurations_tested': len(configurations),
        'analyses': all_analyses
    }

    save_results(output, 'output/search_analysis_results.json')

    # Generate summary report
    print(f"\n\n{'='*70}")
    print("ANALYSIS SUMMARY")
    print("="*70)
    
    for analysis in all_analyses:
        print(f"\nQuery: '{analysis['query']}'")
        
        for config in analysis['configurations']:
            print(f"\n  Configuration: {config['name']}")
            print(f"    Filtered docs: {config['metadata']['documents_filtered']}")
            print(f"    Top result: {config['top_5_results'][0]['title'] if config['top_5_results'] else 'None'}")
            if config['top_5_results']:
                print(f"    Top score: {config['top_5_results'][0]['score']}")
    
    print(f"\n{'='*70}")
    print("Analysis complete!")
    print("="*70)


if __name__ == '__main__':
    main()
