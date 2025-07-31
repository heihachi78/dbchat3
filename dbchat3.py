import os
import logging
import numpy as np
import nest_asyncio
import asyncio
import shutil

from dotenv import load_dotenv
from openai import AzureOpenAI
from pathlib import Path

from lightrag import LightRAG, QueryParam
from lightrag.utils import EmbeddingFunc
from lightrag.kg.shared_storage import initialize_pipeline_status

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

load_dotenv()

AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

AZURE_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_DEPLOYMENT")
AZURE_EMBEDDING_API_VERSION = os.getenv("AZURE_EMBEDDING_API_VERSION")

DATABASE_FILES_DIR = Path("database_files")
WORKING_DIR = Path("working_dir")

EMBEDDING_DIMENSION = 3072 #small 1536, large 3072

logger.info("Loaded environment variables and parameters.")

azure_openai_client = AzureOpenAI(api_version=AZURE_OPENAI_API_VERSION, azure_endpoint=AZURE_OPENAI_ENDPOINT, api_key=AZURE_OPENAI_API_KEY)

logger.info("Initialized Azure OpenAI client.")

sql_files = []
if DATABASE_FILES_DIR.exists() and DATABASE_FILES_DIR.is_dir():
    for sql_file in DATABASE_FILES_DIR.rglob("*.sql"):
        with open(sql_file, encoding="utf-8") as f:
            content = f.read()

        sql_files.append((sql_file, content))

logger.info(f"Found {len(sql_files)} SQL files in {DATABASE_FILES_DIR}.")

system_prompt = """
You are an expert database documentation specialist. Your role is to create comprehensive, detailed documentation for database objects based on DDL (Data Definition Language) statements provided by users.

## Core Instructions

When a user provides DDL for any database object, create thorough documentation that extracts and utilizes ALL available information including comments, constraints, metadata, and specifications. Provide the most complete documentation possible - no detail is too small.

## Documentation Structure

Generate documentation with these sections:

### Object Overview
- Identify the type of database object (table, view, procedure, function, index, trigger, etc.)
- Explain the primary purpose and role within the database schema
- Provide business context and main use cases

### Detailed Structure & Components
- **For tables/views:** Document every column with complete details from DDL comments and constraints
- **For procedures/functions:** Detail all parameters, return types, and logic flow
- **For indexes:** Specify all columns covered, index type, purpose, and performance impact
- **For other objects:** Cover all relevant structural elements with full specifications

### Component Analysis (Leverage ALL DDL Comments)
- Extract business meaning and purpose from inline comments
- Document complete data type specifications (precision, scale, length)
- List all validation rules, constraints, and business logic
- Identify required vs optional elements with reasoning
- Explain default values, their significance, and business rationale
- Note any special handling, edge cases, or implementation details

### Complete Relationship Mapping
- Map all foreign key relationships with detailed explanations
- Identify self-referencing relationships and hierarchical structures
- Document dependencies on other database objects
- List objects that depend on this one
- Provide impact analysis for changes or cascading operations

### Comprehensive Constraints & Rules
- Document every constraint with business justification
- List all business rules enforced at database level
- Note security, access, and data integrity considerations
- Explain performance implications and optimization details

### Usage Patterns & Integration
- Describe how the object fits into larger business processes
- Detail common and advanced interaction patterns
- Identify query patterns this object supports
- Note performance characteristics and tuning considerations
- Explain integration points with applications

### Implementation Details
- Document storage specifications and logging settings
- Note any special database features utilized
- Include maintenance and operational considerations

## Quality Standards

- **Comprehensiveness:** Extract every piece of information from the DDL
- **Clarity:** Use clear, professional language accessible to technical and business users
- **Structure:** Organize with clear markdown headings for easy scanning
- **Accuracy:** Base all documentation strictly on the provided DDL
- **Detail:** Include all constraints, comments, data types, and specifications

## Output Format

Provide well-structured markdown documentation with clear headings. Make the documentation comprehensive yet scannable, suitable for database developers, business analysts, application developers, data architects, and database administrators.

Always begin your response with a clear heading identifying the database object name and type.
"""

