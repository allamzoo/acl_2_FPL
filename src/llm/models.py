"""
LLM Models Module

Manages different LLM integrations for comparison.
Supports 3 free models: Llama 3.1 8B, Mixtral 8x7B, Gemma 7B
Uses Groq API (fast & free), HuggingFace, and OpenRouter as backends.
"""

import os
import requests
import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class BaseLLM(ABC):
    """Abstract base class for LLM integrations."""
    
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        self.model_name = model_name
        self.api_key = api_key
        self.total_tokens = 0
        self.total_cost = 0.0
        
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.3) -> Dict[str, Any]:
        """
        Generate response from LLM.
        
        Args:
            prompt: Formatted prompt with persona, context, task
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature (0.0-1.0)
            
        Returns:
            Dict with 'response', 'model', 'tokens', 'cost'
        """
        pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            'model': self.model_name,
            'total_tokens': self.total_tokens,
            'total_cost': self.total_cost
        }


class HuggingFaceLLM(BaseLLM):
    """
    HuggingFace Inference API integration.
    Free tier available for testing.
    """
    
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        super().__init__(model_name, api_key)
        self.api_url = f"https://api-inference.huggingface.co/models/{model_name}"
        
        # Get API key from parameter or environment
        if not self.api_key:
            self.api_key = os.getenv('HUGGINGFACE_API_KEY')
            
        if not self.api_key:
            logger.warning("No HuggingFace API key found. Set HUGGINGFACE_API_KEY env variable.")
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.3) -> Dict[str, Any]:
        """Generate response using HuggingFace Inference API."""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.95,
                "return_full_text": False
            }
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract generated text
            if isinstance(result, list) and len(result) > 0:
                generated_text = result[0].get('generated_text', '')
            else:
                generated_text = result.get('generated_text', '')
            
            # Estimate tokens (rough approximation)
            prompt_tokens = len(prompt) // 4
            completion_tokens = len(generated_text) // 4
            total_tokens = prompt_tokens + completion_tokens
            
            self.total_tokens += total_tokens
            # HuggingFace free tier - no cost
            
            return {
                'response': generated_text.strip(),
                'model': self.model_name,
                'tokens': total_tokens,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'cost': 0.0,  # Free
                'backend': 'HuggingFace'
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"HuggingFace API error: {e}")
            return {
                'response': f"Error: {str(e)}",
                'model': self.model_name,
                'tokens': 0,
                'cost': 0.0,
                'error': str(e)
            }


