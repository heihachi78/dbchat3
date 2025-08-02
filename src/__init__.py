"""
DBChat3 - Database Documentation RAG System

This package provides tools for generating comprehensive database documentation
using Azure OpenAI and enabling intelligent querying through LightRAG.
"""

from .config import Config
from .azure_client import AzureOpenAIClient
from .documentation_processor import DocumentationProcessor
from .rag_manager import RAGManager, azure_llm_callback, embedding_func

__all__ = [
    'Config',
    'AzureOpenAIClient',
    'DocumentationProcessor',
    'RAGManager',
    'azure_llm_callback',
    'embedding_func'
]

__version__ = '1.0.0'