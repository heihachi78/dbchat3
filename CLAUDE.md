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

# Run in Jupyter notebook
jupyter notebook dbchat3.ipynb
```

## High-Level Architecture

### Core Components

1. **Documentation Generator** (`src/documentation_processor.py`): Uses Azure OpenAI (GPT-4) to convert SQL DDL files into comprehensive markdown documentation
   - Processes files from `database_files/` directory
   - Generates markdown files for each SQL object (tables, views, indexes)
   - Uses detailed system prompt for thorough documentation extraction
   - Cleans up existing docs before regeneration

2. **RAG System** (`src/rag_manager.py`): Built on LightRAG for knowledge graph-based querying
   - Uses Neo4j as graph storage backend for enhanced performance
   - Initializes storage and pipeline in `working_dir/`
   - Supports multiple query modes: naive, local, global, and hybrid
   - Uses Azure text-embedding-3-small for semantic search
   - Maintains conversation history for context-aware responses

3. **Azure OpenAI Integration** (`src/azure_client.py`):
   - `llm_model_func()`: Handles GPT-4 API calls for text generation
   - `embedding_func()`: Generates embeddings using Azure's text-embedding model
   - Configuration via environment variables in `.env`
   - Standalone functions to avoid deepcopy issues with LightRAG

4. **Configuration Management** (`src/config.py`):
   - Centralized configuration using environment variables
   - Detailed system prompt for documentation generation
   - Path management for directories and files

### Key Workflows

1. **SQL Processing Flow**:
   - Scans `database_files/` for `.sql` files recursively
   - Sends each file to Azure OpenAI with comprehensive documentation prompt
   - Saves generated markdown alongside SQL files
   - Copies processed docs to `working_dir/` for RAG ingestion

2. **RAG Initialization**:
   - Creates LightRAG instance with Azure OpenAI functions
   - Initializes vector storage and knowledge graph in `working_dir/`
   - Inserts all markdown documentation into RAG storage
   - Builds knowledge graph for semantic relationships

3. **Interactive Query Processing**:
   - Accepts natural language queries about database schema
   - Maintains conversation history for context
   - Processes through selected search mode (naive/local/global/hybrid)
   - Supports mode switching and history management commands

### Application Entry Points

- **main.py**: Command-line interface with argument parsing
- **dbchat3.ipynb**: Jupyter notebook for interactive development
- Both support the same core functionality through modular architecture

## Environment Configuration

Required environment variables in `.env`:

### Azure OpenAI Configuration
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_OPENAI_DEPLOYMENT` (GPT-4 model)
- `AZURE_EMBEDDING_DEPLOYMENT`
- `AZURE_EMBEDDING_API_VERSION`

### Neo4j Configuration
- `NEO4J_URI` (default: "neo4j://localhost:7687")
- `NEO4J_USERNAME` (default: "neo4j")
- `NEO4J_PASSWORD` (required)
- `NEO4J_DATABASE` (default: "neo4j")

**Note**: LightRAG uses Neo4j Community Edition with the default database. The system is configured to use `graph_storage="Neo4JStorage"` with explicit connection parameters to ensure compatibility with Community Edition, which doesn't support creating new databases.

### Optional Settings
- `LOG_DIR` (optional, defaults to "logs")

## Important Patterns

- **Neo4j Graph Storage**: Uses Neo4j instead of NetworkX for better performance and scalability
- **Configuration Validation**: Validates Neo4j connection settings on startup
- Embedding dimension set to 3072 for text-embedding-3-small
- Comprehensive logging throughout for debugging (file + console)
- Error handling for file operations and API calls
- Automatic directory creation for `working_dir` if missing
- Standalone async functions for LightRAG compatibility
- Conversation history maintenance in interactive mode
- Comprehensive system prompt for detailed documentation extraction

## Neo4j Setup

To run Neo4j locally using Docker:

```bash
docker run -d --restart always --publish=7474:7474 --publish=7687:7687 \
  --env NEO4J_AUTH=neo4j/your_password \
  --volume=/path/to/data:/data \
  neo4j:latest
```

- Neo4j Browser: http://localhost:7474
- Bolt connection: neo4j://localhost:7687
- Default credentials: neo4j/your_password

## Interactive Chat Commands

When in chat mode (`python main.py --chat`):
- `exit`, `quit`, `q` - Exit the application
- `/mode <mode>` - Change query mode (naive|local|global|hybrid)
- `/clear` - Clear conversation history
- `/history` - Show conversation history
- `modes` - Test query with all modes