class OpenRouterLLM(BaseLLM):
    """
    OpenRouter API integration.
    Provides access to many free models.
    """
    
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        super().__init__(model_name, api_key)
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
        
        # Get API key from parameter or environment
        if not self.api_key:
            self.api_key = os.getenv('OPENROUTER_API_KEY')
            
        if not self.api_key:
            logger.warning("No OpenRouter API key found. Set OPENROUTER_API_KEY env variable.")
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.3) -> Dict[str, Any]:
        """Generate response using OpenRouter API."""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/allamzoo/acl_2_FPL",
            "X-Title": "FPL Graph-RAG"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.95
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract response
            generated_text = result['choices'][0]['message']['content']
            
            # Get token usage
            usage = result.get('usage', {})
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            total_tokens = usage.get('total_tokens', prompt_tokens + completion_tokens)
            
            self.total_tokens += total_tokens
            
            # Get cost (many models are free on OpenRouter)
            cost = result.get('usage', {}).get('total_cost', 0.0)
            self.total_cost += cost
            
            return {
                'response': generated_text.strip(),
                'model': self.model_name,
                'tokens': total_tokens,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'cost': cost,
                'backend': 'OpenRouter'
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API error: {e}")
            return {
                'response': f"Error: {str(e)}",
                'model': self.model_name,
                'tokens': 0,
                'cost': 0.0,
                'error': str(e)
            }


class GroqLLM(BaseLLM):
    """
    Groq API integration.
    Very fast inference with generous free tier.
    """
    
    def __init__(self, model_name: str, api_key: Optional[str] = None):
        super().__init__(model_name, api_key)
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        
        # Get API key from parameter or environment
        if not self.api_key:
            self.api_key = os.getenv('GROQ_API_KEY')
            
        if not self.api_key:
            logger.warning("No Groq API key found. Set GROQ_API_KEY env variable.")
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.3) -> Dict[str, Any]:
        """Generate response using Groq API."""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": 0.95
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Extract response
            generated_text = result['choices'][0]['message']['content']
            
            # Get token usage
            usage = result.get('usage', {})
            prompt_tokens = usage.get('prompt_tokens', 0)
            completion_tokens = usage.get('completion_tokens', 0)
            total_tokens = usage.get('total_tokens', prompt_tokens + completion_tokens)
            
            self.total_tokens += total_tokens
            # Groq is free
            self.total_cost += 0.0
            
            return {
                'response': generated_text.strip(),
                'model': self.model_name,
                'tokens': total_tokens,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'cost': 0.0,
                'backend': 'Groq'
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Groq API error: {e}")
            return {
                'response': f"Error: {str(e)}",
                'model': self.model_name,
                'tokens': 0,
                'cost': 0.0,
                'error': str(e)
            }


class LLMManager:
    """
    Manages multiple LLM models for comparison.
    Supports 3 free models: Mistral 7B, Llama 3 8B, Gemma 7B.
    """
    
    # Model configurations - Using Groq free models
    MODELS = {
        # 1. Llama 4 Maverick (Meta - Latest Llama 4, excellent instruction following)
        'llama-4-maverick': {
            'huggingface': 'meta-llama/Meta-Llama-3-8B-Instruct',
            'openrouter': 'meta-llama/llama-3.1-8b-instruct:free',
            'groq': 'meta-llama/llama-4-maverick-17b-128e-instruct',
            'preferred_backend': 'groq',
            'description': 'Llama 4 Maverick 17B - Latest Meta model with 128K context',
            'strengths': ['instruction-following', 'reasoning', 'long-context']
        },
        
        # 2. Qwen 3 32B (Alibaba - Powerful multilingual model)
        'qwen-3-32b': {
            'huggingface': 'Qwen/Qwen2.5-7B-Instruct',
            'openrouter': 'qwen/qwen-2.5-7b-instruct:free',
            'groq': 'qwen/qwen3-32b',
            'preferred_backend': 'groq',
            'description': 'Qwen 3 32B - Powerful reasoning and analysis',
            'strengths': ['reasoning', 'analysis', 'multilingual']
        },
        
        # 3. GPT OSS 20B (OpenAI - Open source GPT model)
        'gpt-oss-20b': {
            'huggingface': 'mistralai/Mistral-7B-Instruct-v0.3',
            'openrouter': 'mistralai/mistral-7b-instruct:free',
            'groq': 'openai/gpt-oss-20b',
            'preferred_backend': 'groq',
            'description': 'GPT OSS 20B - OpenAI open source model',
            'strengths': ['structured-output', 'instruction-following', 'accuracy']
        }
    }
    
    def __init__(self, backend: str = 'hybrid'):
        """
        Initialize LLM Manager.
        
        Args:
            backend: 'hybrid' (default - uses preferred backend per model),
                     'huggingface', 'groq', or 'openrouter' (forces all models to one backend)
        """
        self.backend = backend.lower()
        self.models = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize all three models."""
        for model_key, config in self.MODELS.items():
            # Determine which backend to use for this model
            if self.backend == 'hybrid':
                # Use the preferred backend specified in config
                backend_to_use = config.get('preferred_backend', 'huggingface')
            else:
                # Force all models to use the same backend
                backend_to_use = self.backend
            
            # Initialize model with appropriate backend
            if backend_to_use == 'huggingface':
                model_name = config['huggingface']
                self.models[model_key] = HuggingFaceLLM(model_name)
                logger.info(f"Initialized {model_key} on HuggingFace: {config['description']}")
            elif backend_to_use == 'groq':
                model_name = config.get('groq')
                if not model_name:
                    logger.warning(f"Model {model_key} not available on Groq")
                    continue
                self.models[model_key] = GroqLLM(model_name)
                logger.info(f"Initialized {model_key} on Groq: {config['description']}")
            elif backend_to_use == 'openrouter':
                model_name = config.get('openrouter')
                if not model_name:
                    logger.warning(f"Model {model_key} not available on OpenRouter")
                    continue
                self.models[model_key] = OpenRouterLLM(model_name)
                logger.info(f"Initialized {model_key} on OpenRouter: {config['description']}")
            else:
                raise ValueError(f"Unknown backend: {backend_to_use}. Use 'huggingface', 'groq', or 'openrouter'")
    
    def generate(
        self,
        prompt: str,
        model: str = 'gemma-2-2b',
        max_tokens: int = 512,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Generate response using specified model.
        
        Args:
            prompt: Formatted prompt (PERSONA + CONTEXT + TASK)
            model: Model key ('gemma-2-2b', 'llama-3-8b', 'mistral-7b')
            max_tokens: Max response tokens
            temperature: Sampling temperature (lower = more deterministic)
            
        Returns:
            Response dict with 'response', 'model', 'tokens', 'cost'
        """
        if model not in self.models:
            raise ValueError(f"Unknown model: {model}. Choose from: {list(self.models.keys())}")
        
        llm = self.models[model]
        result = llm.generate(prompt, max_tokens, temperature)
        
        # Add model metadata
        result['model_key'] = model
        result['model_info'] = self.MODELS[model]
        
        return result
    
    def generate_all(
        self,
        prompt: str,
        max_tokens: int = 512,
        temperature: float = 0.3
    ) -> Dict[str, Dict[str, Any]]:
        """
        Generate responses from ALL three models for comparison.
        
        Args:
            prompt: Formatted prompt
            max_tokens: Max response tokens
            temperature: Sampling temperature
            
        Returns:
            Dict mapping model_key -> response_dict
        """
        results = {}
        
        for model_key in self.models.keys():
            logger.info(f"Generating response from {model_key}...")
            results[model_key] = self.generate(prompt, model_key, max_tokens, temperature)
        
        return results
    
    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get usage statistics for all models."""
        return {
            model_key: llm.get_stats()
            for model_key, llm in self.models.items()
        }
    
    def list_models(self) -> List[Dict[str, Any]]:
        """List available models with descriptions."""
        return [
            {
                'key': model_key,
                'name': config[self.backend],
                'description': config['description'],
                'strengths': config['strengths'],
                'backend': self.backend
            }
            for model_key, config in self.MODELS.items()
        ]


def create_llm_manager(backend: str = 'groq') -> LLMManager:
    """
    Factory function to create LLM Manager.
    
    Args:
        backend: 'groq' (default, fast & free), 'huggingface', or 'openrouter'
        
    Returns:
        Initialized LLMManager
    """
    return LLMManager(backend)

