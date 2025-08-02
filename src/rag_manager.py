import logging
import numpy as np
from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc, TokenTracker
from lightrag.kg.shared_storage import initialize_pipeline_status
from .config import Config
from neo4j import GraphDatabase

logger = logging.getLogger(__name__)

# Global token tracker for standalone functions
_global_token_tracker = None

def set_global_token_tracker(tracker):
    """Set the global token tracker for standalone functions"""
    global _global_token_tracker
    _global_token_tracker = tracker

# Import azure_factory for shared clients
from .azure_factory import get_chat_client, get_embedding_client


# Standalone functions for LightRAG - use shared clients AND track tokens for RAG
async def llm_model_func(prompt: str, system_prompt: str = None, 
                       history_messages: list = None, **kwargs) -> str:
    """LLM function for LightRAG - uses shared Azure client with RAG token tracking"""
    if history_messages is None:
        history_messages = []
    
    # Use shared client instead of creating new one
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
    
    # Track token usage for RAG if global tracker is available
    global _global_token_tracker
    if _global_token_tracker and Config.ENABLE_TOKEN_TRACKING and chat_completion.usage:
        usage = chat_completion.usage
        _global_token_tracker.add_usage({
            'prompt_tokens': usage.prompt_tokens,
            'completion_tokens': usage.completion_tokens,
            'total_tokens': usage.total_tokens
        })
        logger.debug(f"LLM tracked {usage.total_tokens} tokens for RAG")
    
    logger.info("LLM model response generated")
    return chat_completion.choices[0].message.content

async def embedding_func(texts: list[str]) -> np.ndarray:
    """Generate embeddings for texts - uses shared Azure client with RAG token tracking"""
    # Use shared client instead of creating new one
    client = get_embedding_client()
    
    embedding = client.embeddings.create(
        model=Config.AZURE_EMBEDDING_DEPLOYMENT,
        input=texts
    )
    
    # Track token usage for RAG if global tracker is available
    global _global_token_tracker
    if _global_token_tracker and Config.ENABLE_TOKEN_TRACKING and embedding.usage:
        usage = embedding.usage
        _global_token_tracker.add_usage({
            'prompt_tokens': usage.prompt_tokens,
            'completion_tokens': 0,  # Embeddings don't have completion tokens
            'total_tokens': usage.total_tokens
        })
        logger.debug(f"Embedding tracked {usage.total_tokens} tokens for RAG")
    
    embeddings = [item.embedding for item in embedding.data]
    logger.info(f"Generated embeddings for {len(texts)} texts")
    return np.array(embeddings)

