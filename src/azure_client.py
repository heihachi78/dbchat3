import logging
import threading
import numpy as np
from .config import Config
from .azure_factory import get_chat_client, get_embedding_client

logger = logging.getLogger(__name__)

class AzureOpenAIClient:
    def __init__(self):
        # Use shared clients instead of creating new ones
        self.client = get_chat_client()
        self.embedding_client = get_embedding_client()
        # Token usage tracking with thread safety
        self.token_usage = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0
        }
        self._token_lock = threading.Lock()
        logger.info("Initialized Azure OpenAI clients")
    
    def generate_documentation(self, content: str, system_prompt: str) -> str:
        """Generate documentation for SQL content"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content.strip()}
        ]
        
        response = self.client.chat.completions.create(
            model=Config.AZURE_OPENAI_DEPLOYMENT,
            messages=messages,
            temperature=0,
            top_p=1,
            n=1,
        )
        
        # Track token usage if available (thread-safe)
        if response.usage and Config.ENABLE_TOKEN_TRACKING:
            with self._token_lock:
                self.token_usage["total_tokens"] += response.usage.total_tokens
                self.token_usage["prompt_tokens"] += response.usage.prompt_tokens
                self.token_usage["completion_tokens"] += response.usage.completion_tokens
            logger.debug(f"Documentation generation used {response.usage.total_tokens} tokens")
        
        return response.choices[0].message.content
    
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
    
    async def llm_model_func(self, prompt: str, system_prompt: str = None, 
                           history_messages: list = None, **kwargs) -> str:
        """Async function for LightRAG LLM calls"""
        if history_messages is None:
            history_messages = []
        
        # Use shared client instead of creating new one every time
        client = get_chat_client()
            
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history_messages:
            messages.extend(history_messages)
        messages.append({"role": "user", "content": prompt})
        
        chat_completion = client.chat.completions.create(
            model=Config.AZURE_OPENAI_DEPLOYMENT,
            messages=messages,
            temperature=kwargs.get("temperature", 0),
            top_p=kwargs.get("top_p", 1),
            n=kwargs.get("n", 1),
        )
        
        logger.info("LLM model response generated")
        return chat_completion.choices[0].message.content
    
    async def embedding_func(self, texts: list[str]) -> np.ndarray:
        """Generate embeddings for texts"""
        # Use shared client instead of creating new one every time
        client = get_embedding_client()
        
        embedding = client.embeddings.create(
            model=Config.AZURE_EMBEDDING_DEPLOYMENT,
            input=texts
        )
        
        embeddings = [item.embedding for item in embedding.data]
        logger.info(f"Generated embeddings for {len(texts)} texts")
        return np.array(embeddings)