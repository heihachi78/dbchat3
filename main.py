import argparse
import asyncio
import logging
import os
from datetime import datetime
from src import AzureOpenAIClient, DocumentationProcessor, RAGManager, Config
from src.token_aggregator import TokenAggregator

# Configure logging
# Create logs directory if it doesn't exist
os.makedirs(Config.LOG_DIR, exist_ok=True)

# Set LOG_DIR environment variable for LightRAG
os.environ['LOG_DIR'] = str(Config.LOG_DIR)

# Configure logging with file handler
log_filename = Config.LOG_DIR / f"dbchat3_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()  # Keep console output
    ]
)
logger = logging.getLogger(__name__)

async def process_database_files():
    """Process all database files and build RAG index"""
    # Validate all configuration at startup
    try:
        Config.validate_all_config()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\nConfiguration error: {e}")
        print("Please check your .env file and ensure all required settings are configured.")
        raise SystemExit(1)
    
    logger.info("Starting database file processing...")
    
    # Initialize components
    azure_client = AzureOpenAIClient()
    doc_processor = DocumentationProcessor(azure_client)
    rag_manager = RAGManager()
    
    # Create token aggregator for unified tracking
    token_aggregator = TokenAggregator(azure_client, rag_manager)
    
    # Process SQL files
    doc_processor.process_sql_files()
    
    # Clear databases before starting
    logger.info("Clearing Neo4j database...")
    rag_manager.clear_neo4j_database()
    
    logger.info("Clearing MongoDB database...")
    rag_manager.clear_mongodb_database()
    
    # Initialize RAG
    await rag_manager.initialize()
    
    # Insert documents
    await rag_manager.insert_documents()
    
    # Report unified token usage
    if Config.ENABLE_TOKEN_TRACKING:
        print(token_aggregator.get_summary(detailed=True))
    
    logger.info("Database file processing completed")
    return rag_manager, token_aggregator

async def run_pipeline():
    """Run RAG pipeline without generating documentation (assumes MD files exist)"""
    # Validate all configuration at startup
    try:
        Config.validate_all_config()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\nConfiguration error: {e}")
        print("Please check your .env file and ensure all required settings are configured.")
        raise SystemExit(1)
    
    logger.info("Starting RAG pipeline (skipping documentation generation)...")
    
    # Initialize components
    doc_processor = DocumentationProcessor(None)  # No Azure client needed
    rag_manager = RAGManager()
    
    # Create token aggregator (only RAG tracking in this mode)
    token_aggregator = TokenAggregator(rag_manager=rag_manager)
    
    # Clear databases before starting
    logger.info("Clearing Neo4j database...")
    rag_manager.clear_neo4j_database()
    
    logger.info("Clearing MongoDB database...")
    rag_manager.clear_mongodb_database()
    
    # Recreate working directory and copy existing MD files
    doc_processor.recreate_working_dir_and_copy_docs()
    
    # Initialize RAG
    await rag_manager.initialize()
    
    # Insert documents
    await rag_manager.insert_documents()
    
    # Report unified token usage  
    if Config.ENABLE_TOKEN_TRACKING:
        print(token_aggregator.get_summary(detailed=True))
    
    logger.info("RAG pipeline completed")
    return rag_manager, token_aggregator

