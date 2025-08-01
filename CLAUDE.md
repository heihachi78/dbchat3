# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

DBChat3 is a Python application that generates database documentation using Azure OpenAI and enables intelligent querying through LightRAG. It processes SQL DDL files to create comprehensive markdown documentation and builds a knowledge graph for natural language queries.

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the main application
python dbchat3.py

# Run in Jupyter notebook
jupyter notebook dbchat3.ipynb
```

## High-Level Architecture

### Core Components

1. **Documentation Generator**: Uses Azure OpenAI (GPT-4) to convert SQL DDL files into comprehensive markdown documentation
   - Processes files from `database_files/` directory
   - Generates markdown files for each SQL object (tables, views, indexes)
   - Uses detailed system prompt for thorough documentation extraction

2. **RAG System**: Built on LightRAG for knowledge graph-based querying
   - Initializes storage and pipeline in `working_dir/`
   - Supports multiple query modes: naive, local, global, and hybrid
   - Uses Azure text-embedding-3-small for semantic search

3. **Azure OpenAI Integration**:
   - `llm_model_func()`: Handles GPT-4 API calls for text generation
   - `embedding_func()`: Generates embeddings using Azure's text-embedding model
   - Configuration via environment variables in `.env`

### Key Workflows

1. **SQL Processing Flow**:
   - Scans `database_files/` for `.sql` files
   - Sends each file to Azure OpenAI with documentation prompt
   - Saves generated markdown alongside SQL files
   - Copies processed docs to `working_dir/`

2. **RAG Initialization**:
   - Creates LightRAG instance with Azure OpenAI functions
   - Initializes vector storage and knowledge graph
   - Inserts all markdown documentation into RAG storage

3. **Query Processing**:
   - Accepts natural language queries about database schema
   - Processes through selected search mode (naive/local/global/hybrid)
   - Returns contextual answers based on documentation

## Environment Configuration

Required environment variables in `.env`:
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_OPENAI_DEPLOYMENT` (GPT-4 model)
- `AZURE_EMBEDDING_DEPLOYMENT`
- `AZURE_EMBEDDING_API_VERSION`

## Important Patterns

- Uses `nest_asyncio` for async operations in Jupyter environments
- Embedding dimension set to 3072 for text-embedding-3-small
- Comprehensive logging throughout for debugging
- Error handling for file operations and API calls
- Automatic directory creation for `working_dir` if missing