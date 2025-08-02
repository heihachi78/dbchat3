# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

DBChat3 is a Python application that generates database documentation using Azure OpenAI and enables intelligent querying through LightRAG. It processes SQL DDL files to create comprehensive markdown documentation and builds a knowledge graph for natural language queries.

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Process database files and rebuild documentation
python main.py --process_database_files

# Start interactive chat mode
python main.py --chat

# Process files and immediately start chat mode
python main.py --process_database_files --chat

# Run RAG pipeline without regenerating docs (assumes MD files exist)
python main.py --run_pipeline

# Run pipeline and start chat
python main.py --run_pipeline --chat

# Run in Jupyter notebook
jupyter notebook dbchat3.ipynb
```

## High-Level Architecture

### Core Components

1. **Documentation Generator** (`src/documentation_processor.py`): Uses Azure OpenAI (GPT-4) to convert SQL DDL files into comprehensive markdown documentation
   - Processes files from `database_files/` directory
   - Generates markdown files for each SQL object (tables, views, indexes, functions)
   - Uses detailed system prompt for thorough documentation extraction
   - Cleans up existing docs before regeneration
   - Can skip generation if MD files already exist (`--run_pipeline` flag)

2. **RAG System** (`src/rag_manager.py`): Built on LightRAG for knowledge graph-based querying
   - Uses Neo4j as graph storage backend for enhanced performance
   - Initializes storage and pipeline in `working_dir/`
   - Supports multiple query modes: naive, local, global, and hybrid
   - Uses Azure text-embedding-3-large for semantic search
   - Maintains conversation history for context-aware responses
   - Clears Neo4j database before each initialization

3. **Azure OpenAI Integration** (`src/azure_client.py`):
   - `llm_model_func()`: Handles GPT-4 API calls for text generation
   - `embedding_func()`: Generates embeddings using Azure's text-embedding model
   - Configuration via environment variables in `.env`
   - Standalone async functions to avoid deepcopy issues with LightRAG
   - Clients instantiated inside functions for thread safety

4. **Configuration Management** (`src/config.py`):
   - Centralized configuration using environment variables
   - Detailed system prompt for documentation generation
   - Path management for directories and files
   - Validates Neo4j configuration on startup

### Key Workflows

1. **SQL Processing Flow**:
   - Scans `database_files/` for `.sql` files recursively
   - Sends each file to Azure OpenAI with comprehensive documentation prompt
   - Saves generated markdown alongside SQL files
   - Copies processed docs to `working_dir/` for RAG ingestion

2. **RAG Initialization**:
   - Clears Neo4j database to ensure clean state
   - Creates LightRAG instance with Azure OpenAI functions
   - Initializes vector storage (FAISS) and knowledge graph in `working_dir/`
   - Inserts all markdown documentation into RAG storage
   - Builds knowledge graph for semantic relationships

3. **Interactive Query Processing**:
   - Accepts natural language queries about database schema
   - Maintains conversation history for context
   - Processes through selected search mode (naive/local/global/hybrid)
   - Supports mode switching and history management commands
   - Can test queries with all modes simultaneously

### Application Entry Points

- **main.py**: Command-line interface with argument parsing
- **dbchat3.ipynb**: Jupyter notebook for interactive development (currently removed)
- Both support the same core functionality through modular architecture

## Environment Configuration

Required environment variables in `.env`:

### Azure OpenAI Configuration
- `AZURE_OPENAI_API_KEY` (required)
- `AZURE_OPENAI_ENDPOINT` (e.g., https://your-resource.openai.azure.com/)
- `AZURE_OPENAI_API_VERSION` (e.g., 2025-01-01-preview)
- `AZURE_OPENAI_DEPLOYMENT` (e.g., gpt-4.1)
- `AZURE_EMBEDDING_DEPLOYMENT` (e.g., text-embedding-3-large)
- `AZURE_EMBEDDING_API_VERSION` (e.g., 2024-02-01)
- `AZURE_EMBEDDING_DIMENSION` (e.g., 3072 for large, 1536 for small)

### Neo4j Configuration
- `NEO4J_URI` (default: "neo4j://localhost:7687")
- `NEO4J_USERNAME` (default: "neo4j")
- `NEO4J_PASSWORD` (required)
- `NEO4J_DATABASE` (default: "neo4j")
- `NEO4J_WORKSPACE` (optional)

**Note**: LightRAG uses Neo4j Community Edition with the default database. The system is configured to use `graph_storage="Neo4JStorage"` with explicit connection parameters to ensure compatibility with Community Edition, which doesn't support creating new databases.

### Optional Settings
- `LOG_DIR` (optional, defaults to "logs")

### Token Tracking Settings
- `ENABLE_TOKEN_TRACKING` (default: "true") - Enable/disable token usage tracking
- `SHOW_TOKEN_USAGE_IN_CHAT` (default: "true") - Show token usage after each query in chat mode

## Important Patterns

- **Neo4j Graph Storage**: Uses Neo4j instead of NetworkX for better performance and scalability
- **Configuration Validation**: Validates Neo4j connection settings on startup
- **Embedding Dimension**: Set to 3072 for text-embedding-3-large (was 3072 for small, 3072 for large)
- **Comprehensive Logging**: File and console logging with timestamps
- **Error Handling**: Robust error handling for file operations and API calls
- **Directory Management**: Automatic creation of `working_dir` and `logs` directories
- **Standalone Async Functions**: LightRAG compatibility requires standalone functions
- **Conversation History**: Maintained across queries in interactive mode
- **Comprehensive System Prompt**: Detailed instructions for thorough documentation extraction
- **Token Tracking**: Built-in token usage tracking using LightRAG's TokenTracker utility

## Neo4j Setup

To run Neo4j locally using Docker (from neo4j.md):

```bash
docker run -d --restart always --publish=7474:7474 --publish=7687:7687 \
  --env NEO4J_AUTH=neo4j/pass4jdbchat \
  --volume=/home/tothi/python/dbchat3/data:/data \
  neo4j:2025.06.2
