"""
Intent Classifier Module

Classifies user queries into different intents using LLM-based classification.
This routes queries to the appropriate retrieval strategy and Cypher query.
"""

from enum import Enum
from typing import Dict, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)


class Intent(Enum):
    """
    Available intents for FPL Graph-RAG system.
    Each intent maps to specific Cypher queries in the baseline retriever.
    """
    PLAYER_SEARCH = "player_search"  # Find specific player
    PLAYER_STATS = "player_stats"  # Get player statistics for a season
    TOP_SCORERS = "top_scorers"  # Top goal scorers by position
    TOP_ASSISTERS = "top_assisters"  # Top assist providers
    TEAM_ANALYSIS = "team_analysis"  # Get team players and performance
    GAMEWEEK_PERFORMERS = "gameweek_performers"  # Top performers in gameweek
    PLAYER_COMPARISON = "player_comparison"  # Compare multiple players
    HIGH_PERFORMERS = "high_performers"  # Players exceeding thresholds
    PLAYER_FORM = "player_form"  # Recent gameweek performance
    ICT_ANALYSIS = "ict_analysis"  # ICT index-based analysis
    UNKNOWN = "unknown"  # Unable to classify


class LLMIntentClassifier:
    """
    LLM-based intent classifier using local transformers.
    Uses zero-shot classification for accurate intent detection.
    """
    
    def __init__(self, model_name: str = "facebook/bart-large-mnli"):
        """
        Initialize the intent classifier with a zero-shot model.
        
        Args:
            model_name: HuggingFace model for zero-shot classification
        """
        try:
            from transformers import pipeline
            
            self.model_name = model_name
            logger.info(f"Loading zero-shot classifier: {model_name}")
            
            # Initialize zero-shot classification pipeline
            self.classifier = pipeline(
                "zero-shot-classification",
                model=model_name,
                device=-1  # Use CPU (change to 0 for GPU)
            )
            
            # Define candidate labels (intent descriptions)
            self.candidate_labels = [
                "finding a specific player by name",
                "getting player statistics for a season",
                "finding top goal scorers by position",
                "finding top assist providers",
                "analyzing team players and performance",
                "finding top performers in a gameweek",
                "comparing multiple players",
                "finding players exceeding performance thresholds",
                "analyzing recent player form",
                "finding players with best ICT scores"
            ]
            
            # Map labels to intents
            self.label_to_intent = {
                "finding a specific player by name": Intent.PLAYER_SEARCH,
                "getting player statistics for a season": Intent.PLAYER_STATS,
                "finding top goal scorers by position": Intent.TOP_SCORERS,
                "finding top assist providers": Intent.TOP_ASSISTERS,
                "analyzing team players and performance": Intent.TEAM_ANALYSIS,
                "finding top performers in a gameweek": Intent.GAMEWEEK_PERFORMERS,
                "comparing multiple players": Intent.PLAYER_COMPARISON,
                "finding players exceeding performance thresholds": Intent.HIGH_PERFORMERS,
                "analyzing recent player form": Intent.PLAYER_FORM,
                "finding players with best ICT scores": Intent.ICT_ANALYSIS
            }
            
            logger.info("LLM intent classifier initialized successfully")
            self.available = True
            
        except Exception as e:
            logger.warning(f"Failed to load LLM classifier: {str(e)}")
            logger.warning("Falling back to simple classifier")
            self.available = False
    
    def classify(self, query: str) -> Dict[str, Any]:
        """
        Classify user query using zero-shot classification.
        
        Args:
            query: User's natural language query
            
        Returns:
            Dictionary with intent, confidence, and reasoning
        """
        if not self.available:
            logger.warning("LLM classifier not available, use SimpleIntentClassifier instead")
            return {
                "intent": Intent.UNKNOWN,
                "confidence": 0.0,
                "reasoning": "LLM classifier not initialized",
                "query": query
            }
        
        try:
            # Perform zero-shot classification
            result = self.classifier(
                query,
                self.candidate_labels,
                multi_label=False
            )
            
            # Extract top prediction
            top_label = result['labels'][0]
            confidence = result['scores'][0]
            
            # Map to intent
            intent = self.label_to_intent.get(top_label, Intent.UNKNOWN)
            
            logger.info(f"Query classified as {intent.value} (confidence: {confidence:.2f})")
            
            return {
                "intent": intent,
                "confidence": confidence,
                "reasoning": f"Matched to: {top_label}",
                "query": query,
                "all_scores": dict(zip(result['labels'][:3], result['scores'][:3]))  # Top 3
            }
            
        except Exception as e:
            logger.error(f"Intent classification failed: {str(e)}")
            return {
                "intent": Intent.UNKNOWN,
                "confidence": 0.0,
                "reasoning": f"Classification failed: {str(e)}",
                "query": query
            }
    
    def get_query_mapping(self, intent: Intent) -> str:
        """
        Map intent to the corresponding retriever method name.
        
        Args:
            intent: Classified intent
            
        Returns:
            Method name in BaselineRetriever
        """
        mapping = {
            Intent.PLAYER_SEARCH: "find_player_by_name",
            Intent.PLAYER_STATS: "get_player_season_stats",
            Intent.TOP_SCORERS: "get_top_scorers",
            Intent.TOP_ASSISTERS: "get_top_assisters",
            Intent.TEAM_ANALYSIS: "get_team_players",
            Intent.GAMEWEEK_PERFORMERS: "get_gameweek_top_performers",
            Intent.PLAYER_COMPARISON: "compare_players",
            Intent.HIGH_PERFORMERS: "get_high_performers",
            Intent.PLAYER_FORM: "get_player_form",
            Intent.ICT_ANALYSIS: "get_top_ict_players",
        }
        
        return mapping.get(intent, "unknown")