async def chat_mode(rag_manager=None, token_aggregator=None):
    """Interactive chat mode"""
    # If RAG manager not provided, create one for existing data
    if not rag_manager:
        # Validate all configuration at startup
        try:
            Config.validate_all_config()
            logger.info("Configuration validated successfully")
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            print(f"\nConfiguration error: {e}")
            print("Please check your .env file and ensure all required settings are configured.")
            raise SystemExit(1)
        rag_manager = RAGManager()
        await rag_manager.initialize()
        await rag_manager.insert_documents()
        
        # Create token aggregator if not provided
        if not token_aggregator:
            token_aggregator = TokenAggregator(rag_manager=rag_manager)
    
    print("\n" + "="*50)
    print("DBChat3 - Interactive Query Mode")
    print("="*50)
    print("Enter your queries about the database schema.")
    print("The system maintains conversation history for context.")
    print("")
    print("Commands:")
    print("  exit, quit, q     - Exit the application")
    print("  /mode <mode>      - Change query mode (naive|local|global|hybrid)")
    print("  /clear            - Clear conversation history")
    print("  /history          - Show conversation history")
    print("  /tokens           - Show current session token usage")
    print("  /tokens reset     - Reset token counter")
    print("  /tokens summary   - Show detailed token breakdown")
    print("  /tokens off       - Disable token tracking display")
    print("  /tokens on        - Enable token tracking display")
    print("  modes             - Test query with all modes")
    print("="*50 + "\n")
    
    current_mode = "hybrid"  # Default mode
    conversation_history = []  # Store conversation history
    show_token_usage = True  # Default to showing token usage
    
    # Enable token tracking by default and reset for chat session
    rag_manager.set_token_tracking(True)
    token_aggregator.reset_all()
    
    while True:
        try:
            query = input(f"\nQuery [{current_mode}]> ").strip()
            
            # Check for exit commands
            if query.lower() in ['exit', 'quit', 'q']:
                print("Goodbye!")
                break
            
            # Check for mode change
            if query.startswith('/mode '):
                new_mode = query[6:].strip().lower()
                if new_mode in ['naive', 'local', 'global', 'hybrid']:
                    current_mode = new_mode
                    print(f"Mode changed to: {current_mode}")
                else:
                    print(f"Invalid mode. Available modes: naive, local, global, hybrid")
                continue
            
            # Check for clear history command
            if query.lower() == '/clear':
                conversation_history.clear()
                print("Conversation history cleared.")
                continue
            
            # Check for show history command
            if query.lower() == '/history':
                if not conversation_history:
                    print("No conversation history.")
                else:
                    print("\nConversation History:")
                    print("-" * 30)
                    for i, msg in enumerate(conversation_history):
                        role = msg["role"].capitalize()
                        content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
                        print(f"{i+1}. {role}: {content}")
                    print("-" * 30)
                continue
            
            # Check for token commands
            if query.lower().startswith('/tokens'):
                parts = query.split()
                if len(parts) == 1:
                    # Show current session token usage
                    print(token_aggregator.get_summary())
                elif len(parts) == 2 and parts[1].lower() == 'reset':
                    token_aggregator.reset_all()
                    print("Token counter reset.")
                elif len(parts) == 2 and parts[1].lower() == 'summary':
                    print(token_aggregator.get_summary(detailed=True))
                elif len(parts) == 2 and parts[1].lower() == 'off':
                    show_token_usage = False
                    print("Token tracking display disabled.")
                elif len(parts) == 2 and parts[1].lower() == 'on':
                    show_token_usage = True
                    print("Token tracking display enabled.")
                else:
                    print("Invalid token command. Use: /tokens, /tokens reset, /tokens summary, /tokens off, /tokens on")
                continue
            
            if query.lower() == 'modes':
                test_query = input("Enter query to test all modes> ").strip()
                if test_query:
                    print("\n" + "="*50)
                    results = await rag_manager.query_all_modes(test_query, conversation_history)
                    for mode, result in results.items():
                        print(f"\nResult ({mode.capitalize()}):")
                        print(result)
                        print("\n" + "-"*50)
                    
                    # Show token usage for all modes
                    if show_token_usage:
                        usage = rag_manager.get_token_usage()
                        print(f"\nToken Usage for All Modes Query:")
                        print(f"  Total: {usage.get('total_tokens', 0)}, "
                              f"Prompt: {usage.get('prompt_tokens', 0)}, "
                              f"Completion: {usage.get('completion_tokens', 0)}")
                continue
            
            if query:
                print("\nSearching...")
                
                # Add user query to conversation history
                conversation_history.append({"role": "user", "content": query})
                
                result = await rag_manager.query(query, mode=current_mode, conversation_history=conversation_history)
                print("\nResult:")
                print(result)
                
                # Add assistant response to conversation history
                conversation_history.append({"role": "assistant", "content": result})
                
                # Show token usage for this query
                if show_token_usage:
                    usage = rag_manager.get_token_usage()
                    query_total = usage.get('total_tokens', 0)
                    query_prompt = usage.get('prompt_tokens', 0)
                    query_completion = usage.get('completion_tokens', 0)
                    
                    print(f"\n[Token usage - Total: {query_total}, "
                          f"Prompt: {query_prompt}, "
                          f"Completion: {query_completion}]")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except EOFError:
            print("\nGoodbye!")
            break
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="DBChat3 - Database Documentation RAG System"
    )
    parser.add_argument(
        "--process_database_files",
        action="store_true",
        help="Process all SQL files and rebuild documentation"
    )
    parser.add_argument(
        "--run_pipeline",
        action="store_true",
        help="Run RAG pipeline without generating documentation (assumes MD files exist)"
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Interactive chat mode for querying database documentation"
    )
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if not args.process_database_files and not args.run_pipeline and not args.chat:
        parser.print_help()
        return
    
    # Run the appropriate mode
    if args.process_database_files:
        rag_manager, token_aggregator = asyncio.run(process_database_files())
        
        # If chat mode also requested, continue with it
        if args.chat:
            asyncio.run(chat_mode(rag_manager, token_aggregator))
    
    elif args.run_pipeline:
        rag_manager, token_aggregator = asyncio.run(run_pipeline())
        
        # If chat mode also requested, continue with it
        if args.chat:
            asyncio.run(chat_mode(rag_manager, token_aggregator))
    
    elif args.chat:
        asyncio.run(chat_mode())

if __name__ == "__main__":
    main()