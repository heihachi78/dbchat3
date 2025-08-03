import logging
import threading
import ollama
import numpy as np
import re
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, host: str = "http://localhost:11434", timeout: int = 300):
        self.host = host
        self.timeout = timeout
        # Create both sync and async clients with enhanced timeout settings
        self.client = ollama.Client(host=host, timeout=timeout)
        
        # For async client, use extended timeout for LightRAG operations
        extended_timeout = max(timeout, 600)  # Minimum 10 minutes for complex operations
        self.async_client = ollama.AsyncClient(host=host, timeout=extended_timeout)
        
        # Store both timeouts for reference
        self.sync_timeout = timeout
        self.async_timeout = extended_timeout
        
        # Token usage tracking with thread safety
        self.token_usage = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0
        }
        self._token_lock = threading.Lock()
        logger.info(f"Initialized Ollama clients with host: {host}, sync_timeout: {self.sync_timeout}s, async_timeout: {self.async_timeout}s")
    
    def _strip_thinking_tags(self, text: str) -> str:
        """Remove <think>...</think> tags and their content from text"""
        # Remove thinking tags and their content using regex with DOTALL flag
        cleaned_text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        # Strip any leading/trailing whitespace that might be left
        return cleaned_text.strip()
    
    def generate_documentation(self, content: str, system_prompt: str, model: str = None) -> str:
        """Generate documentation for SQL content using Ollama"""
        # Import here to avoid circular import
        from .config import Config
        if model is None:
            model = Config.OLLAMA_LLM_MODEL
            
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": content.strip()}
            ]
            
            response = self.client.chat(
                model=model,
                messages=messages,
                options={
                    "temperature": 0,
                    "top_p": 1,
                    "num_ctx": Config.OLLAMA_NUM_CTX,  # Configurable context window
                }
            )
            
            # Track token usage if available
            if hasattr(response, 'prompt_eval_count') and hasattr(response, 'eval_count'):
                with self._token_lock:
                    prompt_tokens = response.prompt_eval_count or 0
                    completion_tokens = response.eval_count or 0
                    total_tokens = prompt_tokens + completion_tokens
                    
                    self.token_usage["prompt_tokens"] += prompt_tokens
                    self.token_usage["completion_tokens"] += completion_tokens
                    self.token_usage["total_tokens"] += total_tokens
                    
                logger.debug(f"Documentation generation used {total_tokens} tokens")
            
            # Clean the response by removing thinking tags
            raw_content = response['message']['content']
            cleaned_content = self._strip_thinking_tags(raw_content)
            return cleaned_content
            
        except Exception as e:
            logger.error(f"Error in Ollama generate_documentation: {e}")
            raise
    
    async def chat_completion_async(self, messages: List[Dict[str, str]], model: str = None, **kwargs) -> str:
        """Async chat completion for LightRAG integration"""
        # Import here to avoid circular import
        from .config import Config
        if model is None:
            model = Config.OLLAMA_LLM_MODEL
            
        try:
            options = kwargs.get("options", {})
            # Ensure we have sufficient context
            if "num_ctx" not in options:
                options["num_ctx"] = Config.OLLAMA_NUM_CTX
            
            response = await self.async_client.chat(
                model=model,
                messages=messages,
                options=options
            )
            
            # Track token usage if available
            if hasattr(response, 'prompt_eval_count') and hasattr(response, 'eval_count'):
                with self._token_lock:
                    prompt_tokens = response.prompt_eval_count or 0
                    completion_tokens = response.eval_count or 0
                    total_tokens = prompt_tokens + completion_tokens
                    
                    self.token_usage["prompt_tokens"] += prompt_tokens
                    self.token_usage["completion_tokens"] += completion_tokens
                    self.token_usage["total_tokens"] += total_tokens
            
            # Clean the response by removing thinking tags
            raw_content = response['message']['content']
            cleaned_content = self._strip_thinking_tags(raw_content)
            return cleaned_content
            
        except Exception as e:
            logger.error(f"Error in Ollama async chat completion: {e}")
            raise
    
    async def embed_async(self, texts: List[str], model: str = None) -> np.ndarray:
        """Async embedding generation for LightRAG integration"""
        # Import here to avoid circular import
        from .config import Config
        if model is None:
            model = Config.OLLAMA_EMBEDDING_MODEL
            
        try:
            response = await self.async_client.embed(
                model=model,
                input=texts
            )
            
            # Note: Ollama doesn't provide token counts for embeddings
            # We could estimate based on text length if needed
            
            embeddings = response['embeddings']
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return np.array(embeddings)
            
        except Exception as e:
            logger.error(f"Error in Ollama async embed: {e}")
            raise
    
    def get_token_usage(self) -> dict:
        """Get current token usage statistics"""
        with self._token_lock:
            return self.token_usage.copy()
    
    def reset_token_usage(self):
        """Reset token usage statistics"""
        with self._token_lock:
            self.token_usage = {
                "total_tokens": 0,
                "prompt_tokens": 0,
                "completion_tokens": 0
            }