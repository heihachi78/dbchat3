# DBChat3 - Database Documentation RAG System

A powerful Python application that automatically generates comprehensive database documentation using AI and provides intelligent querying capabilities through Retrieval-Augmented Generation (RAG) using LightRAG with hybrid storage architecture.

## Overview

DBChat3 combines multiple LLM providers (Azure OpenAI and Ollama) with LightRAG to create an intelligent database documentation and querying system. It automatically processes SQL DDL files, generates detailed markdown documentation, and enables natural language queries about your database schema through a knowledge graph.

## Features

- **Dual LLM Provider Support**: Choose between Azure OpenAI (cloud) or Ollama (local) for AI processing
- **Automatic Documentation Generation**: Converts SQL DDL files into comprehensive markdown documentation
- **Hybrid Storage Architecture**: 
  - Neo4j for knowledge graph relationships and entity connections
  - MongoDB for document metadata and key-value storage
  - FAISS for high-performance vector search and semantic matching
- **RAG-Powered Querying**: Query your database schema using natural language with four search modes
- **Multi-Modal Search**: Supports naive, local, global, and hybrid search strategies
- **Schema Analysis**: Provides detailed analysis of tables, views, indexes, functions, and relationships
- **Interactive Chat Interface**: Command-line chat with conversation history and mode switching
- **Comprehensive Token Usage Tracking**: Monitor API costs and usage patterns with detailed statistics
- **Configuration Validation**: Automatic validation of all required settings on startup
- **Error Handling & Timeouts**: Robust error handling with configurable timeouts and retry logic
- **Docker Integration**: Easy database setup with Docker Compose

## Architecture

The system follows this workflow:

1. **Input Processing**: Reads SQL DDL files from the `database_files` directory structure
2. **Documentation Generation**: Uses AI (Azure OpenAI or Ollama) to generate detailed markdown documentation for each SQL object
3. **Knowledge Graph Building**: Processes documentation through LightRAG with hybrid storage:
   - Neo4j stores relationship graphs and entity connections
   - MongoDB manages document processing status and key-value operations
   - FAISS handles vector embeddings for fast semantic search
4. **Query Interface**: Enables natural language queries with multiple search strategies and conversation context

## Prerequisites

### Core Requirements
- Python 3.8+
- Neo4j database (Community Edition supported)
- MongoDB database for document metadata
- Docker (recommended for running databases locally)

### LLM Provider Requirements

Choose one of the following:

**Option A: Azure OpenAI (Recommended for production)**
- Azure OpenAI account with API access
- GPT-4 or GPT-4.1-mini deployment for text generation
- Text embedding model deployment (text-embedding-3-small or text-embedding-3-large)

