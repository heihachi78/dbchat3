import logging
import numpy as np
from openai import AzureOpenAI
from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc
from lightrag.kg.shared_storage import initialize_pipeline_status
from config import Config

logger = logging.getLogger(__name__)

# Standalone functions for LightRAG to avoid deepcopy issues
async def llm_model_func(prompt: str, system_prompt: str = None, 
                       history_messages: list = None, **kwargs) -> str:
    """LLM function for LightRAG"""
    if history_messages is None:
        history_messages = []
    
    client = AzureOpenAI(
        api_key=Config.AZURE_OPENAI_API_KEY,
        api_version=Config.AZURE_OPENAI_API_VERSION,
        azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
    )
        
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

async def embedding_func(texts: list[str]) -> np.ndarray:
    """Generate embeddings for texts"""
    client = AzureOpenAI(
        api_key=Config.AZURE_OPENAI_API_KEY,
        api_version=Config.AZURE_EMBEDDING_API_VERSION,
        azure_endpoint=Config.AZURE_OPENAI_ENDPOINT,
    )
    
    embedding = client.embeddings.create(
        model=Config.AZURE_EMBEDDING_DEPLOYMENT,
        input=texts
    )
    
    embeddings = [item.embedding for item in embedding.data]
    logger.info(f"Generated embeddings for {len(texts)} texts")
    return np.array(embeddings)

class RAGManager:
    def __init__(self):
        self.working_dir = Config.WORKING_DIR
        self.rag = None
    
    async def initialize(self):
        """Initialize LightRAG with Azure OpenAI functions"""
        self.rag = LightRAG(
            working_dir=str(self.working_dir),
            llm_model_func=llm_model_func,
            embedding_func=EmbeddingFunc(
                embedding_dim=Config.EMBEDDING_DIMENSION,
                max_token_size=8192,
                func=embedding_func,
            ),
        )
        
        await self.rag.initialize_storages()
        await initialize_pipeline_status()
        
        logger.info("Initialized LightRAG with storage and pipeline status")
    
    def insert_documents(self):
        """Insert all markdown documents into RAG storage"""
        if not self.rag:
            raise RuntimeError("RAG not initialized. Call initialize() first.")
        
        for md_file in self.working_dir.rglob("*.md"):
            with open(md_file, encoding="utf-8") as doc:
                self.rag.insert([doc.read()], file_paths=[md_file.name])
                logger.info(f"Inserted documentation from {md_file} into RAG storage")
        
        logger.info("All documentation files inserted into RAG storage")
    
    def query(self, text: str, mode: str = "hybrid") -> str:
        """Query the RAG system"""
        if not self.rag:
            raise RuntimeError("RAG not initialized. Call initialize() first.")
        
        return self.rag.query(text, param=QueryParam(mode=mode))
    
    def query_all_modes(self, text: str) -> dict:
        """Query using all available modes and return results"""
        if not self.rag:
            raise RuntimeError("RAG not initialized. Call initialize() first.")
        
        results = {}
        modes = ["naive", "local", "global", "hybrid"]
        
        for mode in modes:
            try:
                results[mode] = self.rag.query(text, param=QueryParam(mode=mode))
            except Exception as e:
                logger.error(f"Error querying in {mode} mode: {e}")
                results[mode] = f"Error: {str(e)}"
        
        return results