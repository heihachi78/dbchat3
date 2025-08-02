import argparse
import asyncio
import logging
import os
from datetime import datetime
from src import AzureOpenAIClient, DocumentationProcessor, RAGManager, Config

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

async def process_database_files(use_llamaindex=False):
    """Process all database files and build RAG index"""
    logger.info("Starting database file processing...")
    
    # Initialize components
    azure_client = AzureOpenAIClient()
    doc_processor = DocumentationProcessor(azure_client)
    rag_manager = RAGManager(use_llamaindex=use_llamaindex)
    
    # Process SQL files
    doc_processor.process_sql_files()
    
    # Report token usage for documentation generation
    if Config.ENABLE_TOKEN_TRACKING:
        doc_usage = azure_client.get_token_usage()
        logger.info(f"Token usage for documentation generation:")
        logger.info(f"  Total tokens: {doc_usage['total_tokens']}")
        logger.info(f"  Prompt tokens: {doc_usage['prompt_tokens']}")
        logger.info(f"  Completion tokens: {doc_usage['completion_tokens']}")
        print(f"\nDocumentation Generation Token Usage:")
        print(f"  Total tokens: {doc_usage['total_tokens']}")
        print(f"  Prompt tokens: {doc_usage['prompt_tokens']}")
        print(f"  Completion tokens: {doc_usage['completion_tokens']}")
    
    # Clear Neo4j database before starting
    logger.info("Clearing Neo4j database...")
    rag_manager.clear_neo4j_database()
    
    # Initialize RAG
    await rag_manager.initialize()
    
    # Insert documents
    await rag_manager.insert_documents()
    
    # Report token usage for RAG insertion
    if Config.ENABLE_TOKEN_TRACKING:
        rag_usage = rag_manager.get_token_usage()
        logger.info(f"Token usage for RAG document insertion:")
        logger.info(f"  Total tokens: {rag_usage['total_tokens']}")
        logger.info(f"  Prompt tokens: {rag_usage['prompt_tokens']}")
        logger.info(f"  Completion tokens: {rag_usage['completion_tokens']}")
        print(f"\nRAG Document Insertion Token Usage:")
        print(f"  Total tokens: {rag_usage['total_tokens']}")
        print(f"  Prompt tokens: {rag_usage['prompt_tokens']}")
        print(f"  Completion tokens: {rag_usage['completion_tokens']}")
        
        # Total usage
        total_usage = {
            "total_tokens": doc_usage['total_tokens'] + rag_usage['total_tokens'],
            "prompt_tokens": doc_usage['prompt_tokens'] + rag_usage['prompt_tokens'],
            "completion_tokens": doc_usage['completion_tokens'] + rag_usage['completion_tokens']
        }
        print(f"\nTotal Token Usage for Processing:")
        print(f"  Total tokens: {total_usage['total_tokens']}")
        print(f"  Prompt tokens: {total_usage['prompt_tokens']}")
        print(f"  Completion tokens: {total_usage['completion_tokens']}")
    
    logger.info("Database file processing completed")
    return rag_manager

async def run_pipeline(use_llamaindex=False):
    """Run RAG pipeline without generating documentation (assumes MD files exist)"""
    logger.info("Starting RAG pipeline (skipping documentation generation)...")
    
    # Initialize components
    doc_processor = DocumentationProcessor(None)  # No Azure client needed
    rag_manager = RAGManager(use_llamaindex=use_llamaindex)
    
    # Clear Neo4j database before starting
    logger.info("Clearing Neo4j database...")
    rag_manager.clear_neo4j_database()
    
    # Recreate working directory and copy existing MD files
    doc_processor.recreate_working_dir_and_copy_docs()
    
    # Initialize RAG
    await rag_manager.initialize()
    
    # Insert documents
    await rag_manager.insert_documents()
    
    # Report token usage for RAG insertion
    if Config.ENABLE_TOKEN_TRACKING:
        rag_usage = rag_manager.get_token_usage()
        logger.info(f"Token usage for RAG document insertion:")
        logger.info(f"  Total tokens: {rag_usage['total_tokens']}")
        logger.info(f"  Prompt tokens: {rag_usage['prompt_tokens']}")
        logger.info(f"  Completion tokens: {rag_usage['completion_tokens']}")
        print(f"\nRAG Document Insertion Token Usage:")
        print(f"  Total tokens: {rag_usage['total_tokens']}")
        print(f"  Prompt tokens: {rag_usage['prompt_tokens']}")
        print(f"  Completion tokens: {rag_usage['completion_tokens']}")
    
    logger.info("RAG pipeline completed")
    return rag_manager