logger.info("System prompt for documentation generation initialized.")

if os.path.exists(WORKING_DIR):
    shutil.rmtree(WORKING_DIR)

os.mkdir(WORKING_DIR)

logger.info(f"Working directory {WORKING_DIR} recreated.")

for md_file in DATABASE_FILES_DIR.rglob("*.md"):
    try:
        md_file.unlink(missing_ok=True)
        logger.info(f"Deleted file {md_file}")
    except PermissionError:
        logger.error(f"Permission denied deleting file {md_file}")
    except Exception as e:
        logger.error(f"Unexpected error deleting file {md_file}: {e}")


for sql_file, content in sql_files:
    user_prompt = content.strip()
    messages = []
    messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    chat_completion = azure_openai_client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT,
            messages=messages,
            temperature=0,
            top_p=1,
            n=1,
        ).choices[0].message.content
    with open(sql_file.with_suffix(".md"), "w") as f:
        f.write(chat_completion)
        logger.info(f"Generated documentation for {sql_file}.")

for md_file in DATABASE_FILES_DIR.rglob("*.md"):
    try:
        target_file = Path(WORKING_DIR) / md_file.name
        target_file.write_text(md_file.read_text(encoding="utf-8"), encoding="utf-8")
        logger.info(f"Copied file {md_file} to {target_file}")
    except PermissionError:
        logger.error(f"Permission denied copying file {md_file} to {target_file}")
    except Exception as e:
        logger.error(f"Unexpected error copying file {md_file} to {target_file}: {e}")

async def llm_model_func(
    prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
) -> str:
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
    )

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    if history_messages:
        messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    chat_completion = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=messages,
        temperature=kwargs.get("temperature", 0),
        top_p=kwargs.get("top_p", 1),
        n=kwargs.get("n", 1),
    )
    logger.info(f"LLM model response generated.")
    return chat_completion.choices[0].message.content

async def embedding_func(texts: list[str]) -> np.ndarray:
    client = AzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_EMBEDDING_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
    )
    embedding = client.embeddings.create(model=AZURE_EMBEDDING_DEPLOYMENT, input=texts)

    embeddings = [item.embedding for item in embedding.data]
    logger.info(f"Generated embeddings for {len(texts)} texts.")
    return np.array(embeddings)

async def initialize_rag():
    rag = LightRAG(
        working_dir=WORKING_DIR.name,
        llm_model_func=llm_model_func,
        embedding_func=EmbeddingFunc(
            embedding_dim=EMBEDDING_DIMENSION,
            max_token_size=8192,
            func=embedding_func,
        ),
    )

    await rag.initialize_storages()
    await initialize_pipeline_status()

    logger.info("Initialized LightRAG with storage and pipeline status.")
    return rag

rag = asyncio.run(initialize_rag())

logger.info("LightRAG initialized successfully.")

for md_file in WORKING_DIR.rglob("*.md"):
    with open(md_file, encoding="utf-8") as doc:
        rag.insert([doc.read()], file_paths=[md_file.name])
        logger.info(f"Inserted documentation from {md_file} into RAG storage.")

logger.info("All documentation files inserted into RAG storage.")

query_text = "What tables are in the database?"

print("==" * 50)
print("Result (Naive):")
print(rag.query(query_text, param=QueryParam(mode="naive")))
print("\n")

print("==" * 50)
print("\nResult (Local):")
print(rag.query(query_text, param=QueryParam(mode="local")))
print("\n")

print("==" * 50)
print("\nResult (Global):")
print(rag.query(query_text, param=QueryParam(mode="global")))
print("\n")

print("==" * 50)
print("\nResult (Hybrid):")
print(rag.query(query_text, param=QueryParam(mode="hybrid")))
print("\n")

# LLM
# 215 requests
# 709K total tokens 
# 431K Prompt tokens
# 278K completion tokens
# Embedding
# 3K requests
# 503K total tokens
# 503K prompt tokens