**Option B: Ollama (Local deployment)**
- Ollama installation (https://ollama.ai)
- Local models: LLM model (e.g., qwen3:4b, llama2:latest) and embedding model (e.g., nomic-embed-text:latest)
- Sufficient hardware for local model inference

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd dbchat3
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up databases using Docker Compose** (recommended):
   ```bash
   docker-compose up -d
   ```
   This will start both Neo4j and MongoDB with the correct configuration.
   
   **Or manually run each database**:
   
   Neo4j:
   ```bash
   docker run -d --restart always --publish=7474:7474 --publish=7687:7687 \
     --env NEO4J_AUTH=neo4j/yourneo4jpass \
     --volume=$PWD/data/neo4j:/data \
     neo4j:2025.06.2
   ```
   
   MongoDB:
   ```bash
   docker run -d --restart always -p 27017:27017 \
     -e MONGO_INITDB_ROOT_USERNAME=mongoadmin \
     -e MONGO_INITDB_ROOT_PASSWORD=yourmongopass \
     -v $PWD/data/mongodb:/data/db \
     mongo
   ```
   
   **Access Points**:
   - Neo4j Browser: http://localhost:7474
   - Neo4j Bolt: neo4j://localhost:7687
   - MongoDB: mongodb://mongoadmin:yourmongopass@localhost:27017/

5. **Configure environment variables**:
   ```bash
   cp sample_env_file.txt .env
   # Edit .env with your credentials and LLM provider choice
   ```

## Configuration

### LLM Provider Selection

Set your preferred LLM provider in `.env`:

```bash
# Choose your LLM provider: "azure" or "ollama"
LLM_PROVIDER=azure  # or "ollama"
```

### Azure OpenAI Configuration (if using Azure)

```bash
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2025-01-01-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini
AZURE_EMBEDDING_DEPLOYMENT=text-embedding-3-small
AZURE_EMBEDDING_API_VERSION=2024-02-01
```

### Ollama Configuration (if using Ollama)

```bash
OLLAMA_HOST=http://localhost:11434
OLLAMA_LLM_MODEL=qwen3:4b
OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest
OLLAMA_TIMEOUT=300
OLLAMA_NUM_CTX=32768
```

**Important**: Ensure your Ollama models are pulled before use:
```bash
ollama pull qwen3:4b
ollama pull nomic-embed-text:latest
```

**Context Window Configuration**:
- `OLLAMA_NUM_CTX`: Context window size in tokens (default: 32768)
- Larger values enable processing longer documents but use more memory
- Reduce to 8192 or 16384 for faster processing with shorter documents

### Database Configuration

```bash
# Neo4j Configuration
NEO4J_URI=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=yourneo4jpass
NEO4J_WORKSPACE=neo4j

# MongoDB Configuration
MONGO_USER=mongoadmin
MONGO_PASS=yourmongopass
MONGO_URI=mongodb://mongoadmin:yourmongopass@localhost:27017/
```

### Model Settings

```bash
# Must match your embedding model's output dimension
# Azure text-embedding-3-small: 1536
# Ollama nomic-embed-text: 768
EMBEDDING_DIMENSION=1536
```

### Optional Settings

```bash
# Token tracking
ENABLE_TOKEN_TRACKING=true
SHOW_TOKEN_USAGE_IN_CHAT=true

# Logging
LOG_DIR=logs
```

## Usage

### Command Line Interface

The application supports several command-line modes:

```bash
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
```

### Directory Structure

Organize your SQL files in the `database_files` directory:

```
database_files/
├── sampledb/
│   └── hr/
│       ├── table/
│       │   ├── hr.employees.sql
│       │   ├── hr.departments.sql
│       │   └── ...
│       ├── view/
│       │   └── hr.emp_details_view.sql
│       ├── index/
│       │   ├── hr.emp_name_ix.sql
│       │   └── ...
│       └── function/
│           └── hr.get_employee_name.sql
```

### Interactive Chat Commands

When in chat mode (`python main.py --chat`):

- **Query Commands**:
  - Type your natural language query and press Enter
  - `exit`, `quit`, `q` - Exit the application
  
- **Mode Commands**:
  - `/mode <mode>` - Change query mode (naive|local|global|hybrid)
  - `modes` - Test query with all modes simultaneously
  
- **History Commands**:
  - `/clear` - Clear conversation history
  - `/history` - Show conversation history
  
- **Token Tracking Commands**:
  - `/tokens` - Show current session token usage
  - `/tokens reset` - Reset token counter
  - `/tokens summary` - Show detailed token breakdown
  - `/tokens off` - Disable token tracking display
  - `/tokens on` - Enable token tracking display

### Query Modes

The system supports four different query modes:

- **Naive**: Simple text matching without context
- **Local**: Context-aware local search within documents
- **Global**: Knowledge graph-based global search across relationships
- **Hybrid**: Combines local and global approaches for best results (recommended)

### Example Queries

```
# Database structure queries
"What tables are in the database?"
"Show me the employee table structure"
"What columns does the departments table have?"

# Relationship queries
"What are the relationships between departments and employees?"
"How are employees linked to their managers?"
"Show me all foreign key relationships"

# Index and performance queries
"List all indexes in the HR schema"
"What indexes exist on the employees table?"
"Are there any unique constraints?"

# Business logic queries
"What views are available in the database?"
"Show me all stored functions"
"What does the emp_details_view contain?"
```

## Performance Considerations

### Azure OpenAI vs Ollama

**Azure OpenAI (Recommended)**:
- ✅ Fast processing and response times
- ✅ High-quality results with GPT-4 models
- ✅ Reliable and consistent performance
- ❌ Requires API costs and internet connection

**Ollama (Local)**:
- ✅ No API costs or internet dependency
- ✅ Full data privacy and control
- ⚠️ **Significantly slower processing times**
- ⚠️ **May hang during knowledge graph extraction**
- ❌ Requires powerful hardware for good performance

### Ollama Performance Warnings

When using Ollama:
- **Initial processing can take hours**: The first document processing triggers extensive knowledge graph extraction
- **High CPU usage**: Monitor system resources during processing
- **Potential hanging**: `--run_pipeline` may hang indefinitely during complex knowledge extraction
- **Workaround**: Use Azure OpenAI for initial setup, then switch to Ollama for queries

### Cost Optimization

- **Never run both flags together**: Don't use `--process_database_files` and `--run_pipeline` simultaneously (duplicates processing)
- **Use `--run_pipeline`**: When markdown files already exist in `working_dir/`
- **Monitor token usage**: Use `/tokens` command in chat mode to track API costs
- **Process in batches**: For large databases, consider processing in smaller batches

## Token Usage Tracking

DBChat3 includes comprehensive token usage tracking:

### Features
- Automatic tracking for all LLM operations
- Per-query statistics in chat mode
- Session totals and cumulative tracking
- Mode comparison for optimization
- Configurable display options

### Example Output
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

### Processing Statistics
When processing database files, you'll see:
```
Documentation Generation Token Usage:
  Total tokens: 15420
  Prompt tokens: 12890
  Completion tokens: 2530

RAG Document Insertion Token Usage:
  Total tokens: 8750
  Prompt tokens: 7200
  Completion tokens: 1550
```

## Output

The system generates:

1. **Markdown Documentation**: Detailed documentation for each SQL object alongside source files
2. **Working Directory**: Processed files and knowledge graphs in `working_dir/`
   - High-performance FAISS vector indexes for fast semantic search
   - Key-value stores for document management
   - Neo4j graph database for relationships
3. **Query Results**: Natural language responses with source citations
4. **Logs**: Detailed application logs in `logs/` directory with timestamps

## Project Structure

```
dbchat3/
├── main.py                 # Main entry point with CLI
├── src/
│   ├── __init__.py        # Module initialization
│   ├── azure_client.py    # Azure OpenAI client wrapper
│   ├── azure_factory.py   # Factory for creating Azure clients
│   ├── ollama_client.py   # Ollama client wrapper
│   ├── ollama_factory.py  # Factory for creating Ollama clients
│   ├── config.py          # Configuration management with validation
│   ├── documentation_processor.py  # SQL to Markdown conversion
│   ├── rag_manager.py     # LightRAG integration with hybrid storage
│   ├── retry_utils.py     # Retry logic utilities
│   └── token_aggregator.py # Token usage tracking and reporting
├── database_files/        # Input SQL DDL files
│   └── sampledb/hr/      # Sample HR schema with SQL/MD files
│       ├── table/        # Table definitions
│       ├── view/         # View definitions  
│       ├── index/        # Index definitions
│       └── function/     # Function definitions
├── working_dir/          # Generated docs and RAG storage
│   ├── *.md              # Processed documentation
│   ├── faiss_index_*.index  # FAISS vector indexes
│   └── faiss_index_*.index.meta.json # FAISS metadata
├── data/                 # Database data (managed via Docker volumes)
│   ├── neo4j/           # Neo4j database files
│   └── mongodb/         # MongoDB database files
├── logs/                 # Application logs (timestamped)
├── requirements.txt      # Python dependencies
├── sample_env_file.txt   # Environment template with documentation
├── docker-compose.yml   # Docker Compose configuration
├── README.md             # This file
└── CLAUDE.md            # AI assistant instructions
```

## Key Components

### Documentation Generation
- Uses specialized system prompts for comprehensive database documentation
- Extracts all DDL information including comments, constraints, and relationships
- Generates structured markdown with clear sections and business context
- Tracks token usage for cost monitoring

### RAG System
- Built on LightRAG with hybrid storage architecture:
  - **Neo4j**: Stores knowledge graph relationships and entity connections
  - **MongoDB**: Manages document processing status and key-value operations
  - **FAISS**: Provides high-performance vector similarity search
- Supports multiple embedding and search strategies
- Maintains conversation context and semantic understanding
- Clears databases on initialization for clean state
- Automatic storage initialization and management

### LLM Provider Integration
- **Azure OpenAI**: GPT-4 for documentation, text-embedding-3-small for semantic search
- **Ollama**: Local models with configurable endpoints and timeouts
- Unified interface with shared client factories
- Standalone async functions for LightRAG compatibility
- Comprehensive error handling and retry logic

## Database Management

### Initialization Behavior
- System clears Neo4j and MongoDB databases on each initialization
- Ensures clean state for consistent results
- Use Docker volumes to persist data between container restarts
- Both databases start fresh with each pipeline run

### Docker Integration
- Docker Compose simplifies multi-database setup
- Persistent volumes maintain data across container restarts
- Environment variable integration for easy configuration
- Health checks and automatic restart policies

## Troubleshooting

### Common Issues

1. **Configuration Errors**: 
   - Check that all required environment variables are set in `.env`
   - Ensure `LLM_PROVIDER` matches your chosen provider configuration
   - Verify `EMBEDDING_DIMENSION` matches your embedding model

2. **API Key Issues**: 
   - Ensure your Azure OpenAI credentials are correctly set
   - Verify your deployments match the model names in configuration

3. **Ollama Issues**:
   - Ensure Ollama is running: `ollama serve`
   - Check models are pulled: `ollama list`
   - Monitor for high CPU usage during processing
   - Consider switching to Azure OpenAI if hanging occurs

4. **Database Connection Issues**: 
   - Check Neo4j is running and accessible at port 7687
   - Verify MongoDB is running at port 27017
   - Ensure credentials match those in `.env` file
   - Use `docker-compose ps` to check container status

5. **Performance Issues**: 
   - Large databases may require processing in batches
   - Monitor token usage to manage API costs
   - Consider using Azure OpenAI for better performance

### Logging

Comprehensive logging is available:
- Console output for real-time feedback
- File logs in `logs/` directory with timestamps
- Token usage tracking in logs for cost monitoring
- Debug-level logging for troubleshooting

### Performance Monitoring

Monitor system performance:
- Check Ollama process CPU usage: `ps aux | grep ollama`
- Monitor database connections and response times
- Track token usage patterns for optimization
- Use Docker stats for container resource monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Add your license information here]

## Support

For issues and questions:
- Check the troubleshooting section
- Review configuration documentation in `sample_env_file.txt`
- Review database setup in Docker Compose configuration
- Check LLM provider documentation (Azure OpenAI or Ollama)
- Open an issue in the repository

---

**Note**: This project supports both cloud-based (Azure OpenAI) and local (Ollama) LLM providers. Azure OpenAI is recommended for production use due to performance and reliability, while Ollama provides a cost-effective local alternative with trade-offs in processing speed. Monitor token usage and system resources to optimize costs and performance based on your specific requirements.