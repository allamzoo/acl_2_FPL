"""
Comprehensive LLM Evaluation Framework - Quantitative & Qualitative Analysis

Evaluates 3 LLM models (Llama 4 Maverick, Qwen 3 32B, GPT OSS 20B) with:

QUANTITATIVE METRICS:
- Response time, token usage, cost estimation
- Retrieval quality, intent detection accuracy

QUALITATIVE METRICS (Human Evaluation):
- Answer correctness, relevance, completeness
- Naturalness, factual accuracy

Test cases cover: team queries, comparisons, value queries, squad building
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.llm.generator import FPLAnswerGenerator
import time
import json
from typing import Dict, List, Any
from datetime import datetime

class ComprehensiveLLMEvaluator:
    """Framework for quantitative and qualitative LLM evaluation."""
    
    def __init__(self):
        self.generator = FPLAnswerGenerator()
        self.models = [
            ("llama-4-maverick", "Llama 4 Maverick"),
            ("qwen-3-32b", "Qwen 3 32B"),
            ("gpt-oss-20b", "GPT OSS 20B")
        ]
        self.retrieval_modes = [
            ("baseline", "Baseline Only"),
            ("baseline+embedding1", "Baseline + mpnet"),
            ("baseline+embedding2", "Baseline + MiniLM")
        ]
        
        # Groq pricing (per million tokens)
        self.pricing = {
            "llama-4-maverick": {"input": 0.40, "output": 0.40},
            "qwen-3-32b": {"input": 0.50, "output": 0.50},
            "gpt-oss-20b": {"input": 0.15, "output": 0.15}
        }
        
        self.results = []
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens (1 token ≈ 4 characters)."""
        return len(text) // 4
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost in USD."""
        pricing = self.pricing.get(model, {"input": 0.40, "output": 0.40})
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost
    
    def run_test(self, query: str, season: str, mode: str, model: str, 
                 expected: str = "", query_type: str = "") -> Dict[str, Any]:
        """Run single test and collect metrics."""
        print(f"   • {model:20} | {mode:20}", end=" ", flush=True)
        
        start_time = time.time()
        try:
            result = self.generator.answer(
                query=query,
                season=season,
                model=model,
                retrieval_mode=mode,
                max_tokens=1024
            )
            elapsed = time.time() - start_time
            
            answer = result.get('answer', '')
            context = result.get('context', {})
            
            # Extract metrics
            players = context.get('unified_players', [])
            intent = context.get('intent', 'N/A')
            confidence = context.get('intent_confidence', 0)
            
            # Token estimation
            prompt_text = query + str(context.get('baseline_results', {}))[:500]
            input_tokens = self.estimate_tokens(prompt_text)
            output_tokens = self.estimate_tokens(answer)
            cost = self.calculate_cost(model, input_tokens, output_tokens)
            
            top_players = [p.get('player_name', 'Unknown') for p in players[:3]]
            
            print(f"✓ {elapsed:.2f}s | {output_tokens}tok | ${cost:.6f}")
            
            return {
                'query': query,
                'query_type': query_type,
                'season': season,
                'model': model,
                'retrieval_mode': mode,
                'timestamp': datetime.now().isoformat(),
                
                # Quantitative
                'response_time_sec': round(elapsed, 2),
                'response_length_chars': len(answer),
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'total_tokens': input_tokens + output_tokens,
                'cost_usd': round(cost, 6),
                'players_retrieved': len(players),
                'intent': str(intent),
                'confidence': round(confidence, 2),
                'top_players': top_players,
                
                'answer': answer,
                'expected': expected,
                
                # Qualitative (manual scoring)
                'correctness_score': None,
                'relevance_score': None,
                'completeness_score': None,
                'naturalness_score': None,
                'accuracy_score': None,
                'notes': ''
            }
            
        except Exception as e:
            print(f"✗ Error: {str(e)[:50]}")
            return {'query': query, 'model': model, 'mode': mode, 'error': str(e)}
    
    def run_evaluation(self):
        """Run complete evaluation."""
        
        test_cases = [
            {
                'query': 'best arsenal midfielders',
                'season': '2021-22',
                'type': 'team_position',
                'expected': 'Bukayo Saka (179pts), Martin Ødegaard (131pts), Smith Rowe (125pts)'
            },
            {
                'query': 'top liverpool defenders season 2022',
                'season': '2022-23',
                'type': 'top_team_position',
                'expected': 'TAA (156pts), Van Dijk (127pts), Robertson (121pts)'
            },
            {
                'query': 'who are the top scorers in 2021-22',
                'season': '2021-22',
                'type': 'aggregate_scorers',
                'expected': 'Salah (23G), Son (23G), Ronaldo (18G)'
            },
            {
                'query': 'compare Mohamed Salah and Harry Kane in 2021-22',
                'season': '2021-22',
                'type': 'comparison',
                'expected': 'Salah: 265pts, 23G, 14A | Kane: 221pts, 17G, 9A'
            },
            {
                'query': 'best value midfielders under 7 million',
                'season': '2021-22',
                'type': 'value_query',
                'expected': 'High points-per-million ratio players'
            }
        ]
        
        print("\n" + "="*80)
        print("COMPREHENSIVE LLM EVALUATION - QUANTITATIVE & QUALITATIVE")
        print("="*80)
        print(f"\n📋 Configuration:")
        print(f"   Test Cases: {len(test_cases)}")
        print(f"   Models: {len(self.models)}")
        print(f"   Retrieval Modes: {len(self.retrieval_modes)}")
        print(f"   Total Tests: {len(test_cases) * len(self.models) * len(self.retrieval_modes)}")
        print("\n" + "="*80)
        
        for i, tc in enumerate(test_cases, 1):
            print(f"\n{'#'*80}")
            print(f"# TEST {i}/{len(test_cases)}: {tc['type'].upper()}")
            print(f"# Query: '{tc['query']}'")
            print(f"# Expected: {tc['expected']}")
            print(f"{'#'*80}\n")
            
            for mode_id, mode_name in self.retrieval_modes:
                print(f"\n🔍 {mode_name}")
                
                for model_id, model_name in self.models:
                    metrics = self.run_test(
                        query=tc['query'],
                        season=tc['season'],
                        mode=mode_id,
                        model=model_id,
                        expected=tc['expected'],
                        query_type=tc['type']
                    )
                    
                    self.results.append(metrics)
        
        self.generator.close()
    
    def save_results(self, filename: str = "evaluation_results.json"):
        """Save to JSON."""
        path = os.path.join(os.path.dirname(__file__), filename)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Results saved: {path}")
        return path
    
    def quantitative_summary(self):
        """Generate quantitative summary."""
        print("\n" + "="*80)
        print("QUANTITATIVE METRICS SUMMARY")
        print("="*80)
        
        # By model
        print("\n📊 BY MODEL:")
        print("\n| Metric | Llama 4 Maverick | Qwen 3 32B | GPT OSS 20B |")
        print("|--------|------------------|------------|-------------|")
        
        model_names = [name for _, name in self.models]
        metrics_to_show = [
            ('avg_response_time', 'Avg Time (s)', lambda x: f"{x:.2f}s"),
            ('avg_output_tokens', 'Avg Tokens', lambda x: f"{x:.0f}"),
            ('total_cost', 'Total Cost', lambda x: f"${x:.6f}"),
            ('avg_length', 'Avg Length', lambda x: f"{x:.0f} chars"),
        ]
        
        for metric_key, metric_label, formatter in metrics_to_show:
            row = f"| {metric_label:30} |"
            
            for model_id, model_name in self.models:
                model_results = [r for r in self.results if r.get('model') == model_id and 'error' not in r]
                
                if not model_results:
                    row += f" N/A |"
                    continue
                
                if metric_key == 'avg_response_time':
                    value = sum(r['response_time_sec'] for r in model_results) / len(model_results)
                elif metric_key == 'avg_output_tokens':
                    value = sum(r['output_tokens'] for r in model_results) / len(model_results)
                elif metric_key == 'total_cost':
                    value = sum(r['cost_usd'] for r in model_results)
                elif metric_key == 'avg_length':
                    value = sum(r['response_length_chars'] for r in model_results) / len(model_results)
                
                row += f" {formatter(value):^16} |"
            
            print(row)
        
        # By retrieval mode
        print("\n📊 BY RETRIEVAL MODE:")
        print("\n| Mode | Avg Time | Avg Players | Tests |")
        print("|------|----------|-------------|-------|")
        
        for mode_id, mode_name in self.retrieval_modes:
            mode_results = [r for r in self.results if r.get('retrieval_mode') == mode_id and 'error' not in r]
            if mode_results:
                avg_time = sum(r['response_time_sec'] for r in mode_results) / len(mode_results)
                avg_players = sum(r['players_retrieved'] for r in mode_results) / len(mode_results)
                print(f"| {mode_name:20} | {avg_time:8.2f}s | {avg_players:11.1f} | {len(mode_results):5} |")
        
        # By query type
        print("\n📊 BY QUERY TYPE:")
        print("\n| Query Type | Tests | Avg Time | Avg Tokens |")
        print("|------------|-------|----------|------------|")
        
        query_types = set(r.get('query_type', 'unknown') for r in self.results if 'error' not in r)
        for qtype in sorted(query_types):
            type_results = [r for r in self.results if r.get('query_type') == qtype and 'error' not in r]
            if type_results:
                avg_time = sum(r['response_time_sec'] for r in type_results) / len(type_results)
                avg_tokens = sum(r['output_tokens'] for r in type_results) / len(type_results)
                print(f"| {qtype:22} | {len(type_results):5} | {avg_time:8.2f}s | {avg_tokens:10.0f} |")
    
    def qualitative_guide(self):
        """Print qualitative evaluation guide."""
        print("\n" + "="*80)
        print("QUALITATIVE EVALUATION GUIDE")
        print("="*80)
        print("""