# Lightweight fallback classifier (no dependencies)
class SimpleIntentClassifier:
    """
    Simple keyword-based fallback classifier.
    Used when LLM classification fails or for testing.
    Fast and reliable with no external dependencies.
    """
    
    def classify(self, query: str) -> Dict[str, Any]:
        """
        Classify using simple keyword matching.
        
        Args:
            query: User query
            
        Returns:
            Classification result
        """
        query_lower = query.lower().strip()
        
        # Simple keyword patterns (order matters - more specific first)
        
        # Quick check for common "top" queries
        if "top" in query_lower:
            # Check for scorers/goals
            if any(x in query_lower for x in ["scorer", "goal", "attack", "forward", "striker"]) and not any(x in query_lower for x in ["assist"]):
                return {
                    "intent": Intent.TOP_SCORERS,
                    "confidence": 0.95,
                    "reasoning": "Top + scorer/goal keywords detected",
                    "query": query
                }
            # Check for assisters
            if any(x in query_lower for x in ["assist", "playmaker", "creator"]):
                return {
                    "intent": Intent.TOP_ASSISTERS,
                    "confidence": 0.95,
                    "reasoning": "Top + assist keywords detected",
                    "query": query
                }
        
        # PLAYER_COMPARISON (check before stats)
        if any(phrase in query_lower for phrase in ["compare", " vs ", " versus ", "difference between"]):
            return {
                "intent": Intent.PLAYER_COMPARISON,
                "confidence": 0.85,
                "reasoning": "Comparison keywords detected",
                "query": query
            }
        
        # TOP_SCORERS
        if any(phrase in query_lower for phrase in [
            "topscorers", "top scorers", "top scorer", "topscorer",
            "most goals", "goal scorers", "goalscorers", "goal scorer",
            "best scorers", "leading scorers", "highest scorers",
            "who scored", "top goal", "highest goal", "goals leader",
            "who are the top", "top attackers", "best attackers"
        ]):
            return {
                "intent": Intent.TOP_SCORERS,
                "confidence": 0.9,
                "reasoning": "Top scorers keywords detected",
                "query": query
            }
        
        # TOP_ASSISTERS
        if any(phrase in query_lower for phrase in ["most assists", "top assist", "best playmaker", "assist leader"]):
            return {
                "intent": Intent.TOP_ASSISTERS,
                "confidence": 0.9,
                "reasoning": "Assist keywords detected",
                "query": query
            }
        
        # GAMEWEEK_PERFORMERS
        if any(phrase in query_lower for phrase in ["gameweek", " gw", "week "]):
            return {
                "intent": Intent.GAMEWEEK_PERFORMERS,
                "confidence": 0.85,
                "reasoning": "Gameweek keywords detected",
                "query": query
            }
        
        # PLAYER_FORM
        if any(phrase in query_lower for phrase in ["form", "recent", "last few", "last 5", "lately"]):
            return {
                "intent": Intent.PLAYER_FORM,
                "confidence": 0.8,
                "reasoning": "Form keywords detected",
                "query": query
            }
        
        # ICT_ANALYSIS
        if any(phrase in query_lower for phrase in ["ict", "influence", "creativity", "threat"]):
            return {
                "intent": Intent.ICT_ANALYSIS,
                "confidence": 0.9,
                "reasoning": "ICT keywords detected",
                "query": query
            }
        
        # HIGH_PERFORMERS (threshold-based)
        if any(phrase in query_lower for phrase in ["more than", "at least", "minimum", ">=", ">", "over "]):
            return {
                "intent": Intent.HIGH_PERFORMERS,
                "confidence": 0.75,
                "reasoning": "Threshold keywords detected",
                "query": query
            }
        
        # TEAM_ANALYSIS
        if any(phrase in query_lower for phrase in ["team", "club", "squad", "roster"]):
            return {
                "intent": Intent.TEAM_ANALYSIS,
                "confidence": 0.8,
                "reasoning": "Team keywords detected",
                "query": query
            }
        
        # PLAYER_STATS
        if any(phrase in query_lower for phrase in ["stats", "statistics", "performance", "season"]):
            return {
                "intent": Intent.PLAYER_STATS,
                "confidence": 0.75,
                "reasoning": "Stats keywords detected",
                "query": query
            }
        
        # PLAYER_SEARCH (most general)
        if any(phrase in query_lower for phrase in ["who is", "find player", "search for", "tell me about"]):
            return {
                "intent": Intent.PLAYER_SEARCH,
                "confidence": 0.8,
                "reasoning": "Search keywords detected",
                "query": query
            }
        
        # UNKNOWN
        return {
            "intent": Intent.UNKNOWN,
            "confidence": 0.3,
            "reasoning": "No clear pattern matched",
            "query": query
        }
    
    def get_query_mapping(self, intent: Intent) -> str:
        """Map intent to retriever method."""
        mapping = {
            Intent.PLAYER_SEARCH: "find_player_by_name",
            Intent.PLAYER_STATS: "get_player_season_stats",
            Intent.TOP_SCORERS: "get_top_scorers",
            Intent.TOP_ASSISTERS: "get_top_assisters",
            Intent.TEAM_ANALYSIS: "get_team_players",
            Intent.GAMEWEEK_PERFORMERS: "get_gameweek_top_performers",
            Intent.PLAYER_COMPARISON: "compare_players",
            Intent.HIGH_PERFORMERS: "get_high_performers",
            Intent.PLAYER_FORM: "get_player_form",
            Intent.ICT_ANALYSIS: "get_top_ict_players",
        }
        return mapping.get(intent, "unknown")


