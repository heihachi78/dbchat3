import os
import shutil
import logging
from pathlib import Path
from azure_client import AzureOpenAIClient
from config import Config

logger = logging.getLogger(__name__)

class DocumentationProcessor:
    def __init__(self, azure_client: AzureOpenAIClient):
        self.azure_client = azure_client
        self.database_dir = Config.DATABASE_FILES_DIR
        self.working_dir = Config.WORKING_DIR
        self.system_prompt = Config.SYSTEM_PROMPT
    
    def process_sql_files(self):
        """Process all SQL files and generate documentation"""
        # Clean up working directory
        if os.path.exists(self.working_dir):
            shutil.rmtree(self.working_dir)
        os.mkdir(self.working_dir)
        logger.info(f"Working directory {self.working_dir} recreated")
        
        # Clean up existing markdown files
        self._cleanup_existing_docs()
        
        # Find and process SQL files
        sql_files = self._find_sql_files()
        logger.info(f"Found {len(sql_files)} SQL files in {self.database_dir}")
        
        # Generate documentation for each SQL file
        for sql_file, content in sql_files:
            self._generate_doc_for_file(sql_file, content)
        
        # Copy markdown files to working directory
        self._copy_docs_to_working_dir()
    
    def _find_sql_files(self) -> list:
        """Find all SQL files in database directory"""
        sql_files = []
        if self.database_dir.exists() and self.database_dir.is_dir():
            for sql_file in self.database_dir.rglob("*.sql"):
                with open(sql_file, encoding="utf-8") as f:
                    content = f.read()
                sql_files.append((sql_file, content))
        return sql_files
    
    def _cleanup_existing_docs(self):
        """Remove existing markdown files"""
        for md_file in self.database_dir.rglob("*.md"):
            try:
                md_file.unlink(missing_ok=True)
                logger.info(f"Deleted file {md_file}")
            except PermissionError:
                logger.error(f"Permission denied deleting file {md_file}")
            except Exception as e:
                logger.error(f"Unexpected error deleting file {md_file}: {e}")
    
    def _generate_doc_for_file(self, sql_file: Path, content: str):
        """Generate documentation for a single SQL file"""
        try:
            documentation = self.azure_client.generate_documentation(
                content, 
                self.system_prompt
            )
            
            with open(sql_file.with_suffix(".md"), "w") as f:
                f.write(documentation)
            
            logger.info(f"Generated documentation for {sql_file}")
        except Exception as e:
            logger.error(f"Error generating documentation for {sql_file}: {e}")
    
    def _copy_docs_to_working_dir(self):
        """Copy all markdown files to working directory"""
        for md_file in self.database_dir.rglob("*.md"):
            try:
                target_file = Path(self.working_dir) / md_file.name
                target_file.write_text(
                    md_file.read_text(encoding="utf-8"), 
                    encoding="utf-8"
                )
                logger.info(f"Copied file {md_file} to {target_file}")
            except PermissionError:
                logger.error(f"Permission denied copying file {md_file}")
            except Exception as e:
                logger.error(f"Unexpected error copying file {md_file}: {e}")