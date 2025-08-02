import logging
from openai import AzureOpenAI
from .config import Config

logger = logging.getLogger(__name__)

# Global shared clients - created once and reused
_chat_client = None
_embedding_client = None

def get_chat_client():
    """Get shared Azure OpenAI chat client. Creates it once, then reuses it."""
    global _chat_client
    
    if _chat_client is None:
        # Validate config before creating client
        Config.validate_azure_config()
        
        _chat_client = AzureOpenAI(
            api_version=Config.AZURE_OPENAI_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
            api_key=Config.AZURE_OPENAI_API_KEY
        )
        logger.info("Created shared Azure OpenAI chat client")
    
    return _chat_client

def get_embedding_client():
    """Get shared Azure OpenAI embedding client. Creates it once, then reuses it."""
    global _embedding_client
    
    if _embedding_client is None:
        # Validate config before creating client
        Config.validate_azure_config()
        
        _embedding_client = AzureOpenAI(
            api_key=Config.AZURE_OPENAI_API_KEY,
            api_version=Config.AZURE_EMBEDDING_API_VERSION,
            azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
        )
        logger.info("Created shared Azure OpenAI embedding client")
    
    return _embedding_client