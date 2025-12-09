"""
Feature Embeddings Test Script
Tests feature vector embeddings with 2 different models.
"""

from src.embeddings.feature_embeddings import FeatureEmbedder
from colorama import init, Fore, Style
import time
import numpy as np

init(autoreset=True)


def test_single_model(model_name: str, season: str = "2021-22"):
    """Test a single embedding model."""
    
    print(f"\n{Fore.CYAN}{'=' * 100}")
    print(f"{Fore.CYAN}{Style.BRIGHT}Testing Model: {model_name}")
    print(f"{Fore.CYAN}{'=' * 100}")
    
    try:
        # Initialize embedder
        print(f"\n{Fore.YELLOW}Initializing embedder...")
        start_time = time.time()
        
        with FeatureEmbedder(model_name=model_name) as embedder:
            init_time = time.time() - start_time
            print(f"{Fore.GREEN}✓ Model loaded in {init_time:.2f}s")
            print(f"{Fore.WHITE}Embedding dimension: {embedder.embedding_dim}")
            
            # Generate embeddings
            print(f"\n{Fore.YELLOW}Generating embeddings for season {season}...")
            start_time = time.time()
            
            embeddings = embedder.generate_embeddings(season=season, description_type="detailed")
            
            gen_time = time.time() - start_time
            print(f"{Fore.GREEN}✓ Generated {len(embeddings)} embeddings in {gen_time:.2f}s")
            
            # Analyze embeddings
            if embeddings:
                print(f"\n{Fore.CYAN}Embedding Statistics:")
                embedding_array = np.array(list(embeddings.values()))
                
                norms = np.linalg.norm(embedding_array, axis=1)
                print(f"{Fore.WHITE}  Mean norm: {np.mean(norms):.4f}")
                print(f"{Fore.WHITE}  Std norm: {np.std(norms):.4f}")
                print(f"{Fore.WHITE}  Min norm: {np.min(norms):.4f}")
                print(f"{Fore.WHITE}  Max norm: {np.max(norms):.4f}")
                
                # Show sample embeddings
                print(f"\n{Fore.CYAN}Sample Players:")
                for i, (player, emb) in enumerate(list(embeddings.items())[:3]):
                    print(f"{Fore.WHITE}  {i+1}. {player}")
                    print(f"{Fore.WHITE}     Embedding shape: {emb.shape}")
                    print(f"{Fore.WHITE}     First 5 values: {emb[:5]}")
            
            # Test similarity search
            print(f"\n{Fore.YELLOW}Testing similarity search...")
            
            test_queries = [
                "High scoring forward with lots of goals",
                "Midfielder with great assists and creativity",
                "Defender with clean sheets",
            ]
            
            for query in test_queries:
                print(f"\n{Fore.CYAN}Query: {Fore.WHITE}\"{query}\"")
                similar = embedder.find_similar_players(query, top_k=3)
                
                for i, result in enumerate(similar, 1):
                    print(f"{Fore.GREEN}  {i}. {result['player_name']} "
                          f"(similarity: {result['similarity']:.4f})")
            
            # Store embeddings (optional - commented out to avoid modifying DB)
            # print(f"\n{Fore.YELLOW}Storing embeddings in Neo4j...")
            # embedder.store_embeddings_in_neo4j(embeddings, season, 
            #                                   property_name=f"{model_name.replace('/', '_')}_embedding")
            # print(f"{Fore.GREEN}✓ Embeddings stored")
            
        return {
            'model_name': model_name,
            'embedding_dim': embedder.embedding_dim,
            'num_embeddings': len(embeddings),
            'init_time': init_time,
            'gen_time': gen_time,
            'mean_norm': float(np.mean(norms)),
            'std_norm': float(np.std(norms))
        }
        
    except Exception as e:
        print(f"{Fore.RED}✗ Error: {str(e)}")
        return {'model_name': model_name, 'error': str(e)}


