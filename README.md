# DBChat3 - Database Documentation RAG System

A powerful Python application that automatically generates comprehensive database documentation using AI and provides intelligent querying capabilities through Retrieval-Augmented Generation (RAG) using LightRAG with Neo4j graph storage.

## Overview

DBChat3 combines Azure OpenAI services with LightRAG to create an intelligent database documentation and querying system. It automatically processes SQL DDL files, generates detailed markdown documentation, and enables natural language queries about your database schema through a knowledge graph stored in Neo4j.

## Features

- **Automatic Documentation Generation**: Converts SQL DDL files into comprehensive markdown documentation using Azure OpenAI (GPT-4)
- **Neo4j Graph Storage**: Enhanced performance and scalability with Neo4j as the knowledge graph backend
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
3. **Knowledge Graph Building**: Processes documentation through LightRAG to build a knowledge graph in Neo4j
4. **Query Interface**: Enables natural language queries with multiple search strategies and conversation history

## Prerequisites

- Python 3.8+
- Azure OpenAI account with API access
- GPT-4 deployment for text generation
- Text embedding model deployment (text-embedding-3-large)
- Neo4j database (Community Edition supported)
- Docker (optional, for running Neo4j locally)

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

4. **Set up Neo4j** (using Docker):
   ```bash
   docker run -d --restart always --publish=7474:7474 --publish=7687:7687 \
     --env NEO4J_AUTH=neo4j/pass4jdbchat \
     --volume=/home/tothi/python/dbchat3/data:/data \
     neo4j:2025.06.2
   ```
   - Neo4j Browser: http://localhost:7474
   - Bolt connection: neo4j://localhost:7687

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
AZURE_OPENAI_DEPLOYMENT=gpt-4.1
AZURE_EMBEDDING_DEPLOYMENT=text-embedding-3-large
AZURE_EMBEDDING_API_VERSION=2024-02-01
AZURE_EMBEDDING_DIMENSION=3072
```

### Neo4j Configuration
```bash
NEO4J_URI=neo4j://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=pass4jdbchat
NEO4J_DATABASE=neo4j
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
│   └── rag_manager.py     # LightRAG integration
├── database_files/        # Input SQL DDL files
│   └── sampledb/         # Sample database with HR schema
├── working_dir/          # Generated docs and RAG storage
│   ├── *.md              # Processed documentation
│   ├── faiss_index_*.index  # Vector indexes
│   └── kv_store_*.json   # Document stores
├── data/                 # Neo4j database files
├── logs/                 # Application logs
├── requirements.txt      # Python dependencies
├── .env.sample          # Environment template
├── README.md             # This file
├── CLAUDE.md            # AI assistant instructions
└── neo4j.md             # Neo4j setup guide
```

## Key Components

### Documentation Generation
- Uses a specialized system prompt for comprehensive database documentation
- Extracts all DDL information including comments, constraints, and relationships
- Generates structured markdown with clear sections and business context
- Tracks token usage for cost monitoring

### RAG System
- Built on LightRAG for advanced knowledge graph capabilities
- Uses Neo4j for scalable graph storage and querying
- Supports multiple embedding and search strategies
- Maintains conversation context and semantic understanding
- Clears Neo4j database on initialization for clean state

### Azure OpenAI Integration
- GPT-4 for high-quality documentation generation
- text-embedding-3-large for semantic search capabilities
- Standalone async functions for LightRAG compatibility
- Configurable parameters for consistent results

## Usage Warnings

- **Cost Optimization**: 
  - Never run `--run_pipeline` and `--process_database_files` together (duplicates processing)
  - Use `--run_pipeline` when markdown files already exist
  - Monitor token usage with `/tokens` command
  
- **Neo4j Database**: 
  - System clears Neo4j database on each initialization
  - Use Docker volumes to persist data between restarts
  
- **Memory Usage**:
  - Large databases may require processing in batches
  - FAISS indexes are loaded into memory

## Dependencies

Key dependencies include:

- `lightrag-hku`: Advanced RAG framework with knowledge graph support
- `openai`: Azure OpenAI client library
- `neo4j`: Neo4j Python driver for graph database
- `numpy`: Numerical computing for embeddings
- `asyncio`: Asynchronous programming support
- `python-dotenv`: Environment variable management
- `faiss-cpu`: Vector similarity search

## Troubleshooting

### Common Issues

1. **API Key Issues**: Ensure your Azure OpenAI credentials are correctly set in `.env`
2. **Model Availability**: Verify your deployments match the model names in configuration
3. **Neo4j Connection**: Check Neo4j is running and credentials are correct
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
- Review Neo4j setup in `neo4j.md`
- Open an issue in the repository

---

**Note**: This project requires active Azure OpenAI subscriptions and may incur API costs based on usage. Monitor token usage regularly to manage costs effectively.