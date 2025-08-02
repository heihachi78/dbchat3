import logging
from openai import AzureOpenAI, AuthenticationError, APIConnectionError
from .config import Config

logger = logging.getLogger(__name__)

# Global shared clients - created once and reused
_chat_client = None
_embedding_client = None

def get_chat_client():
    """Get shared Azure OpenAI chat client. Creates it once, then reuses it."""
    global _chat_client
    
    if _chat_client is None:
        try:
            # Configuration validation happens at application startup in main.py
            # No need to validate here again
            
            _chat_client = AzureOpenAI(
                api_version=Config.AZURE_OPENAI_API_VERSION,
                azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
                api_key=Config.AZURE_OPENAI_API_KEY
            )
            logger.info("Created shared Azure OpenAI chat client")
            
        except AuthenticationError as e:
            logger.error(f"Azure OpenAI authentication failed for chat client: {e}")
            raise ValueError(f"Invalid Azure OpenAI credentials for chat client: {e}")
        except APIConnectionError as e:
            logger.error(f"Azure OpenAI connection failed for chat client: {e}")
            raise ConnectionError(f"Cannot connect to Azure OpenAI for chat client: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating Azure OpenAI chat client: {e}")
            raise RuntimeError(f"Failed to create Azure OpenAI chat client: {e}")
    
    return _chat_client

def get_embedding_client():
    """Get shared Azure OpenAI embedding client. Creates it once, then reuses it."""
    global _embedding_client
    
    if _embedding_client is None:
        try:
            # Configuration validation happens at application startup in main.py
            # No need to validate here again
            
            _embedding_client = AzureOpenAI(
                api_key=Config.AZURE_OPENAI_API_KEY,
                api_version=Config.AZURE_EMBEDDING_API_VERSION,
                azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            )
            logger.info("Created shared Azure OpenAI embedding client")
            
        except AuthenticationError as e:
            logger.error(f"Azure OpenAI authentication failed for embedding client: {e}")
            raise ValueError(f"Invalid Azure OpenAI credentials for embedding client: {e}")
        except APIConnectionError as e:
            logger.error(f"Azure OpenAI connection failed for embedding client: {e}")
            raise ConnectionError(f"Cannot connect to Azure OpenAI for embedding client: {e}")
        except Exception as e:
            logger.error(f"Unexpected error creating Azure OpenAI embedding client: {e}")
            raise RuntimeError(f"Failed to create Azure OpenAI embedding client: {e}")
    
    return _embedding_client