def compare_two_models():
    """Compare two different embedding models."""
    
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}{'=' * 100}")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}FEATURE EMBEDDINGS - MODEL COMPARISON")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}{'=' * 100}")
    
    # Two models to compare
    models = [
        "all-MiniLM-L6-v2",  # Faster, smaller (384 dimensions)
        "all-mpnet-base-v2",  # Better quality (768 dimensions)
    ]
    
    results = {}
    
    for model in models:
        result = test_single_model(model, season="2021-22")
        results[model] = result
    
    # Comparison summary
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}{'=' * 100}")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}COMPARISON SUMMARY")
    print(f"{Fore.MAGENTA}{Style.BRIGHT}{'=' * 100}")
    
    print(f"\n{Fore.CYAN}{'Model':<30} {'Dimension':<12} {'Init Time':<12} {'Gen Time':<12} {'Embeddings':<12}")
    print(f"{Fore.CYAN}{'-' * 100}")
    
    for model, res in results.items():
        if 'error' not in res:
            print(f"{Fore.WHITE}{model:<30} "
                  f"{res['embedding_dim']:<12} "
                  f"{res['init_time']:<12.2f} "
                  f"{res['gen_time']:<12.2f} "
                  f"{res['num_embeddings']:<12}")
        else:
            print(f"{Fore.RED}{model:<30} ERROR: {res['error']}")
    
    print(f"\n{Fore.YELLOW}Performance Analysis:")
    
    # Find faster model
    if all('error' not in r for r in results.values()):
        fastest = min(results.items(), key=lambda x: x[1]['init_time'] + x[1]['gen_time'])
        best_quality = max(results.items(), key=lambda x: x[1]['embedding_dim'])
        
        print(f"{Fore.GREEN}  Fastest: {fastest[0]} "
              f"(total: {fastest[1]['init_time'] + fastest[1]['gen_time']:.2f}s)")
        print(f"{Fore.GREEN}  Highest dimension (potentially better quality): {best_quality[0]} "
              f"({best_quality[1]['embedding_dim']} dims)")
        
        # Recommendations
        print(f"\n{Fore.CYAN}Recommendations:")
        print(f"{Fore.WHITE}  • Use {Fore.GREEN}{models[0]}{Fore.WHITE} for: "
              f"Real-time applications, faster inference, lower memory")
        print(f"{Fore.WHITE}  • Use {Fore.GREEN}{models[1]}{Fore.WHITE} for: "
              f"Better accuracy, offline processing, quality prioritized")
    
    print(f"\n{Fore.MAGENTA}{'=' * 100}")


def test_description_formats():
    """Test different description formats."""
    
    print(f"\n{Fore.YELLOW}{Style.BRIGHT}{'=' * 100}")
    print(f"{Fore.YELLOW}{Style.BRIGHT}TESTING DESCRIPTION FORMATS")
    print(f"{Fore.YELLOW}{Style.BRIGHT}{'=' * 100}")
    
    with FeatureEmbedder("all-MiniLM-L6-v2") as embedder:
        # Get sample player
        players = embedder.get_player_features("2021-22")
        
        if players:
            sample = players[0]
            
            print(f"\n{Fore.CYAN}Sample Player Data:")
            print(f"{Fore.WHITE}{sample}")
            
            print(f"\n{Fore.CYAN}Simple Description:")
            simple = embedder.create_player_description(sample)
            print(f"{Fore.WHITE}{simple}")
            
            print(f"\n{Fore.CYAN}Detailed Description:")
            detailed = embedder.create_detailed_description(sample)
            print(f"{Fore.WHITE}{detailed}")
            
            # Compare embeddings
            simple_emb = embedder.model.encode(simple)
            detailed_emb = embedder.model.encode(detailed)
            
            print(f"\n{Fore.CYAN}Embedding Comparison:")
            print(f"{Fore.WHITE}  Simple embedding shape: {simple_emb.shape}")
            print(f"{Fore.WHITE}  Detailed embedding shape: {detailed_emb.shape}")
            print(f"{Fore.WHITE}  Similarity: {np.dot(simple_emb, detailed_emb) / (np.linalg.norm(simple_emb) * np.linalg.norm(detailed_emb)):.4f}")
    
    print(f"\n{Fore.YELLOW}{'=' * 100}")


if __name__ == "__main__":
    # Test description formats first
    test_description_formats()
    
    # Compare two models
    compare_two_models()
    
    print(f"\n{Fore.GREEN}{Style.BRIGHT}✓ ALL TESTS COMPLETED!")