class RAGManager:
    def __init__(self):
        self.working_dir = Config.WORKING_DIR
        self.rag = None
        self.token_tracker = TokenTracker()
        self.enable_token_tracking = Config.ENABLE_TOKEN_TRACKING
        
        # Set the global token tracker for direct Azure functions
        set_global_token_tracker(self.token_tracker)
        logger.info("RAGManager initialized with direct Azure OpenAI embedding")
    
    def clear_neo4j_database(self):
        """Clear all data from Neo4j database"""
        try:
            driver = GraphDatabase.driver(
                Config.NEO4J_URI,
                auth=(Config.NEO4J_USERNAME, Config.NEO4J_PASSWORD)
            )
            
            with driver.session(database=Config.NEO4J_DATABASE) as session:
                # Delete all nodes and relationships
                session.run("MATCH (n) DETACH DELETE n")
                logger.info("Neo4j database cleared successfully")
            
            driver.close()
        except Exception as e:
            logger.error(f"Failed to clear Neo4j database: {e}")
            raise
    
    async def initialize(self):
        """Initialize LightRAG with Azure OpenAI functions and Neo4j storage"""
        # Validate Neo4j configuration
        try:
            Config.validate_neo4j_config()
            logger.info("Neo4j configuration validated successfully")
        except ValueError as e:
            logger.error(f"Neo4j configuration error: {e}")
            raise
        
        try:
            self.rag = LightRAG(
                working_dir=str(self.working_dir),
                llm_model_func=llm_model_func,
                embedding_func=EmbeddingFunc(
                    embedding_dim=Config.EMBEDDING_DIMENSION,
                    max_token_size=8192,
                    func=embedding_func,
                ),
                vector_storage="FaissVectorDBStorage",
                graph_storage="Neo4JStorage",
            )
            
            logger.info("Initialized LightRAG with direct Azure OpenAI and Neo4j graph storage")
            
            await self.rag.initialize_storages()
            await initialize_pipeline_status()
        except Exception as e:
            logger.error(f"Failed to initialize LightRAG with Neo4j: {e}")
            raise
    
    async def insert_documents(self):
        """Insert all markdown documents into RAG storage"""
        if not self.rag:
            raise RuntimeError("RAG not initialized. Call initialize() first.")
        
        # Reset token tracker for insert operation
        self.reset_token_tracker()
        
        # Use context manager if token tracking is enabled
        if self.enable_token_tracking:
            with self.token_tracker:
                for md_file in self.working_dir.rglob("*.md"):
                    with open(md_file, encoding="utf-8") as doc:
                        await self.rag.ainsert([doc.read()], file_paths=[md_file.name])
                        logger.info(f"Inserted documentation from {md_file} into RAG storage")
        else:
            for md_file in self.working_dir.rglob("*.md"):
                with open(md_file, encoding="utf-8") as doc:
                    await self.rag.ainsert([doc.read()], file_paths=[md_file.name])
                    logger.info(f"Inserted documentation from {md_file} into RAG storage")
        
        logger.info("All documentation files inserted into RAG storage")
        
        # Log token usage for insert operation
        if self.enable_token_tracking:
            usage = self.token_tracker.get_usage()
            logger.info(f"Token usage for document insertion: {usage}")
    
    async def query(self, text: str, mode: str = "hybrid", conversation_history: list = None, track_tokens: bool = True) -> str:
        """Query the RAG system with optional conversation history and token tracking"""
        if not self.rag:
            raise RuntimeError("RAG not initialized. Call initialize() first.")
        
        params = QueryParam(mode=mode)
        if conversation_history:
            params.conversation_history = conversation_history
        
        # Reset token tracker for this query to get per-query usage
        if self.enable_token_tracking and track_tokens:
            self.token_tracker.reset()
        
        result = await self.rag.aquery(text, param=params)
        
        # Log token usage for this query
        if self.enable_token_tracking and track_tokens:
            usage = self.token_tracker.get_usage()
            logger.info(f"Token usage for query (mode={mode}): {usage}")
        
        return result
    
    async def query_all_modes(self, text: str, conversation_history: list = None) -> dict:
        """Query using all available modes and return results"""
        if not self.rag:
            raise RuntimeError("RAG not initialized. Call initialize() first.")
        
        results = {}
        modes = ["naive", "local", "global", "hybrid"]
        
        # Reset token tracker for all-modes query
        self.reset_token_tracker()
        
        for mode in modes:
            try:
                params = QueryParam(mode=mode)
                if conversation_history:
                    params.conversation_history = conversation_history
                    
                # Track tokens per mode
                if self.enable_token_tracking:
                    with self.token_tracker:
                        results[mode] = await self.rag.aquery(text, param=params)
                else:
                    results[mode] = await self.rag.aquery(text, param=params)
                    
            except Exception as e:
                logger.error(f"Error querying in {mode} mode: {e}")
                results[mode] = f"Error: {str(e)}"
        
        # Log total token usage for all modes
        if self.enable_token_tracking:
            usage = self.token_tracker.get_usage()
            logger.info(f"Total token usage for all modes query: {usage}")
        
        return results
    
    def get_token_usage(self) -> dict:
        """Get current token usage statistics"""
        if self.enable_token_tracking:
            return self.token_tracker.get_usage()
        return {"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0}
    
    def reset_token_tracker(self):
        """Reset token usage statistics"""
        if self.enable_token_tracking:
            self.token_tracker.reset()
            logger.info("Token tracker reset")
    
    def set_token_tracking(self, enabled: bool):
        """Enable or disable token tracking"""
        self.enable_token_tracking = enabled
        logger.info(f"Token tracking {'enabled' if enabled else 'disabled'}")