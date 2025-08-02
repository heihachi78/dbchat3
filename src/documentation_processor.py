import os
import shutil
import logging
from pathlib import Path
from .azure_client import AzureOpenAIClient
from .config import Config
from .retry_utils import retry_sync, FILE_OPERATION_RETRY_CONFIG

logger = logging.getLogger(__name__)

class DocumentationProcessor:
    def __init__(self, azure_client: AzureOpenAIClient):
        self.azure_client = azure_client
        self.database_dir = Config.DATABASE_FILES_DIR
        self.working_dir = Config.WORKING_DIR
        self.system_prompt = Config.SYSTEM_PROMPT
    
    def _cleanup_working_dir(self):
        """Clean up and recreate working directory with error handling"""
        try:
            if os.path.exists(self.working_dir):
                shutil.rmtree(self.working_dir)
                logger.info(f"Removed existing working directory {self.working_dir}")
                
            os.makedirs(self.working_dir, exist_ok=True)
            logger.info(f"Working directory {self.working_dir} created")
            
        except PermissionError as e:
            logger.error(f"Permission denied managing working directory {self.working_dir}: {e}")
            raise
        except OSError as e:
            logger.error(f"OS error managing working directory {self.working_dir}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error managing working directory {self.working_dir}: {e}")
            raise
    
    def process_sql_files(self):
        """Process all SQL files and generate documentation"""
        # Clean up working directory
        self._cleanup_working_dir()
        
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
        """Find all SQL files in database directory with error handling"""
        sql_files = []
        if not self.database_dir.exists() or not self.database_dir.is_dir():
            logger.warning(f"Database directory does not exist: {self.database_dir}")
            return sql_files
            
        for sql_file in self.database_dir.rglob("*.sql"):
            try:
                with open(sql_file, encoding="utf-8") as f:
                    content = f.read()
                sql_files.append((sql_file, content))
            except (OSError, IOError, UnicodeDecodeError) as e:
                logger.error(f"Error reading SQL file {sql_file}: {e}")
                # Continue processing other files instead of failing completely
                continue
            except Exception as e:
                logger.error(f"Unexpected error reading SQL file {sql_file}: {e}")
                continue
                
        return sql_files
    
    @retry_sync(**FILE_OPERATION_RETRY_CONFIG)
    def _cleanup_existing_docs(self):
        """Remove existing markdown files with retry logic"""
        failed_deletions = []
        
        for md_file in self.database_dir.rglob("*.md"):
            try:
                md_file.unlink(missing_ok=True)
                logger.info(f"Deleted file {md_file}")
            except PermissionError as e:
                logger.error(f"Permission denied deleting file {md_file}: {e}")
                failed_deletions.append(md_file)
            except OSError as e:
                logger.error(f"OS error deleting file {md_file}: {e}")
                failed_deletions.append(md_file)
            except Exception as e:
                logger.error(f"Unexpected error deleting file {md_file}: {e}")
                failed_deletions.append(md_file)
        
        if failed_deletions:
            logger.warning(f"Failed to delete {len(failed_deletions)} markdown files: {failed_deletions}")
    
    def _generate_doc_for_file(self, sql_file: Path, content: str):
        """Generate documentation for a single SQL file with comprehensive error handling"""
        md_file_path = sql_file.with_suffix(".md")
        
        try:
            # Generate documentation using Azure OpenAI (has its own retry logic)
            documentation = self.azure_client.generate_documentation(
                content, 
                self.system_prompt
            )
            
            # Write documentation with error handling and retry
            self._write_documentation_file(md_file_path, documentation)
            
            logger.info(f"Generated documentation for {sql_file}")
            
        except Exception as e:
            logger.error(f"Error generating documentation for {sql_file}: {e}")
            # Don't re-raise - continue processing other files
    
    @retry_sync(**FILE_OPERATION_RETRY_CONFIG)
    def _write_documentation_file(self, file_path: Path, content: str):
        """Write documentation to file with retry logic
        
        Note: mkdir is required here because this writes to the original database
        directory structure which may have arbitrary subdirectories.
        """
        try:
            # Ensure parent directory exists (required for database directory structure)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
                
        except PermissionError as e:
            logger.error(f"Permission denied writing to {file_path}: {e}")
            raise
        except OSError as e:
            logger.error(f"OS error writing to {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error writing to {file_path}: {e}")
            raise
    
    def _ensure_target_directories(self, md_files: list) -> set:
        """Create all target directories in batch to avoid redundant operations"""
        target_dirs = set()
        
        # Collect all unique target directories
        for md_file in md_files:
            target_file = Path(self.working_dir) / md_file.name
            target_dirs.add(target_file.parent)
        
        # Create all directories in one pass
        failed_dirs = []
        for target_dir in target_dirs:
            try:
                target_dir.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Ensured directory exists: {target_dir}")
            except (PermissionError, OSError) as e:
                logger.error(f"Failed to create directory {target_dir}: {e}")
                failed_dirs.append(target_dir)
                
        if failed_dirs:
            logger.warning(f"Failed to create {len(failed_dirs)} target directories")
            
        return target_dirs - set(failed_dirs)
    
    def _copy_docs_to_working_dir(self):
        """Copy all markdown files to working directory with comprehensive error handling"""
        failed_copies = []
        md_files = list(self.database_dir.rglob("*.md"))
        
        if not md_files:
            logger.info("No markdown files found to copy")
            return
            
        # Create all target directories upfront
        successful_dirs = self._ensure_target_directories(md_files)
        
        for md_file in md_files:
            target_file = Path(self.working_dir) / md_file.name
            
            # Skip if target directory creation failed
            if target_file.parent not in successful_dirs:
                logger.error(f"Skipping {md_file} - target directory creation failed")
                failed_copies.append(md_file)
                continue
            
            try:
                self._copy_single_file(md_file, target_file)
                logger.info(f"Copied file {md_file} to {target_file}")
                
            except Exception as e:
                logger.error(f"Failed to copy {md_file} to {target_file}: {e}")
                failed_copies.append(md_file)
        
        if failed_copies:
            logger.warning(f"Failed to copy {len(failed_copies)} files to working directory: {failed_copies}")
    
    @retry_sync(**FILE_OPERATION_RETRY_CONFIG)
    def _copy_single_file(self, source_file: Path, target_file: Path):
        """Copy a single file with retry logic - assumes target directory already exists"""
        try:
            # Read source file content
            content = source_file.read_text(encoding="utf-8")
            
            # Write to target file
            target_file.write_text(content, encoding="utf-8")
            
        except PermissionError as e:
            logger.error(f"Permission denied copying {source_file} to {target_file}: {e}")
            raise
        except (OSError, IOError) as e:
            logger.error(f"IO error copying {source_file} to {target_file}: {e}")
            raise
        except UnicodeDecodeError as e:
            logger.error(f"Encoding error reading {source_file}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error copying {source_file} to {target_file}: {e}")
            raise
    
    def recreate_working_dir_and_copy_docs(self):
        """Recreate working directory and copy existing markdown files"""
        # Clean up working directory
        self._cleanup_working_dir()
        
        # Copy existing markdown files to working directory
        self._copy_docs_to_working_dir()