class HybridIntentClassifier:
    """
    Smart hybrid intent classifier combining rule-based logic with LLM intelligence.
    
    Strategy:
    1. Uses the SAME rule-based classification logic first
    2. If confidence is high (>= threshold), returns rule-based result immediately
    3. If uncertain or UNKNOWN, asks a smart LLM (Groq API) to classify with context
    4. LLM is given the rule-based attempt to make better decisions
    
    This is fast (rules first) but intelligent (LLM for hard cases).
    """
    
    def __init__(
        self, 
        confidence_threshold: float = 0.85,
        model_name: str = "llama-4-maverick"
    ):
        """
        Initialize smart hybrid classifier.
        
        Args:
            confidence_threshold: Minimum confidence to trust rule-based result
            model_name: Model key for LLM ('llama-4-maverick', 'qwen-3-32b', 'gpt-oss-20b')
        """
        # Use the existing rule-based classifier
        self.rule_classifier = SimpleIntentClassifier()
        self.confidence_threshold = confidence_threshold
        self.model_name = model_name
        
        # Try to initialize Groq LLM
        try:
            from src.llm.models import create_llm_manager
            self.llm_manager = create_llm_manager(backend='groq')
            self.llm_available = True
            logger.info(f"Smart Hybrid Classifier initialized with Groq model: {model_name}")
        except Exception as e:
            logger.warning(f"Groq LLM not available: {e}")
            logger.warning("Will use rule-based only")
            self.llm_available = False
            self.llm_manager = None
    
    def classify(self, query: str) -> Dict[str, Any]:
        """
        Smart classification: rules first, LLM for uncertain cases.
        
        Args:
            query: User's natural language query
            
        Returns:
            Classification result with method used
        """
        # Step 1: Try rule-based classification
        rule_result = self.rule_classifier.classify(query)
        
        # Step 2: Check if rule-based is confident enough
        if (rule_result["confidence"] >= self.confidence_threshold and 
            rule_result["intent"] != Intent.UNKNOWN):
            
            logger.info(
                f"✓ Rule-based confident: {rule_result['intent'].value} "
                f"(confidence: {rule_result['confidence']:.2f})"
            )
            
            return {
                **rule_result,
                "method": "rule_based",
                "llm_used": False
            }
        
        # Step 3: Rules uncertain - use smart LLM
        logger.info(
            f"⚠ Rule-based uncertain (confidence: {rule_result['confidence']:.2f}, "
            f"intent: {rule_result['intent'].value}) - asking smart LLM"
        )
        
        if not self.llm_available:
            logger.warning("LLM not available, returning uncertain rule-based result")
            return {
                **rule_result,
                "method": "rule_based",
                "llm_used": False,
                "note": "LLM unavailable, used uncertain result"
            }
        
        # Step 4: Ask LLM to classify with context
        llm_result = self._ask_smart_llm(query, rule_result)
        
        return llm_result
    
    def _ask_smart_llm(self, query: str, rule_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ask smart LLM to classify the intent using context.
        
        Args:
            query: Original query
            rule_result: Rule-based classification attempt
            
        Returns:
            LLM classification result
        """
        # Build smart prompt with available intents
        intent_descriptions = {
            "player_search": "Finding a specific player by name",
            "player_stats": "Getting player statistics for a season", 
            "top_scorers": "Finding top goal scorers by position",
            "top_assisters": "Finding top assist providers",
            "team_analysis": "Analyzing team players and performance",
            "gameweek_performers": "Finding top performers in a specific gameweek",
            "player_comparison": "Comparing multiple players",
            "high_performers": "Finding players exceeding performance thresholds",
            "player_form": "Analyzing recent player form",
            "ict_analysis": "Finding players with best ICT scores",
        }
        
        # Build the prompt
        prompt = f"""You are an intent classifier for an FPL (Fantasy Premier League) system.

User Query: "{query}"

Rule-based pattern matching suggested:
- Intent: {rule_result['intent'].value}
- Confidence: {rule_result['confidence']:.2f}
- Reasoning: {rule_result['reasoning']}

Available intents:
{chr(10).join(f"- {intent}: {desc}" for intent, desc in intent_descriptions.items())}

Analyze the query and classify it. Output ONLY a JSON object with this format (no markdown, no extra text):
{{"intent": "player_search", "confidence": 0.90, "reasoning": "brief reason"}}"""

        try:
            # Call Groq LLM
            result = self.llm_manager.generate(
                prompt=prompt,
                model=self.model_name,
                temperature=0.1,  # Low temperature for consistent classification
                max_tokens=150
            )
            response = result.get('response', '')
            
            # Parse JSON response
            import json
            import re
            
            # Try to extract JSON - be more flexible
            # First try direct JSON parsing
            try:
                parsed = json.loads(response.strip())
            except:
                # Try to find JSON in the response (handle markdown, extra text)
                json_match = re.search(r'\{[^\}]+\}', response, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                else:
                    logger.error(f"No valid JSON found. Response: {response[:200]}")
                    raise ValueError(f"No valid JSON found in response")
            
            intent_str = parsed.get('intent', 'unknown')
            confidence = float(parsed.get('confidence', 0.5))
            reasoning = parsed.get('reasoning', 'LLM classification')
            
            # Map string to Intent enum
            intent = Intent.UNKNOWN
            for intent_enum in Intent:
                if intent_enum.value == intent_str:
                    intent = intent_enum
                    break
            
            logger.info(
                f"🤖 LLM classified as: {intent.value} "
                f"(confidence: {confidence:.2f})"
            )
            
            return {
                "intent": intent,
                "confidence": confidence,
                "reasoning": reasoning,
                "query": query,
                "method": "llm",
                "llm_used": True,
                "rule_based_suggestion": {
                    "intent": rule_result["intent"].value,
                    "confidence": rule_result["confidence"]
                }
            }
                
        except Exception as e:
            logger.error(f"LLM classification failed: {e}")
            logger.warning("Falling back to rule-based result")
            return {
                **rule_result,
                "method": "rule_based",
                "llm_used": False,
                "note": f"LLM failed: {str(e)}"
            }
    
    def get_query_mapping(self, intent: Intent) -> str:
        """Map intent to retriever method."""
        return self.rule_classifier.get_query_mapping(intent)
