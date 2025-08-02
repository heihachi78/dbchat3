import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Azure OpenAI settings
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
    AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
    AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
    
    AZURE_EMBEDDING_DEPLOYMENT = os.getenv("AZURE_EMBEDDING_DEPLOYMENT")
    AZURE_EMBEDDING_API_VERSION = os.getenv("AZURE_EMBEDDING_API_VERSION")
    
    # Neo4j settings
    NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://localhost:7687")
    NEO4J_USERNAME = os.getenv("NEO4J_USERNAME", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
    NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")
    NEO4J_WORKSPACE = os.getenv("NEO4J_WORKSPACE")
    
    # MongoDB settings
    MONGO_USER = os.getenv("MONGO_USER")
    MONGO_PASS = os.getenv("MONGO_PASS")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DATABASE = os.getenv("MONGO_DATABASE", "LightRAG")
    MONGODB_WORKSPACE = os.getenv("MONGODB_WORKSPACE")
    
    # Directories
    DATABASE_FILES_DIR = Path("database_files")
    WORKING_DIR = Path("working_dir")
    LOG_DIR = Path(os.getenv("LOG_DIR", "logs"))
    
    # Model settings
    EMBEDDING_DIMENSION = int(os.getenv("AZURE_EMBEDDING_DIMENSION", "3072"))  # small 1536, large 3072
    
    # Token tracking settings
    ENABLE_TOKEN_TRACKING = os.getenv("ENABLE_TOKEN_TRACKING", "true").lower() == "true"
    SHOW_TOKEN_USAGE_IN_CHAT = os.getenv("SHOW_TOKEN_USAGE_IN_CHAT", "true").lower() == "true"
    
    @classmethod
    def validate_azure_config(cls):
        """Validate required Azure OpenAI configuration"""
        required_configs = [
            ('AZURE_OPENAI_API_KEY', cls.AZURE_OPENAI_API_KEY),
            ('AZURE_OPENAI_ENDPOINT', cls.AZURE_OPENAI_ENDPOINT),
            ('AZURE_OPENAI_API_VERSION', cls.AZURE_OPENAI_API_VERSION),
            ('AZURE_OPENAI_DEPLOYMENT', cls.AZURE_OPENAI_DEPLOYMENT),
            ('AZURE_EMBEDDING_DEPLOYMENT', cls.AZURE_EMBEDDING_DEPLOYMENT),
            ('AZURE_EMBEDDING_API_VERSION', cls.AZURE_EMBEDDING_API_VERSION),
        ]
        
        missing_configs = [name for name, value in required_configs if not value]
        if missing_configs:
            raise ValueError(
                f"Missing required Azure OpenAI configuration variables: {', '.join(missing_configs)}\n"
                f"Please ensure these are set in your .env file or as environment variables.\n"
                f"Refer to .env.sample for the required format."
            )
    
    @classmethod
    def validate_neo4j_config(cls):
        """Validate Neo4j configuration"""
        if not cls.NEO4J_PASSWORD:
            raise ValueError(
                "NEO4J_PASSWORD environment variable must be set\n"
                "This is required to authenticate with your Neo4j database.\n"
                "Default username is 'neo4j' unless NEO4J_USERNAME is specified."
            )
        
        # Validate URI scheme
        valid_schemes = ['bolt', 'bolt+ssc', 'bolt+s', 'neo4j', 'neo4j+ssc', 'neo4j+s']
        if not any(cls.NEO4J_URI.startswith(scheme + '://') for scheme in valid_schemes):
            raise ValueError(
                f"NEO4J_URI '{cls.NEO4J_URI}' has an invalid scheme\n"
                f"Must use one of these schemes: {', '.join(valid_schemes)}\n"
                f"Example: neo4j://localhost:7687 or bolt://localhost:7687"
            )
    
    @classmethod
    def validate_mongo_config(cls):
        """Validate MongoDB configuration"""
        if not cls.MONGO_URI:
            raise ValueError(
                "MONGO_URI environment variable must be set\n"
                "Example: mongodb://localhost:27017/\n"
                "For authenticated connections, use: mongodb://username:password@host:port/"
            )
        
        # Basic MongoDB URI validation
        if not cls.MONGO_URI.startswith('mongodb://') and not cls.MONGO_URI.startswith('mongodb+srv://'):
            raise ValueError(
                f"MONGO_URI '{cls.MONGO_URI}' has an invalid format\n"
                "Must start with 'mongodb://' or 'mongodb+srv://'\n"
                "Example: mongodb://localhost:27017/"
            )
        
        if not cls.MONGO_DATABASE:
            raise ValueError(
                "MONGO_DATABASE must be specified\n"
                "This defines which MongoDB database to use for storage.\n"
                "Default value is 'LightRAG' if not set."
            )
    
    @classmethod
    def validate_all_config(cls):
        """Validate all configuration"""
        errors = []
        
        # Validate each configuration and collect errors
        try:
            cls.validate_azure_config()
        except ValueError as e:
            errors.append(f"Azure OpenAI Configuration:\n{str(e)}")
        
        try:
            cls.validate_neo4j_config()
        except ValueError as e:
            errors.append(f"Neo4j Configuration:\n{str(e)}")
        
        try:
            cls.validate_mongo_config()
        except ValueError as e:
            errors.append(f"MongoDB Configuration:\n{str(e)}")
        
        # If there are any errors, raise them all together
        if errors:
            raise ValueError("\n\n".join(errors))
    
    # Documentation system prompt
    SYSTEM_PROMPT = """
You are an expert database documentation specialist. Your role is to create comprehensive, detailed documentation for database objects based on DDL (Data Definition Language) statements provided by users.

## Core Instructions

When a user provides DDL for any database object, create thorough documentation that extracts and utilizes ALL available information including comments, constraints, metadata, and specifications. Provide the most complete documentation possible - no detail is too small.
Do not overexplain anything, for example when you find something in the "animal" schema, you dont need to explain what is an "animal" in general.
The generated documentation will be used for creating a graph database from it, which later will be used for RAG to answer question about the database object and their relationship.

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