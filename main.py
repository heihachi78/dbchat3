import argparse
import asyncio
import logging
import nest_asyncio
from azure_client import AzureOpenAIClient
from documentation_processor import DocumentationProcessor
from rag_manager import RAGManager

# Enable nested event loops for Jupyter compatibility
nest_asyncio.apply()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def process_database_files():
    """Process all database files and build RAG index"""
    logger.info("Starting database file processing...")
    
    # Initialize components
    azure_client = AzureOpenAIClient()
    doc_processor = DocumentationProcessor(azure_client)
    rag_manager = RAGManager()
    
    # Process SQL files
    doc_processor.process_sql_files()
    
    # Initialize RAG
    await rag_manager.initialize()
    
    # Insert documents
    rag_manager.insert_documents()
    
    logger.info("Database file processing completed")
    return rag_manager

async def chat_mode(rag_manager=None):
    """Interactive chat mode"""
    # If RAG manager not provided, create one for existing data
    if not rag_manager:
        rag_manager = RAGManager()
        await rag_manager.initialize()
        rag_manager.insert_documents()
    
    print("\n" + "="*50)
    print("DBChat3 - Interactive Query Mode")
    print("="*50)
    print("Enter your queries about the database schema.")
    print("Type 'exit', 'quit', or 'q' to quit.")
    print("Use '/mode <naive|local|global|hybrid>' to change query mode.")
    print("Type 'modes' to test all query modes.")
    print("="*50 + "\n")
    
    current_mode = "hybrid"  # Default mode
    
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
            
            if query.lower() == 'modes':
                test_query = input("Enter query to test all modes> ").strip()
                if test_query:
                    print("\n" + "="*50)
                    results = rag_manager.query_all_modes(test_query)
                    for mode, result in results.items():
                        print(f"\nResult ({mode.capitalize()}):")
                        print(result)
                        print("\n" + "-"*50)
                continue
            
            if query:
                print("\nSearching...")
                result = rag_manager.query(query, mode=current_mode)
                print("\nResult:")
                print(result)
        
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
        "--chat",
        action="store_true",
        help="Interactive chat mode for querying database documentation"
    )
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if not args.process_database_files and not args.chat:
        parser.print_help()
        return
    
    # Run the appropriate mode
    if args.process_database_files:
        rag_manager = asyncio.run(process_database_files())
        
        # If chat mode also requested, continue with it
        if args.chat:
            asyncio.run(chat_mode(rag_manager))
    
    elif args.chat:
        asyncio.run(chat_mode())

if __name__ == "__main__":
    main()