# DBChat3 - Database Documentation RAG System

A powerful Python application that automatically generates comprehensive database documentation using AI and provides intelligent querying capabilities through Retrieval-Augmented Generation (RAG) using LightRAG with Neo4j graph storage.

## Overview

DBChat3 combines Azure OpenAI services with LightRAG to create an intelligent database documentation and querying system. It automatically processes SQL DDL files, generates detailed markdown documentation, and enables natural language queries about your database schema through a knowledge graph stored in Neo4j.

## Features

- **Automatic Documentation Generation**: Converts SQL DDL files into comprehensive markdown documentation using Azure OpenAI (GPT-4)
- **Hybrid Storage Architecture**: 
  - Neo4j for knowledge graph relationships
  - MongoDB for key-value storage and document status tracking
  - FAISS for high-performance vector search
- **RAG-Powered Querying**: Query your database schema using natural language with multiple search modes
- **Multi-Modal Search**: Supports naive, local, global, and hybrid search modes
- **Schema Analysis**: Provides detailed analysis of tables, views, indexes, functions, and relationships
- **Interactive Chat Interface**: Command-line chat with conversation history and mode switching
- **Token Usage Tracking**: Monitor API costs with built-in token tracking and reporting
- **Azure OpenAI Integration**: Leverages GPT-4 and text-embedding-3-large models for high-quality results

## Architecture

The system follows this workflow:

1. **Input Processing**: Reads SQL DDL files from the `database_files` directory
2. **Documentation Generation**: Uses Azure OpenAI to generate detailed markdown documentation for each SQL object
3. **Knowledge Graph Building**: Processes documentation through LightRAG with hybrid storage:
   - Neo4j stores relationship graph data
   - MongoDB manages document status and key-value data
   - FAISS handles vector embeddings for semantic search
4. **Query Interface**: Enables natural language queries with multiple search strategies and conversation history

## Prerequisites

- Python 3.8+
- Azure OpenAI account with API access
- GPT-4.1-mini deployment for text generation
- Text embedding model deployment (text-embedding-3-small)
- Neo4j database (Community Edition supported)
- MongoDB database for key-value storage
- Docker (recommended for running Neo4j and MongoDB locally)

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
   cp .env.sample .env
   # Edit .env with your credentials
   ```

## Configuration

Update the `.env` file with your settings:

### Azure OpenAI Configuration
```bash
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2025-01-01-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini
AZURE_EMBEDDING_DEPLOYMENT=text-embedding-3-small
AZURE_EMBEDDING_API_VERSION=2024-02-01
AZURE_EMBEDDING_DIMENSION=1536
```

### Neo4j Configuration
```bash
NEO4J_URI=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=yourneo4jpass
NEO4J_WORKSPACE=neo4j
```

### MongoDB Configuration
```bash
MONGO_USER=mongoadmin
MONGO_PASS=yourmongopass
MONGO_URI=mongodb://mongoadmin:yourmongopass@localhost:27017/
```

### Token Tracking Settings
```bash
ENABLE_TOKEN_TRACKING=true
SHOW_TOKEN_USAGE_IN_CHAT=true
```

### Optional Settings
```bash
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
  - `/tokens` - Show current token usage
  - `/tokens reset` - Reset token counter
  - `/tokens off` - Disable token tracking
  - `/tokens on` - Enable token tracking

### Query Modes

The system supports four different query modes:

- **Naive**: Simple text matching without context
- **Local**: Context-aware local search within documents
- **Global**: Knowledge graph-based global search across relationships
- **Hybrid**: Combines local and global approaches for best results

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
4. **Logs**: Detailed application logs in `logs/` directory

## Project Structure

```
dbchat3/
├── main.py                 # Main entry point with CLI
├── src/
│   ├── __init__.py        # Module initialization
│   ├── azure_client.py    # Azure OpenAI client wrapper
│   ├── azure_factory.py   # Factory for creating clients
│   ├── config.py          # Configuration management
│   ├── documentation_processor.py  # SQL to Markdown conversion
│   ├── rag_manager.py     # LightRAG integration
│   ├── retry_utils.py     # Retry logic utilities
│   └── token_aggregator.py # Token usage tracking
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
├── data/                 # Database data (committed via Git LFS)
│   ├── neo4j/           # Neo4j database files
│   │   ├── databases/   # Neo4j database storage
│   │   ├── transactions/ # Transaction logs (256MB files)
│   │   └── dbms/        # Database management
│   └── mongodb/         # MongoDB database files
│       ├── db/          # Database files
│       └── configdb/    # Configuration database
├── logs/                 # Application logs (timestamped)
├── requirements.txt      # Python dependencies
├── .env.sample          # Environment template
├── .gitattributes       # Git LFS configuration
├── docker-compose.yml   # Docker Compose configuration
├── README.md             # This file
└── CLAUDE.md            # AI assistant instructions
```

## Key Components

### Documentation Generation
- Uses a specialized system prompt for comprehensive database documentation
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
- Clears both Neo4j and MongoDB databases on initialization for clean state
- Automatic storage initialization and management

### Azure OpenAI Integration
- GPT-4 for high-quality documentation generation
- text-embedding-3-small for semantic search capabilities
- Standalone async functions for LightRAG compatibility
- Configurable parameters for consistent results

## Usage Warnings

- **Cost Optimization**: 
  - Never run `--run_pipeline` and `--process_database_files` together (duplicates processing)
  - Use `--run_pipeline` when markdown files already exist
  - Monitor token usage with `/tokens` command
  
- **Database Management**: 
  - System clears both Neo4j and MongoDB databases on each initialization
  - Use Docker volumes to persist data between container restarts
  - Docker Compose simplifies multi-database setup
  - Both databases start fresh with each pipeline run
  
- **Memory Usage**:
  - Large databases may require processing in batches
  - FAISS indexes are loaded into memory

## Dependencies

Key dependencies include:

- `lightrag-hku`: Advanced RAG framework with knowledge graph support
- `openai`: Azure OpenAI client library
- `neo4j`: Neo4j Python driver for graph database
- `pymongo`: MongoDB Python driver
- `numpy`: Numerical computing for embeddings
- `asyncio`: Asynchronous programming support
- `python-dotenv`: Environment variable management
- `faiss-cpu`: High-performance vector similarity search

## Troubleshooting

### Common Issues

1. **API Key Issues**: Ensure your Azure OpenAI credentials are correctly set in `.env`
2. **Model Availability**: Verify your deployments match the model names in configuration
3. **Database Connections**: 
   - Check Neo4j is running and accessible at port 7687
   - Verify MongoDB is running at port 27017
   - Ensure credentials match those in `.env` file
   - Use `docker-compose ps` to check container status
4. **File Permissions**: Ensure read/write access to working directories
5. **Memory Issues**: Large databases may require chunking or batch processing

### Logging

Comprehensive logging is available:
- Console output for real-time feedback
- File logs in `logs/` directory with timestamps
- Token usage tracking in logs for cost monitoring

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
- Review Azure OpenAI documentation
- Review database setup in Docker Compose configuration
- Open an issue in the repository

---

**Note**: This project requires active Azure OpenAI subscriptions and may incur API costs based on usage. Monitor token usage regularly to manage costs effectively.