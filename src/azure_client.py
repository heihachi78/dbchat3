import logging
import threading
from openai import RateLimitError, APIConnectionError, APITimeoutError
from .config import Config
from .azure_factory import get_chat_client, get_embedding_client
from .retry_utils import retry_sync, AZURE_API_RETRY_CONFIG

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
    
    @retry_sync(**AZURE_API_RETRY_CONFIG)
    def generate_documentation(self, content: str, system_prompt: str) -> str:
        """Generate documentation for SQL content with retry logic"""
        try:
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
            
        except (RateLimitError, APIConnectionError, APITimeoutError) as e:
            logger.error(f"Azure OpenAI API error in generate_documentation: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in generate_documentation: {e}")
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
    
