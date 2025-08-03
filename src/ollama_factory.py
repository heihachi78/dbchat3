import logging
from typing import Optional
from .ollama_client import OllamaClient
from .config import Config

logger = logging.getLogger(__name__)

# Singleton instances
_ollama_client: Optional[OllamaClient] = None
_ollama_client_lock = None

def _get_lock():
    """Lazy initialization of threading lock to avoid import cycle"""
    global _ollama_client_lock
    if _ollama_client_lock is None:
        import threading
        _ollama_client_lock = threading.Lock()
    return _ollama_client_lock

def get_ollama_client() -> OllamaClient:
    """Get or create singleton Ollama client instance"""
    global _ollama_client
    
    if _ollama_client is None:
        lock = _get_lock()
        with lock:
            # Double-check pattern
            if _ollama_client is None:
                # Get configuration values
                host = getattr(Config, 'OLLAMA_HOST', 'http://localhost:11434')
                timeout = int(getattr(Config, 'OLLAMA_TIMEOUT', '300'))
                
                _ollama_client = OllamaClient(host=host, timeout=timeout)
                logger.info("Created singleton Ollama client instance")
    
    return _ollama_client

def reset_ollama_clients():
    """Reset the singleton Ollama client (useful for testing or config changes)"""
    global _ollama_client
    lock = _get_lock()
    
    with lock:
        _ollama_client = None
        logger.info("Reset Ollama client singleton")