import logging
import numpy as np
from urllib.parse import quote_plus
from openai import RateLimitError, APIConnectionError, APITimeoutError
from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc, TokenTracker
from lightrag.kg.shared_storage import initialize_pipeline_status
from .config import Config
from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, TransientError
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, InvalidURI
from .retry_utils import retry_async, retry_sync, AZURE_API_RETRY_CONFIG, DATABASE_RETRY_CONFIG

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
@retry_async(**AZURE_API_RETRY_CONFIG)
async def llm_model_func(prompt: str, system_prompt: str = None, 
                       history_messages: list = None, **kwargs) -> str:
    """LLM function for LightRAG - uses shared Azure client with RAG token tracking and retry logic"""
    if history_messages is None:
        history_messages = []
    
    try:
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
        
    except (RateLimitError, APIConnectionError, APITimeoutError) as e:
        logger.error(f"Azure OpenAI API error in llm_model_func: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in llm_model_func: {e}")
        raise

@retry_async(**AZURE_API_RETRY_CONFIG)
async def embedding_func(texts: list[str]) -> np.ndarray:
    """Generate embeddings for texts - uses shared Azure client with RAG token tracking and retry logic"""
    try:
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
        
    except (RateLimitError, APIConnectionError, APITimeoutError) as e:
        logger.error(f"Azure OpenAI API error in embedding_func: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in embedding_func: {e}")
        raise

class RAGManager:
    def __init__(self):
        self.working_dir = Config.WORKING_DIR
        self.rag = None
        self.token_tracker = TokenTracker()
        self.enable_token_tracking = Config.ENABLE_TOKEN_TRACKING
        
        # Set the global token tracker for direct Azure functions
        set_global_token_tracker(self.token_tracker)
        logger.info("RAGManager initialized with direct Azure OpenAI embedding")
    
    @retry_sync(max_attempts=3, base_delay=2.0, retryable_exceptions=(ServiceUnavailable, TransientError, ConnectionError))
    def clear_neo4j_database(self):
        """Clear all data from Neo4j database with retry logic"""
        driver = None
        try:
            driver = GraphDatabase.driver(
                Config.NEO4J_URI,
                auth=(Config.NEO4J_USERNAME, Config.NEO4J_PASSWORD),
                connection_timeout=10.0,
                max_connection_lifetime=300
            )
            
            # Test connection before proceeding
            with driver.session(database=Config.NEO4J_DATABASE) as session:
                # Verify connection with a simple query
                session.run("RETURN 1")
                
                # Delete all nodes and relationships
                session.run("MATCH (n) DETACH DELETE n")
                logger.info("Neo4j database cleared successfully")
                
        except (ServiceUnavailable, TransientError) as e:
            logger.error(f"Neo4j connection error (will retry): {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to clear Neo4j database: {e}")
            raise
        finally:
            if driver:
                driver.close()
    
    @retry_sync(max_attempts=3, base_delay=2.0, retryable_exceptions=(ConnectionFailure, ServerSelectionTimeoutError, InvalidURI))
    def clear_mongodb_database(self):
        """Clear all data from MongoDB database with retry logic"""
        client = None
        try:
            # Build MongoDB connection string with properly escaped credentials
            escaped_user = quote_plus(Config.MONGO_USER)
            escaped_pass = quote_plus(Config.MONGO_PASS)
            mongo_uri = f"mongodb://{escaped_user}:{escaped_pass}@{Config.MONGO_URI.replace('mongodb://', '')}"
            client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=10000,  # 10 second timeout
                connectTimeoutMS=5000,  # 5 second connection timeout
                socketTimeoutMS=30000   # 30 second socket timeout
            )
            
            # Test connection before proceeding
            client.admin.command('ping')
            
            # Get the database
            db = client[Config.MONGO_DATABASE]
            
            # Get all collection names and drop them
            collection_names = db.list_collection_names()
            for collection_name in collection_names:
                db[collection_name].drop()
                logger.info(f"Dropped MongoDB collection: {collection_name}")
            
            logger.info("MongoDB database cleared successfully")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB connection error (will retry): {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to clear MongoDB database: {e}")
            raise
        finally:
            if client:
                client.close()
    
    async def initialize(self):
        """Initialize LightRAG with Azure OpenAI functions, Neo4j graph storage, and MongoDB KV/doc status storage"""
        # Configuration validation happens at application startup in main.py
        # No need to validate here again
        
        try:
            # Test database connections before initializing LightRAG
            self._test_database_connections()
            
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
                kv_storage="MongoKVStorage",
                doc_status_storage="MongoDocStatusStorage",
            )
            
            logger.info("Initialized LightRAG with Azure OpenAI, Neo4j graph storage, and MongoDB KV/doc status storage")
            
            await self.rag.initialize_storages()
            await initialize_pipeline_status()
        except Exception as e:
            logger.error(f"Failed to initialize LightRAG: {e}")
            raise
    
    def _test_database_connections(self):
        """Test Neo4j and MongoDB connections before initialization"""
        # Test Neo4j connection
        driver = None
        try:
            driver = GraphDatabase.driver(
                Config.NEO4J_URI,
                auth=(Config.NEO4J_USERNAME, Config.NEO4J_PASSWORD),
                connection_timeout=10.0
            )
            with driver.session(database=Config.NEO4J_DATABASE) as session:
                session.run("RETURN 1")
            logger.info("Neo4j connection test successful")
        except Exception as e:
            logger.error(f"Neo4j connection test failed: {e}")
            raise ConnectionError(f"Cannot connect to Neo4j: {e}")
        finally:
            if driver:
                driver.close()
        
        # Test MongoDB connection
        client = None
        try:
            # Use MongoDB URI directly if it already contains credentials
            mongo_uri = self._build_mongo_uri()
            logger.info(f"Using MongoDB URI for connection test: {mongo_uri}")
            client = MongoClient(
                mongo_uri,
                serverSelectionTimeoutMS=10000
            )
            client.admin.command('ping')
            logger.info("MongoDB connection test successful")
        except Exception as e:
            logger.error(f"MongoDB connection test failed: {e}")
            raise ConnectionError(f"Cannot connect to MongoDB: {e}")
        finally:
            if client:
                client.close()
    
    def _build_mongo_uri(self) -> str:
        """Build MongoDB URI, handling cases where credentials are already in URI or need to be added"""
        base_uri = Config.MONGO_URI
        
        # Check if URI already contains credentials (has @ symbol)
        if '@' in base_uri:
            # URI already contains credentials, use as-is
            logger.debug("Using MongoDB URI with embedded credentials")
            return base_uri
        
        # URI doesn't contain credentials, add them if available
        if Config.MONGO_USER and Config.MONGO_PASS:
            # Properly escape credentials
            escaped_user = quote_plus(Config.MONGO_USER)
            escaped_pass = quote_plus(Config.MONGO_PASS)
            
            # Remove mongodb:// prefix, add credentials, then re-add prefix
            uri_without_scheme = base_uri.replace('mongodb://', '').replace('mongodb+srv://', '')
            scheme = 'mongodb+srv://' if base_uri.startswith('mongodb+srv://') else 'mongodb://'
            
            mongo_uri = f"{scheme}{escaped_user}:{escaped_pass}@{uri_without_scheme}"
            logger.debug("Built MongoDB URI with separate user/pass credentials")
            return mongo_uri
        else:
            # No credentials provided, use URI as-is
            logger.debug("Using MongoDB URI without credentials")
            return base_uri
    
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
        
        try:
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
            
        except Exception as e:
            logger.error(f"Error querying in {mode} mode: {e}")
            return f"Error: {str(e)}"
    
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