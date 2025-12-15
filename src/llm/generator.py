"""
LLM Response Generator Module

Combines retrieval results with structured prompts and generates answers.
Supports 3 models: Gemma 2 2B, Llama 3 8B, Mistral 7B (via HuggingFace API).
"""

import logging
from typing import Dict, Any, Optional, List
from src.retrieval.hybrid_retriever import HybridRetriever
from src.llm.prompts import build_fpl_prompt
from src.llm.models import LLMManager, create_llm_manager

logger = logging.getLogger(__name__)


def strip_think_tags(response: str) -> str:
    """
    Remove <think> tags and reasoning from Qwen model responses.
    Qwen models output chain-of-thought reasoning in <think>...</think> tags.
    This function extracts only the final answer after the thinking process.
    
    Args:
        response: Raw model response potentially containing <think> tags
        
    Returns:
        Clean answer without thinking process
    """
    import re
    
    # First, remove all complete <think>...</think> blocks
    cleaned = re.sub(r'<think>.*?</think>', '', response, flags=re.DOTALL | re.IGNORECASE)
    
    # Then remove any remaining incomplete/unclosed <think> tags
    # This handles truncated responses where </think> never appeared
    cleaned = re.sub(r'<think>.*$', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
    
    # Also remove orphaned </think> tags (in case of split content)
    cleaned = re.sub(r'</think>', '', cleaned, flags=re.IGNORECASE)
    
    # Clean up extra whitespace and empty lines
    cleaned = '\n'.join(line for line in cleaned.split('\n') if line.strip())
    cleaned = cleaned.strip()
    
    # If nothing meaningful left after removing think tags, 
    # return a helpful summary instead of empty string
    if not cleaned or len(cleaned) < 10:
        # Check if original contained thinking but no conclusion
        if '<think>' in response.lower():
            # Extract key points from the thinking if possible
            # Look for conclusions, recommendations, or final statements
            lines = response.split('\n')
            # Get last few non-empty lines from thinking as a summary
            meaningful_lines = [l.strip() for l in lines if l.strip() and not l.strip().startswith('<')]
            if meaningful_lines:
                # Return last paragraph as implied conclusion
                last_paragraph = '\n'.join(meaningful_lines[-5:])
                if len(last_paragraph) > 50:
                    return f"[Answer extracted from reasoning]\n\n{last_paragraph}"
            
            return "[Model provided only internal reasoning without a final answer]"
        return response
    
    return cleaned


class FPLAnswerGenerator:
    """
    End-to-end FPL question answering with Graph-RAG.
    
    Pipeline:
    1. User question → Hybrid Retriever (Cypher + Embeddings)
    2. Retrieved context → Structured Prompt (PERSONA + CONTEXT + TASK)
    3. Prompt → LLM (Gemma/Llama/Mistral via HuggingFace)
    4. LLM response → User
    """
    
    def __init__(
        self,
        embedding_model: str = "all-mpnet-base-v2",
        llm_backend: str = "hybrid",
        default_llm: str = "llama-4-maverick"
    ):
        """
        Initialize answer generator.
        
        Args:
            embedding_model: Model for semantic retrieval
            llm_backend: 'hybrid' (default - uses Groq for all 3 models),
                        'huggingface', 'groq', or 'openrouter'
            default_llm: Default model ('llama-4-maverick', 'qwen-3-32b', 'gpt-oss-20b')
        """
        # Initialize retriever
        self.retriever = HybridRetriever(
            embedding_model=embedding_model,
            use_hybrid_embeddings=True
        )
        
        # Initialize LLM manager
        self.llm_manager = create_llm_manager(backend=llm_backend)
        self.default_llm = default_llm
        
        logger.info(f"FPL Answer Generator initialized (LLM backend: {llm_backend})")
    
    def answer(
        self,
        query: str,
        season: str = "2022-23",
        model: Optional[str] = None,
        task_type: str = "answer",
        max_tokens: int = 512,
        temperature: float = 0.3,
        retrieval_mode: str = "baseline+embedding1"
    ) -> Dict[str, Any]:
        """
        Answer FPL question using Graph-RAG pipeline.
        
        Args:
            query: User's question
            season: FPL season
            model: LLM model ('llama-4-maverick', 'qwen-3-32b', 'gpt-oss-20b')
            task_type: Prompt task type ('answer', 'recommend', 'compare', 'explain')
            max_tokens: Max response tokens
            temperature: Sampling temperature
            retrieval_mode: Retrieval strategy:
                - 'baseline' - Baseline only (no embeddings, no merge)
                - 'baseline+embedding1' - Baseline + Embedding Model 1 (merged)
                - 'baseline+embedding2' - Baseline + Embedding Model 2 (merged)
            
        Returns:
            Dict with 'query', 'answer', 'context', 'model', 'tokens', 'cost'
        """
        if model is None:
            model = self.default_llm
        
        logger.info(f"Processing query: '{query}' (season: {season}, model: {model}, mode: {retrieval_mode})")
        
        # Step 1: Retrieve context from Knowledge Graph with selected mode
        logger.info(f"Step 1: Retrieving context (mode: {retrieval_mode})...")
        context = self.retriever.retrieve(query, season, retrieval_mode=retrieval_mode)
        
        num_players = len(context.get('unified_players', []))
        logger.info(f"✓ Retrieved {num_players} relevant players")
        
        # Step 2: Build structured prompt
        logger.info("Step 2: Building structured prompt (PERSONA + CONTEXT + TASK)...")
        prompt = build_fpl_prompt(query, context, task=task_type)
        prompt_length = len(prompt)
        logger.info(f"✓ Prompt built ({prompt_length} chars)")
        
        # Step 3: Generate answer with LLM
        logger.info(f"Step 3: Generating answer with {model}...")
        
        # Increase token limit for Qwen models (they use think tags which consume tokens)
        adjusted_max_tokens = max_tokens
        if 'qwen' in model.lower():
            adjusted_max_tokens = max(1024, max_tokens * 2)
            logger.info(f"Increased max_tokens to {adjusted_max_tokens} for Qwen model")
        
        llm_response = self.llm_manager.generate(
            prompt=prompt,
            model=model,
            max_tokens=adjusted_max_tokens,
            temperature=temperature
        )
        
        logger.info(f"✓ Answer generated ({llm_response['tokens']} tokens)")
        
        # Post-process response: remove <think> tags from all Qwen models
        raw_response = llm_response['response']
        
        # Check both the model parameter and the actual model ID used
        is_qwen = 'qwen' in model.lower() or 'qwen' in str(llm_response.get('model', '')).lower()
        clean_response = strip_think_tags(raw_response) if is_qwen else raw_response
        
        if is_qwen and clean_response != raw_response:
            logger.info(f"✓ Removed <think> tags from Qwen response ({len(raw_response) - len(clean_response)} chars removed)")
        
        # Combine everything into final result
        result = {
            'query': query,
            'season': season,
            'answer': clean_response,  # Use cleaned response
            'raw_answer': raw_response,  # Keep original with thinking for debugging
            'context': {
                'num_players': num_players,
                'unified_players': context.get('unified_players', [])[:10],  # Top 10
                'baseline_results': context.get('baseline_results', {}),
                'semantic_results': context.get('semantic_results', {})
            },
            'model': model,
            'model_info': llm_response.get('model_info', {}),
            'tokens': llm_response['tokens'],
            'prompt_tokens': llm_response.get('prompt_tokens', 0),
            'completion_tokens': llm_response.get('completion_tokens', 0),
            'cost': llm_response.get('cost', 0.0),
            'backend': llm_response.get('backend', 'unknown'),
            'task_type': task_type,
            'prompt_length': prompt_length
        }
        
        return result
    
    def compare_models(
        self,
        query: str,
        season: str = "2022-23",
        task_type: str = "answer",
        max_tokens: int = 512,
        temperature: float = 0.3
    ) -> Dict[str, Dict[str, Any]]:
        """
        Answer same question with ALL three models for comparison.
        
        Args:
            query: User's question
            season: FPL season
            task_type: Prompt task type
            max_tokens: Max response tokens
            temperature: Sampling temperature
            
        Returns:
            Dict mapping model_key -> result_dict
        """
        logger.info(f"Comparing all 3 models for query: '{query}'")
        
        # Step 1: Retrieve context (once, shared by all models)
        logger.info("Retrieving context from Knowledge Graph...")
        context = self.retriever.retrieve(query, season)
        num_players = len(context.get('unified_players', []))
        logger.info(f"✓ Retrieved {num_players} relevant players")
        
        # Step 2: Build prompt (once, shared by all models)
        logger.info("Building structured prompt...")
        prompt = build_fpl_prompt(query, context, task=task_type)
        prompt_length = len(prompt)
        logger.info(f"✓ Prompt built ({prompt_length} chars)")
        
        # Step 3: Generate answers from all models
        logger.info("Generating answers from all 3 models...")
        llm_responses = self.llm_manager.generate_all(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Combine results
        results = {}
        for model_key, llm_response in llm_responses.items():
            # Post-process: remove <think> tags from Qwen models
            raw_response = llm_response['response']
            clean_response = strip_think_tags(raw_response) if 'qwen' in model_key.lower() else raw_response
            
            results[model_key] = {
                'query': query,
                'season': season,
                'answer': clean_response,
                'raw_answer': raw_response if clean_response != raw_response else None,
                'model': model_key,
                'model_info': llm_response.get('model_info', {}),
                'tokens': llm_response['tokens'],
                'prompt_tokens': llm_response.get('prompt_tokens', 0),
                'completion_tokens': llm_response.get('completion_tokens', 0),
                'cost': llm_response.get('cost', 0.0),
                'backend': llm_response.get('backend', 'unknown'),
                'error': llm_response.get('error')
            }
            logger.info(f"✓ {model_key}: {results[model_key]['tokens']} tokens")
        
        # Add shared context info
        comparison = {
            'query': query,
            'season': season,
            'context': {
                'num_players': num_players,
                'unified_players': context.get('unified_players', [])[:10]
            },
            'prompt_length': prompt_length,
            'task_type': task_type,
            'models': results
        }
        
        return comparison
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """List all available LLM models."""
        return self.llm_manager.list_models()
    
    def get_model_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get usage statistics for all models."""
        return self.llm_manager.get_all_stats()
    
    def close(self):
        """Close connections."""
        self.retriever.close()
        logger.info("Answer generator closed")


def create_answer_generator(
    embedding_model: str = "all-mpnet-base-v2",
    llm_backend: str = "openrouter",
    default_llm: str = "mistral-7b"
) -> FPLAnswerGenerator:
    """
    Factory function to create answer generator.
    
    Args:
        embedding_model: Model for semantic retrieval
        llm_backend: 'huggingface' or 'openrouter'
        default_llm: Default LLM ('mistral-7b', 'llama-3-8b', 'gemma-7b')
        
    Returns:
        Initialized FPLAnswerGenerator
    """
    return FPLAnswerGenerator(embedding_model, llm_backend, default_llm)

