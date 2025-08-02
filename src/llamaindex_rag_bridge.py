import logging
import numpy as np
from typing import List
from .llamaindex_client import LlamaIndexAzureClient
from .config import Config

logger = logging.getLogger(__name__)

# Global LlamaIndex client instance for standalone functions
_llamaindex_client = None
# Global token tracker for standalone functions
_global_token_tracker = None

def get_llamaindex_client():
    """Get or create the global LlamaIndex client instance"""
    global _llamaindex_client
    if _llamaindex_client is None:
        _llamaindex_client = LlamaIndexAzureClient()
        logger.info("Created global LlamaIndex client")
    return _llamaindex_client

def set_global_token_tracker(tracker):
    """Set the global token tracker for standalone functions"""
    global _global_token_tracker
    _global_token_tracker = tracker

# LightRAG-compatible standalone functions using LlamaIndex
async def llamaindex_llm_model_func(prompt: str, system_prompt: str = None, 
                                   history_messages: list = None, **kwargs) -> str:
    """LLM function for LightRAG using LlamaIndex Azure OpenAI"""
    if history_messages is None:
        history_messages = []
    
    try:
        client = get_llamaindex_client()
        
        # Build the full prompt with system prompt and history
        full_prompt_parts = []
        
        if system_prompt:
            full_prompt_parts.append(f"System: {system_prompt}")
        
        # Add conversation history
        for msg in history_messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            full_prompt_parts.append(f"{role.capitalize()}: {content}")
        
        # Add current prompt
        full_prompt_parts.append(f"User: {prompt}")
        
        full_prompt = "\n\n".join(full_prompt_parts)
        
        # Generate response using LlamaIndex
        response = await client.llm.acomplete(full_prompt)
        
        # Track token usage for RAG if global tracker is available
        global _global_token_tracker
        if (_global_token_tracker and Config.ENABLE_TOKEN_TRACKING and 
            hasattr(response, 'raw') and response.raw and hasattr(response.raw, 'usage')):
            usage = response.raw.usage
            _global_token_tracker.add_usage({
                'prompt_tokens': usage.prompt_tokens,
                'completion_tokens': usage.completion_tokens,
                'total_tokens': usage.total_tokens
            })
            logger.debug(f"LlamaIndex LLM tracked {usage.total_tokens} tokens for RAG")
        
        logger.info("LlamaIndex LLM model response generated")
        return response.text
        
    except Exception as e:
        logger.error(f"Error in LlamaIndex LLM function: {e}")
        raise

async def llamaindex_embedding_func(texts: List[str]) -> np.ndarray:
    """Generate embeddings for texts using LlamaIndex Azure OpenAI"""
    try:
        client = get_llamaindex_client()
        
        # Generate embeddings using LlamaIndex
        embeddings = await client.embedding_model.aget_text_embedding_batch(texts)
        
        # Convert to numpy array
        embeddings_array = np.array(embeddings)
        
        # Track token usage for RAG if global tracker is available
        # Note: LlamaIndex embedding models may not always provide usage info
        global _global_token_tracker
        if (_global_token_tracker and Config.ENABLE_TOKEN_TRACKING):
            # Estimate token usage based on text length (approximate)
            # This is a fallback since embedding models don't always provide usage stats
            estimated_tokens = sum(len(text.split()) for text in texts) * 1.3  # rough estimate
            _global_token_tracker.add_usage({
                'prompt_tokens': int(estimated_tokens),
                'completion_tokens': 0,  # Embeddings don't have completion tokens
                'total_tokens': int(estimated_tokens)
            })
            logger.debug(f"LlamaIndex embedding estimated {int(estimated_tokens)} tokens for RAG")
        
        logger.info(f"Generated LlamaIndex embeddings for {len(texts)} texts")
        return embeddings_array
        
    except Exception as e:
        logger.error(f"Error in LlamaIndex embedding function: {e}")
        raise

class LlamaIndexRAGBridge:
    """Bridge class to integrate LlamaIndex with the existing RAG system"""
    
    def __init__(self):
        self.client = get_llamaindex_client()
        self.token_usage = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0
        }
        logger.info("Initialized LlamaIndex RAG bridge")
    
    def get_llm_func(self):
        """Get the LlamaIndex-compatible LLM function for LightRAG"""
        return llamaindex_llm_model_func
    
    def get_embedding_func(self):
        """Get the LlamaIndex-compatible embedding function for LightRAG"""
        return llamaindex_embedding_func
    
    def get_token_usage(self) -> dict:
        """Get current token usage statistics from the LlamaIndex client"""
        return self.client.get_token_usage()
    
    def reset_token_usage(self):
        """Reset token usage statistics"""
        self.client.reset_token_usage()
        self.token_usage = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0
        }
        logger.info("LlamaIndex RAG bridge token usage reset")