```

- Neo4j Browser: http://localhost:7474
- Bolt connection: neo4j://localhost:7687
- Default credentials: neo4j/pass4jdbchat

## Interactive Chat Commands

When in chat mode (`python main.py --chat`):
- `exit`, `quit`, `q` - Exit the application
- `/mode <mode>` - Change query mode (naive|local|global|hybrid)
- `/clear` - Clear conversation history
- `/history` - Show conversation history
- `/tokens` - Show current token usage
- `/tokens reset` - Reset token counter
- `/tokens off` - Disable token tracking
- `/tokens on` - Enable token tracking
- `modes` - Test query with all modes (prompts for query)

## Directory Structure

```
dbchat3/
├── main.py                 # Main entry point with CLI argument parsing
├── src/
│   ├── __init__.py        # Module initialization
│   ├── azure_client.py    # Azure OpenAI client wrapper
│   ├── config.py          # Configuration and environment management
│   ├── documentation_processor.py  # SQL to Markdown conversion
│   └── rag_manager.py     # LightRAG integration and query handling
├── database_files/        # Input SQL DDL files
│   └── sampledb/         # Sample database with HR schema
├── working_dir/          # Generated docs and RAG storage
│   ├── *.md              # Processed markdown documentation
│   ├── faiss_index_*.index  # FAISS vector indexes
│   └── kv_store_*.json   # Key-value stores for RAG
├── logs/                 # Application logs
├── data/                 # Neo4j database files
├── requirements.txt      # Python dependencies
├── .env.sample          # Environment template
└── neo4j.md            # Neo4j Docker setup

## Token Usage Tracking

DBChat3 includes comprehensive token usage tracking capabilities powered by LightRAG's TokenTracker utility and custom implementations:

### Features
- **Automatic Tracking**: Token usage is tracked automatically for all LLM operations
- **Documentation Generation Tracking**: Tracks tokens used when generating SQL documentation
- **RAG Pipeline Tracking**: Monitors tokens during document insertion and indexing
- **Per-Query Statistics**: Shows token usage after each query in chat mode
- **Session Totals**: Track cumulative token usage across chat sessions
- **Mode Comparison**: Compare token usage across different query modes
- **Configurable Display**: Control whether token usage is shown in chat

### Token Tracking Commands
- `/tokens` - Display current session token usage
- `/tokens reset` - Reset token counter to zero
- `/tokens off` - Disable token tracking for performance
- `/tokens on` - Re-enable token tracking

### Configuration
Token tracking can be configured via environment variables:
```bash
ENABLE_TOKEN_TRACKING=true       # Enable/disable token tracking globally
SHOW_TOKEN_USAGE_IN_CHAT=true   # Show usage after each query
```

### Implementation Details
- Uses context managers for automatic tracking during RAG operations
- Custom token tracking for Azure OpenAI documentation generation
- Tracks prompt tokens, completion tokens, and total tokens
- Logs token usage to application logs for monitoring
- Resets automatically at the start of each chat session
- Minimal performance overhead when enabled

### Token Tracking Coverage
1. **Documentation Generation** (`--process_database_files`):
   - Tracks tokens used for SQL to Markdown conversion
   - Reports usage for each file processed
   - Shows total documentation generation tokens

2. **RAG Pipeline** (`--run_pipeline` or `--process_database_files`):
   - Tracks tokens during document insertion
   - Monitors knowledge graph building
   - Reports RAG indexing token usage

3. **Interactive Queries** (`--chat`):
   - Per-query token tracking
   - Session totals
   - Mode-specific usage comparison

### Usage Examples

#### Processing Database Files
```bash
$ python main.py --process_database_files

Documentation Generation Token Usage:
  Total tokens: 15420
  Prompt tokens: 12890
  Completion tokens: 2530

RAG Document Insertion Token Usage:
  Total tokens: 8750
  Prompt tokens: 7200
  Completion tokens: 1550

Total Token Usage for Processing:
  Total tokens: 24170
  Prompt tokens: 20090
  Completion tokens: 4080
```

#### Interactive Chat
```
Query [hybrid]> What tables are in the database?
[... query results ...]
[Token usage - Total: 1250, Prompt: 980, Completion: 270]

Query [hybrid]> /tokens
Current Token Usage:
  Total tokens: 3420
  Prompt tokens: 2890
  Completion tokens: 530
```

This feature helps monitor API costs and optimize queries for efficiency.
```

## Usage Warnings

- **Cost Optimization**: 
  - Never run the `--run_pipeline` and the `--process_database_files` together, as it takes a lot of time and uses a paid endpoint