Please manually evaluate each response using the JSON file:

SCORING SCALE (0-5):
  5 = Excellent - Perfect or near-perfect
  4 = Good - Minor issues only
  3 = Adequate - Acceptable but noticeable issues
  2 = Poor - Significant problems
  1 = Very Poor - Major issues
  0 = Unacceptable - Completely wrong/unusable

CRITERIA:
  
1. CORRECTNESS (correctness_score):
   - Are the facts and numbers accurate?
   - Are player names spelled correctly?
   - Are statistics correct?

2. RELEVANCE (relevance_score):
   - Does it answer the specific question?
   - Is information on-topic?
   - No unnecessary tangents?

3. COMPLETENESS (completeness_score):
   - Provides enough detail?
   - Answers all parts of question?
   - Includes key statistics?

4. NATURALNESS (naturalness_score):
   - Well-written and readable?
   - Natural language flow?
   - Proper formatting?

5. FACTUAL ACCURACY (accuracy_score):
   - Player-team associations correct?
   - Seasons and dates accurate?
   - Rankings and comparisons valid?

Add your scores to the JSON file, then run the analysis script.
""")


def main():
    """Run comprehensive evaluation."""
    evaluator = ComprehensiveLLMEvaluator()
    
    # Run tests
    evaluator.run_evaluation()
    
    # Save results
    results_file = evaluator.save_results()
    
    # Quantitative summary
    evaluator.quantitative_summary()
    
    # Qualitative guide
    evaluator.qualitative_guide()
    
    print("\n" + "="*80)
    print("✅ EVALUATION COMPLETE")
    print("="*80)
    print(f"\n📊 Tests run: {len(evaluator.results)}")
    print(f"📁 Results: {results_file}")
    print("\n💡 Next Steps:")
    print("   1. Review quantitative metrics above")
    print("   2. Manually score responses in JSON file")
    print("   3. Document findings in comparison report")
    

if __name__ == "__main__":
    main()