async def chat_mode(rag_manager=None, use_llamaindex=False):
    """Interactive chat mode"""
    # If RAG manager not provided, create one for existing data
    if not rag_manager:
        rag_manager = RAGManager(use_llamaindex=use_llamaindex)
        await rag_manager.initialize()
        await rag_manager.insert_documents()
    
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
    print("  /tokens           - Show current token usage")
    print("  /tokens reset     - Reset token counter")
    print("  /tokens off       - Disable token tracking")
    print("  /tokens on        - Enable token tracking")
    print("  modes             - Test query with all modes")
    print("="*50 + "\n")
    
    current_mode = "hybrid"  # Default mode
    conversation_history = []  # Store conversation history
    
    # Initialize session token tracking
    session_tokens = {"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0}
    
    # Reset token tracker for chat session
    rag_manager.reset_token_tracker()
    
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
                    print(f"\nCurrent Session Token Usage:")
                    print(f"  Total tokens: {session_tokens['total_tokens']}")
                    print(f"  Prompt tokens: {session_tokens['prompt_tokens']}")
                    print(f"  Completion tokens: {session_tokens['completion_tokens']}")
                elif len(parts) == 2 and parts[1].lower() == 'reset':
                    session_tokens = {"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0}
                    rag_manager.reset_token_tracker()
                    print("Token counter reset.")
                elif len(parts) == 2 and parts[1].lower() == 'off':
                    rag_manager.set_token_tracking(False)
                    print("Token tracking disabled.")
                elif len(parts) == 2 and parts[1].lower() == 'on':
                    rag_manager.set_token_tracking(True)
                    print("Token tracking enabled.")
                else:
                    print("Invalid token command. Use: /tokens, /tokens reset, /tokens off, /tokens on")
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
                    if rag_manager.enable_token_tracking:
                        usage = rag_manager.get_token_usage()
                        print(f"\nTotal Token Usage for All Modes:")
                        print(f"  Total tokens: {usage.get('total_tokens', 0)}")
                        print(f"  Prompt tokens: {usage.get('prompt_tokens', 0)}")
                        print(f"  Completion tokens: {usage.get('completion_tokens', 0)}")
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
                
                # Show token usage for this query and update session totals
                if rag_manager.enable_token_tracking and Config.SHOW_TOKEN_USAGE_IN_CHAT:
                    usage = rag_manager.get_token_usage()
                    query_total = usage.get('total_tokens', 0)
                    query_prompt = usage.get('prompt_tokens', 0)
                    query_completion = usage.get('completion_tokens', 0)
                    
                    # Update session totals
                    session_tokens['total_tokens'] += query_total
                    session_tokens['prompt_tokens'] += query_prompt
                    session_tokens['completion_tokens'] += query_completion
                    
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
    parser.add_argument(
        "--use_llamaindex",
        action="store_true",
        help="Use LlamaIndex for embedding generation instead of direct Azure OpenAI"
    )
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if not args.process_database_files and not args.run_pipeline and not args.chat:
        parser.print_help()
        return
    
    # Run the appropriate mode
    if args.process_database_files:
        rag_manager = asyncio.run(process_database_files(use_llamaindex=args.use_llamaindex))
        
        # If chat mode also requested, continue with it
        if args.chat:
            asyncio.run(chat_mode(rag_manager, use_llamaindex=args.use_llamaindex))
    
    elif args.run_pipeline:
        rag_manager = asyncio.run(run_pipeline(use_llamaindex=args.use_llamaindex))
        
        # If chat mode also requested, continue with it
        if args.chat:
            asyncio.run(chat_mode(rag_manager, use_llamaindex=args.use_llamaindex))
    
    elif args.chat:
        asyncio.run(chat_mode(use_llamaindex=args.use_llamaindex))

if __name__ == "__main__":
    main()