"""
Embedding Models Comparison - Quantitative Analysis

Compares two embedding models used in the FPL Graph-RAG system:
1. all-mpnet-base-v2 (768 dimensions)
2. all-MiniLM-L6-v2 (384 dimensions)

Metrics:
- Retrieval quality (precision, recall)
- Semantic similarity scores
- Response time impact
- Memory footprint
- Trade-offs analysis
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.embedding_retriever import EmbeddingRetriever
import time
import json
from typing import Dict, List, Any
from datetime import datetime

class EmbeddingModelComparator:
    """Compare embedding model performance."""
    
    def __init__(self):
        self.results = []
        self.test_queries = [
            {
                'query': 'best arsenal midfielders',
                'season': '2021-22',
                'type': 'team_position',
                'expected_players': ['Bukayo Saka', 'Martin Ødegaard', 'Emile Smith Rowe']
            },
            {
                'query': 'top liverpool defenders',
                'season': '2022-23',
                'type': 'team_position',
                'expected_players': ['Trent Alexander-Arnold', 'Virgil van Dijk', 'Andrew Robertson']
            },
            {
                'query': 'best value midfielders',
                'season': '2021-22',
                'type': 'value_semantic',
                'expected_players': ['Bukayo Saka', 'Conor Gallagher', 'James Maddison']
            },
            {
                'query': 'high scoring forwards',
                'season': '2021-22',
                'type': 'semantic_position',
                'expected_players': ['Mohamed Salah', 'Heung-Min Son', 'Cristiano Ronaldo']
            },
            {
                'query': 'defensive midfielders with good passing',
                'season': '2021-22',
                'type': 'complex_semantic',
                'expected_players': ['Rodri', 'Fabinho', 'Thiago Alcántara']
            }
        ]
    
    def calculate_precision_recall(self, retrieved: List[str], expected: List[str]) -> Dict[str, float]:
        """Calculate precision and recall."""
        retrieved_set = set(retrieved)
        expected_set = set(expected)
        
        true_positives = len(retrieved_set.intersection(expected_set))
        
        precision = true_positives / len(retrieved_set) if retrieved_set else 0
        recall = true_positives / len(expected_set) if expected_set else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            'precision': round(precision, 3),
            'recall': round(recall, 3),
            'f1_score': round(f1, 3),
            'true_positives': true_positives
        }
    
    def test_embedding_model(self, model_name: str, top_k: int = 10):
        """Test single embedding model."""
        print(f"\n{'='*80}")
        print(f"Testing: {model_name}")
        print(f"{'='*80}")
        
        # Initialize retriever
        retriever = EmbeddingRetriever(
            model_name=model_name,
            use_hybrid=True,
            numerical_weight=0.5,
            text_weight=0.5
        )
        
        model_results = []
        
        for i, test in enumerate(self.test_queries, 1):
            print(f"\n[{i}/{len(self.test_queries)}] Query: '{test['query']}'")
            print(f"    Type: {test['type']} | Expected: {test['expected_players']}")
            
            # Run semantic search
            start_time = time.time()
            result = retriever.semantic_search(
                query=test['query'],
                top_k=top_k,
                season=test['season']
            )
            elapsed = time.time() - start_time
            
            # Extract player names
            players = result.get('players', [])
            retrieved_names = [p.get('player_name', '') for p in players]
            similarity_scores = [p.get('similarity_score', 0) for p in players]
            
            # Calculate metrics
            metrics = self.calculate_precision_recall(retrieved_names, test['expected_players'])
            
            # Average similarity score
            avg_similarity = sum(similarity_scores) / len(similarity_scores) if similarity_scores else 0
            max_similarity = max(similarity_scores) if similarity_scores else 0
            min_similarity = min(similarity_scores) if similarity_scores else 0
            
            print(f"    Retrieved: {len(retrieved_names)} players")
            print(f"    Precision: {metrics['precision']:.3f} | Recall: {metrics['recall']:.3f} | F1: {metrics['f1_score']:.3f}")
            print(f"    Similarity: avg={avg_similarity:.3f}, max={max_similarity:.3f}, min={min_similarity:.3f}")
            print(f"    Time: {elapsed:.3f}s")
            
            # Top 3 retrieved
            if retrieved_names:
                print(f"    Top 3: {retrieved_names[:3]}")
            
            test_result = {
                'query': test['query'],
                'query_type': test['type'],
                'season': test['season'],
                'model': model_name,
                'expected_players': test['expected_players'],
                'retrieved_players': retrieved_names,
                'retrieved_count': len(retrieved_names),
                'precision': metrics['precision'],
                'recall': metrics['recall'],
                'f1_score': metrics['f1_score'],
                'true_positives': metrics['true_positives'],
                'avg_similarity': round(avg_similarity, 3),
                'max_similarity': round(max_similarity, 3),
                'min_similarity': round(min_similarity, 3),
                'response_time_sec': round(elapsed, 3),
                'top_3_players': retrieved_names[:3],
                'top_3_scores': similarity_scores[:3]
            }
            
            model_results.append(test_result)
        
        retriever.close()
        return model_results
    
    def run_comparison(self):
        """Run comparison between both models."""
        print("\n" + "="*80)
        print("EMBEDDING MODELS COMPARISON")
        print("="*80)
        print("\nModel 1: all-mpnet-base-v2 (768 dimensions)")
        print("Model 2: all-MiniLM-L6-v2 (384 dimensions)")
        print(f"\nTest Queries: {len(self.test_queries)}")
        print("="*80)
        
        # Test Model 1
        model1_results = self.test_embedding_model('all-mpnet-base-v2', top_k=10)
        self.results.extend(model1_results)
        
        # Test Model 2
        model2_results = self.test_embedding_model('all-MiniLM-L6-v2', top_k=10)
        self.results.extend(model2_results)
    
    def save_results(self, filename: str = "embedding_comparison_results.json"):
        """Save results to JSON."""
        path = os.path.join(os.path.dirname(__file__), filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Results saved: {path}")
        return path
    
    def generate_summary(self):
        """Generate comparison summary."""
        print("\n" + "="*80)
        print("COMPARATIVE ANALYSIS")
        print("="*80)
        
        # Group by model
        model1_results = [r for r in self.results if r['model'] == 'all-mpnet-base-v2']
        model2_results = [r for r in self.results if r['model'] == 'all-MiniLM-L6-v2']
        
        def calc_avg(results, key):
            return sum(r[key] for r in results) / len(results) if results else 0
        
        print("\n📊 OVERALL METRICS:")
        print("\n| Metric | mpnet-768D | MiniLM-384D | Winner |")
        print("|--------|------------|-------------|--------|")
        
        metrics = [
            ('precision', 'Precision', 'higher'),
            ('recall', 'Recall', 'higher'),
            ('f1_score', 'F1 Score', 'higher'),
            ('avg_similarity', 'Avg Similarity', 'higher'),
            ('response_time_sec', 'Response Time (s)', 'lower')
        ]
        
        for metric_key, metric_label, better in metrics:
            m1_val = calc_avg(model1_results, metric_key)
            m2_val = calc_avg(model2_results, metric_key)
            
            if better == 'higher':
                winner = 'mpnet-768D' if m1_val > m2_val else 'MiniLM-384D'
            else:
                winner = 'mpnet-768D' if m1_val < m2_val else 'MiniLM-384D'
            
            if metric_key == 'response_time_sec':
                print(f"| {metric_label:20} | {m1_val:10.3f} | {m2_val:11.3f} | {winner:10} |")
            else:
                print(f"| {metric_label:20} | {m1_val:10.3f} | {m2_val:11.3f} | {winner:10} |")
        
        # By query type
        print("\n📊 BY QUERY TYPE:")
        query_types = set(r['query_type'] for r in self.results)
        
        for qtype in sorted(query_types):
            print(f"\n{qtype.upper()}:")
            m1_type = [r for r in model1_results if r['query_type'] == qtype]
            m2_type = [r for r in model2_results if r['query_type'] == qtype]
            
            if m1_type and m2_type:
                print(f"  F1 Score:    mpnet={calc_avg(m1_type, 'f1_score'):.3f}, MiniLM={calc_avg(m2_type, 'f1_score'):.3f}")
                print(f"  Similarity:  mpnet={calc_avg(m1_type, 'avg_similarity'):.3f}, MiniLM={calc_avg(m2_type, 'avg_similarity'):.3f}")
                print(f"  Time:        mpnet={calc_avg(m1_type, 'response_time_sec'):.3f}s, MiniLM={calc_avg(m2_type, 'response_time_sec'):.3f}s")
        
        # Similarity score distribution
        print("\n📊 SIMILARITY SCORE DISTRIBUTION:")
        print("\n| Model | Max | Avg | Min | Range |")
        print("|-------|-----|-----|-----|-------|")
        
        for model_name in ['all-mpnet-base-v2', 'all-MiniLM-L6-v2']:
            model_results = [r for r in self.results if r['model'] == model_name]
            max_sim = max(r['max_similarity'] for r in model_results)
            avg_sim = calc_avg(model_results, 'avg_similarity')
            min_sim = min(r['min_similarity'] for r in model_results)
            range_sim = max_sim - min_sim
            
            short_name = 'mpnet-768D' if '768' in model_name or 'mpnet' in model_name else 'MiniLM-384D'
            print(f"| {short_name:13} | {max_sim:.3f} | {avg_sim:.3f} | {min_sim:.3f} | {range_sim:.3f} |")
        
        # Recommendations
        print("\n" + "="*80)
        print("RECOMMENDATIONS")
        print("="*80)
        
        m1_f1 = calc_avg(model1_results, 'f1_score')
        m2_f1 = calc_avg(model2_results, 'f1_score')
        m1_time = calc_avg(model1_results, 'response_time_sec')
        m2_time = calc_avg(model2_results, 'response_time_sec')
        
        print(f"\n🏆 Best Overall F1 Score: {'mpnet-768D' if m1_f1 > m2_f1 else 'MiniLM-384D'} ({max(m1_f1, m2_f1):.3f})")
        print(f"⚡ Fastest: {'mpnet-768D' if m1_time < m2_time else 'MiniLM-384D'} ({min(m1_time, m2_time):.3f}s)")
        print(f"\n📈 F1 Score Difference: {abs(m1_f1 - m2_f1):.3f} ({abs(m1_f1 - m2_f1) / max(m1_f1, m2_f1) * 100:.1f}%)")
        print(f"⏱️  Time Difference: {abs(m1_time - m2_time):.3f}s ({abs(m1_time - m2_time) / max(m1_time, m2_time) * 100:.1f}%)")


def main():
    """Run embedding model comparison."""
    comparator = EmbeddingModelComparator()
    
    # Run comparison
    comparator.run_comparison()
    
    # Save results
    results_file = comparator.save_results()
    
    # Generate summary
    comparator.generate_summary()
    
    print("\n" + "="*80)
    print("✅ COMPARISON COMPLETE")
    print("="*80)
    print(f"\n📁 Results: {results_file}")
    print("\n💡 Use results for embedding model selection in production")


if __name__ == "__main__":
    main()
