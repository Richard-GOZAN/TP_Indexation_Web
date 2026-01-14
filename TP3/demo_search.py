"""
Simple Usage Example - TP3 Search Engine
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
    print(f"RECHERCHE: '{results['query']}'")
    print("="*70)
    
    # Metadata
    meta = results['metadata']
    print(f"\nMétadonnées:")
    print(f"  Total documents corpus: {meta['total_documents']}")
    print(f"  Documents filtrés: {meta['documents_filtered']}")
    print(f"  Résultats retournés: {meta['documents_returned']}")
    print(f"  Mode filtrage: {meta['filter_mode']}")
    print(f"  Mode ranking: {meta['ranking_mode']}")
    
    # Results
    print(f"\nRésultats:")
    print("-"*70)
    
    if not results['results']:
        print("  Aucun résultat trouvé.")
    else:
        for i, result in enumerate(results['results'], 1):
            print(f"\n{i}. {result['title']}")
            print(f"   Score: {result['score']:.2f}")
            
            # Reviews
            if result['review_stats'].get('total_reviews', 0) > 0:
                reviews = result['review_stats']
                print(f"   Avis: ⭐ {reviews['mean_mark']:.1f}/5 ({reviews['total_reviews']} avis)")
            
            # Description
            desc = result['description']
            if desc:
                desc_short = desc[:100] + "..." if len(desc) > 100 else desc
                print(f"   {desc_short}")
            
            print(f"   🔗 {result['url']}")


def main():
    """Main demo function"""
    
    print("="*70)
    print("TP3 - MOTEUR DE RECHERCHE E-COMMERCE")
    print("="*70)
    print("\nInitialisation du moteur...")
    
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
    
    print("✓ Moteur initialisé avec succès!")
    
    # Example searches
    examples = [
        {
            'query': 'chocolate candy',
            'description': 'Recherche simple de produit'
        },
        {
            'query': 'leather sneakers',
            'description': 'Recherche par matériau et type'
        },
        {
            'query': 'made in italy',
            'description': 'Recherche par origine (avec synonymes)'
        }
    ]
    
    for example in examples:
        print(f"\n\n{'='*70}")
        print(f"EXEMPLE: {example['description']}")
        
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
    print("SAUVEGARDE D'UN EXEMPLE")
    print("="*70)
    
    example_results = engine.search("chocolate candy", top_k=3)
    
    with open('output/example_search_result.json', 'w', encoding='utf-8') as f:
        json.dump(example_results, f, indent=2, ensure_ascii=False)
    
    print("✓ Exemple sauvegardé dans: output/example_search_result.json")
    
    print(f"\n\n{'='*70}")
    print("DÉMO TERMINÉE")
    print("="*70)
    print("\nPour utiliser le moteur dans notre code:")
    print("  1. Importer: from search_engine import SearchEngine")
    print("  2. Initialiser: engine = SearchEngine(...)")
    print("  3. Rechercher: results = engine.search('votre requête')")
    print("\nVoir README.md du TP3 pour documentation complète.")


if __name__ == '__main__':
    main()
