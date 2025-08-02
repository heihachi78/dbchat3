# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

DBChat3 is a database documentation RAG system that uses Azure OpenAI to generate comprehensive documentation from SQL DDL files and provides intelligent querying through LightRAG with hybrid storage (Neo4j graph + MongoDB + FAISS vectors).

## Key Commands

### Running the Application
```bash
# Process database files and generate documentation (full pipeline)
python main.py --process_database_files

# Run RAG pipeline only (assumes .md files already exist in working_dir)
python main.py --run_pipeline

# Start interactive chat mode
python main.py --chat

# Process files and immediately start chat
python main.py --process_database_files --chat
```

### Database Management
```bash
# Start both databases (recommended approach)
docker-compose up -d

# Check database status
docker-compose ps

# Stop databases
docker-compose down

# View logs
docker-compose logs neo4j
docker-compose logs mongodb
```

### Development Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows
```

## Architecture Overview

### Core Components

1. **main.py**: Entry point with CLI argument parsing, orchestrates the entire pipeline
   - `process_database_files()`: Full pipeline - generates docs and builds RAG
   - `run_pipeline()`: RAG-only pipeline when docs already exist
   - `interactive_chat()`: Interactive query interface

2. **src/documentation_processor.py**: Converts SQL DDL to markdown documentation
   - Processes files from `database_files/` directory
   - Outputs markdown to `working_dir/`
   - Uses Azure OpenAI GPT-4 with specialized prompt

3. **src/rag_manager.py**: Manages LightRAG with hybrid storage
   - Neo4j for knowledge graph relationships
   - MongoDB for document status and key-value operations
   - FAISS for vector similarity search
   - Clears both databases on initialization for clean state

4. **src/azure_client.py**: Azure OpenAI client wrapper
   - Handles GPT-4 text generation
   - Manages text-embedding-3-large embeddings
   - Tracks token usage for cost monitoring

5. **src/azure_factory.py**: Creates standalone async functions for LightRAG
   - Required because LightRAG expects functions, not class methods
   - Provides `text_func` and `embedding_func` with proper signatures

6. **src/config.py**: Central configuration management
   - Loads from `.env` file
   - Validates all required settings
   - Contains the system prompt for documentation generation

### Storage Architecture

- **Neo4j**: Graph database for entity relationships and knowledge graph
- **MongoDB**: Document store for processing status and key-value operations
- **FAISS**: Vector indexes for semantic search (stored in `working_dir/`)
- **Working Directory**: Contains generated .md files and FAISS indexes

### Query Modes

- **naive**: Simple text matching
- **local**: Context-aware search within documents
- **global**: Knowledge graph traversal across relationships
- **hybrid**: Combines local and global approaches

## Important Implementation Details

1. **Database Initialization**: Both Neo4j and MongoDB are cleared on each pipeline run to ensure clean state

2. **Token Tracking**: Enable with `ENABLE_TOKEN_TRACKING=true` in .env
   - Tracks usage for documentation generation separately from RAG operations
   - Display in chat with `SHOW_TOKEN_USAGE_IN_CHAT=true`

3. **File Organization**: SQL files must follow this structure:
   ```
   database_files/
   └── <database_name>/
       └── <schema_name>/
           ├── table/
           ├── view/
           ├── index/
           └── function/
   ```

4. **Async Architecture**: LightRAG requires async functions, handled via:
   - `asyncio.run()` in main.py
   - Standalone async functions in azure_factory.py
   - Motor (async MongoDB driver) for database operations

5. **Error Handling**: 
   - Configuration validation before startup
   - Graceful handling of missing files
   - Proper database connection error messages

## Environment Variables

Required in `.env`:
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_DEPLOYMENT` (GPT-4 model)
- `AZURE_EMBEDDING_DEPLOYMENT` (text-embedding-3-large)
- `NEO4J_PASSWORD`
- `MONGO_USER` and `MONGO_PASS`

## Common Issues and Solutions

1. **Import Errors**: Ensure virtual environment is activated
2. **Database Connection Failed**: Check Docker containers are running
3. **API Errors**: Verify Azure OpenAI deployments match configuration
4. **Memory Issues**: Large databases may require batch processing
5. **Token Limits**: Monitor usage with `/tokens` command in chat