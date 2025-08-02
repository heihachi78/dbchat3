import logging
import numpy as np
from typing import List
from llama_index.core import Settings
from llama_index.llms.azure_openai import AzureOpenAI as LlamaIndexAzureOpenAI
from llama_index.embeddings.azure_openai import AzureOpenAIEmbedding
from .config import Config

logger = logging.getLogger(__name__)

class LlamaIndexAzureClient:
    """LlamaIndex-based Azure OpenAI client for enhanced embedding and LLM management"""
    
    def __init__(self):
        # Initialize LlamaIndex Azure OpenAI LLM
        self.llm = LlamaIndexAzureOpenAI(
            model=Config.AZURE_OPENAI_DEPLOYMENT,
            deployment_name=Config.AZURE_OPENAI_DEPLOYMENT,
            api_key=Config.AZURE_OPENAI_API_KEY,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            api_version=Config.AZURE_OPENAI_API_VERSION,
            temperature=0,
            max_tokens=None,
        )
        
        # Initialize LlamaIndex Azure OpenAI Embedding
        self.embedding_model = AzureOpenAIEmbedding(
            model=Config.AZURE_EMBEDDING_DEPLOYMENT,
            deployment_name=Config.AZURE_EMBEDDING_DEPLOYMENT,
            api_key=Config.AZURE_OPENAI_API_KEY,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            api_version=Config.AZURE_EMBEDDING_API_VERSION,
            embed_batch_size=10,  # Process embeddings in batches
        )
        
        # Set global LlamaIndex settings
        Settings.llm = self.llm
        Settings.embed_model = self.embedding_model
        
        # Token usage tracking
        self.token_usage = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0
        }
        
        logger.info("Initialized LlamaIndex Azure OpenAI clients")
    
    def generate_documentation(self, content: str, system_prompt: str) -> str:
        """Generate documentation for SQL content using LlamaIndex LLM"""
        try:
            # Create a prompt with system message embedded
            full_prompt = f"System: {system_prompt}\n\nUser: {content.strip()}"
            
            # Generate response using LlamaIndex
            response = self.llm.complete(full_prompt)
            
            # Track token usage if available (LlamaIndex provides this info)
            if hasattr(response, 'raw') and response.raw and hasattr(response.raw, 'usage'):
                usage = response.raw.usage
                if Config.ENABLE_TOKEN_TRACKING:
                    self.token_usage["total_tokens"] += usage.total_tokens
                    self.token_usage["prompt_tokens"] += usage.prompt_tokens
                    self.token_usage["completion_tokens"] += usage.completion_tokens
                    logger.debug(f"LlamaIndex documentation generation used {usage.total_tokens} tokens")
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating documentation with LlamaIndex: {e}")
            raise
    
    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for texts using LlamaIndex embedding model"""
        try:
            # Generate embeddings using LlamaIndex
            embeddings = self.embedding_model.get_text_embedding_batch(texts)
            
            # Convert to numpy array
            embeddings_array = np.array(embeddings)
            
            logger.info(f"Generated LlamaIndex embeddings for {len(texts)} texts")
            return embeddings_array
            
        except Exception as e:
            logger.error(f"Error generating embeddings with LlamaIndex: {e}")
            raise
    
    async def async_generate_documentation(self, content: str, system_prompt: str) -> str:
        """Async version of documentation generation"""
        try:
            # Create a prompt with system message embedded
            full_prompt = f"System: {system_prompt}\n\nUser: {content.strip()}"
            
            # Generate response using LlamaIndex async method
            response = await self.llm.acomplete(full_prompt)
            
            # Track token usage if available
            if hasattr(response, 'raw') and response.raw and hasattr(response.raw, 'usage'):
                usage = response.raw.usage
                if Config.ENABLE_TOKEN_TRACKING:
                    self.token_usage["total_tokens"] += usage.total_tokens
                    self.token_usage["prompt_tokens"] += usage.prompt_tokens
                    self.token_usage["completion_tokens"] += usage.completion_tokens
                    logger.debug(f"LlamaIndex async documentation generation used {usage.total_tokens} tokens")
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error generating documentation with LlamaIndex async: {e}")
            raise
    
    async def async_get_embeddings(self, texts: List[str]) -> np.ndarray:
        """Async version of embedding generation"""
        try:
            # Generate embeddings using LlamaIndex async method
            embeddings = await self.embedding_model.aget_text_embedding_batch(texts)
            
            # Convert to numpy array
            embeddings_array = np.array(embeddings)
            
            logger.info(f"Generated LlamaIndex async embeddings for {len(texts)} texts")
            return embeddings_array
            
        except Exception as e:
            logger.error(f"Error generating async embeddings with LlamaIndex: {e}")
            raise
    
    def get_token_usage(self) -> dict:
        """Get current token usage statistics"""
        return self.token_usage.copy()
    
    def reset_token_usage(self):
        """Reset token usage statistics"""
        self.token_usage = {
            "total_tokens": 0,
            "prompt_tokens": 0,
            "completion_tokens": 0
        }
        logger.info("LlamaIndex token usage reset")