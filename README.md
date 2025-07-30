# DBChat3 - Database Documentation RAG System

A powerful Python application that automatically generates comprehensive database documentation using AI and provides intelligent querying capabilities through Retrieval-Augmented Generation (RAG) using LightRAG.

## Overview

DBChat3 combines Azure OpenAI services with LightRAG to create an intelligent database documentation and querying system. It automatically processes SQL DDL files, generates detailed markdown documentation, and enables natural language queries about your database schema.

## Features

- **Automatic Documentation Generation**: Converts SQL DDL files into comprehensive markdown documentation using Azure OpenAI
- **RAG-Powered Querying**: Query your database schema using natural language with multiple search modes
- **Multi-Modal Search**: Supports naive, local, global, and hybrid search modes
- **Schema Analysis**: Provides detailed analysis of tables, views, indexes, and relationships
- **Azure OpenAI Integration**: Leverages GPT-4 and text-embedding models for high-quality results

## Architecture

The system follows this workflow:

1. **Input Processing**: Reads SQL DDL files from the `database_files` directory
2. **Documentation Generation**: Uses Azure OpenAI to generate detailed markdown documentation for each SQL object
3. **Knowledge Graph Building**: Processes documentation through LightRAG to build a knowledge graph
4. **Query Interface**: Enables natural language queries with multiple search strategies

## Prerequisites

- Python 3.8+
- Azure OpenAI account with API access
- GPT-4 deployment for text generation
- Text embedding model deployment (text-embedding-3-small)

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

4. **Configure environment variables**:
   ```bash
   cp .env.sample .env
   # Edit .env with your Azure OpenAI credentials
   ```

## Configuration

Update the `.env` file with your Azure OpenAI settings:

```bash
AZURE_OPENAI_API_KEY=your_api_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_VERSION=2025-01-01-preview
AZURE_OPENAI_DEPLOYMENT=gpt-4.1-mini

AZURE_EMBEDDING_DEPLOYMENT=text-embedding-3-small
AZURE_EMBEDDING_API_VERSION=2023-05-15
```

## Usage

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
│       └── index/
│           ├── hr.emp_name_ix.sql
│           └── ...
```

### Running the Application

1. **Basic execution**:
   ```bash
   python dbchat3.py
   ```

2. **Jupyter Notebook**:
   ```bash
   jupyter notebook dbchat3.ipynb
   ```

### Query Modes

The system supports four different query modes:

- **Naive**: Simple text matching
- **Local**: Context-aware local search
- **Global**: Knowledge graph-based global search  
- **Hybrid**: Combines local and global approaches

### Example Queries

```python
# Example queries you can ask:
query_text = "What tables are in the database?"
query_text = "Show me the employee table structure"
query_text = "What are the relationships between departments and employees?"
query_text = "List all indexes in the HR schema"
```

## Output

The system generates:

1. **Markdown Documentation**: Detailed documentation for each SQL object in `database_files/`
2. **Working Directory**: Processed files and knowledge graphs in `working_dir/`
3. **Query Results**: Natural language responses to your database questions

## Project Structure

```
dbchat3/
├── dbchat3.py              # Main application script
├── dbchat3.ipynb           # Jupyter notebook version
├── requirements.txt        # Python dependencies
├── .env.sample            # Environment variables template
├── database_files/        # Input SQL DDL files
│   └── sampledb/         # Sample HR database schema
└── working_dir/          # Generated documentation and indexes
```

## Key Components

### Documentation Generation
- Uses a specialized system prompt for comprehensive database documentation
- Extracts all DDL information including comments, constraints, and relationships
- Generates structured markdown with clear sections and business context

### RAG System
- Built on LightRAG for advanced knowledge graph capabilities
- Supports multiple embedding and search strategies
- Maintains conversation context and semantic understanding

### Azure OpenAI Integration
- GPT-4 for high-quality documentation generation
- Text-embedding-3-small for semantic search capabilities
- Configurable temperature and parameters for consistent results

## Dependencies

Key dependencies include:

- `lightrag-hku`: Advanced RAG framework with knowledge graph support
- `openai`: Azure OpenAI client library
- `numpy`: Numerical computing for embeddings
- `asyncio`: Asynchronous programming support
- `python-dotenv`: Environment variable management

## Troubleshooting

### Common Issues

1. **API Key Issues**: Ensure your Azure OpenAI credentials are correctly set in `.env`
2. **Model Availability**: Verify your deployments match the model names in configuration
3. **File Permissions**: Check that the application can read SQL files and write to working directory
4. **Memory Issues**: Large databases may require chunking or processing in batches

### Logging

The application includes comprehensive logging. Check console output for detailed processing information and error messages.

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
- Open an issue in the repository

---

**Note**: This project requires active Azure OpenAI subscriptions and may incur API costs based on usage.
