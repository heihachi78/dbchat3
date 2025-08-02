"""Token Aggregator for unified token usage tracking across different components."""

from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class TokenAggregator:
    """Aggregates token usage from multiple sources (Azure OpenAI Client and RAG Manager)."""
    
    def __init__(self, azure_client=None, rag_manager=None):
        """Initialize the token aggregator with optional client references.
        
        Args:
            azure_client: AzureOpenAIClient instance for documentation processing
            rag_manager: RAGManager instance for RAG operations
        """
        self.azure_client = azure_client
        self.rag_manager = rag_manager
    
    def set_azure_client(self, azure_client):
        """Set or update the Azure OpenAI client reference."""
        self.azure_client = azure_client
    
    def set_rag_manager(self, rag_manager):
        """Set or update the RAG manager reference."""
        self.rag_manager = rag_manager
    
    def get_azure_usage(self) -> Dict[str, int]:
        """Get token usage from Azure OpenAI client.
        
        Returns:
            Dictionary with token usage or empty dict if no client
        """
        if self.azure_client and hasattr(self.azure_client, 'get_token_usage'):
            return self.azure_client.get_token_usage()
        return {"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0}
    
    def get_rag_usage(self) -> Dict[str, int]:
        """Get token usage from RAG manager.
        
        Returns:
            Dictionary with token usage or empty dict if no manager
        """
        if self.rag_manager and hasattr(self.rag_manager, 'get_token_usage'):
            usage = self.rag_manager.get_token_usage()
            # Ensure consistent format
            return {
                "total_tokens": usage.get("total_tokens", 0),
                "prompt_tokens": usage.get("prompt_tokens", 0),
                "completion_tokens": usage.get("completion_tokens", 0)
            }
        return {"total_tokens": 0, "prompt_tokens": 0, "completion_tokens": 0}
    
    def get_total_usage(self) -> Dict[str, Any]:
        """Get aggregated token usage from all sources.
        
        Returns:
            Dictionary with total usage and breakdown by source
        """
        azure_usage = self.get_azure_usage()
        rag_usage = self.get_rag_usage()
        
        total_usage = {
            "total": {
                "total_tokens": azure_usage["total_tokens"] + rag_usage["total_tokens"],
                "prompt_tokens": azure_usage["prompt_tokens"] + rag_usage["prompt_tokens"],
                "completion_tokens": azure_usage["completion_tokens"] + rag_usage["completion_tokens"]
            },
            "breakdown": {
                "documentation": azure_usage,
                "rag": rag_usage
            }
        }
        
        return total_usage
    
    def get_summary(self, detailed: bool = False) -> str:
        """Get a formatted summary of token usage.
        
        Args:
            detailed: If True, show breakdown by source
            
        Returns:
            Formatted string with token usage summary
        """
        usage = self.get_total_usage()
        total = usage["total"]
        
        summary_lines = [
            "\n=== Token Usage Summary ===",
            f"Total Tokens: {total['total_tokens']:,}",
            f"Prompt Tokens: {total['prompt_tokens']:,}",
            f"Completion Tokens: {total['completion_tokens']:,}"
        ]
        
        if detailed:
            breakdown = usage["breakdown"]
            summary_lines.append("\n--- Breakdown by Component ---")
            
            # Documentation (Azure) usage
            doc_usage = breakdown["documentation"]
            if doc_usage["total_tokens"] > 0:
                summary_lines.extend([
                    f"\nDocumentation Processing:",
                    f"  Total: {doc_usage['total_tokens']:,}",
                    f"  Prompt: {doc_usage['prompt_tokens']:,}",
                    f"  Completion: {doc_usage['completion_tokens']:,}"
                ])
            
            # RAG usage
            rag_usage = breakdown["rag"]
            if rag_usage["total_tokens"] > 0:
                summary_lines.extend([
                    f"\nRAG Operations:",
                    f"  Total: {rag_usage['total_tokens']:,}",
                    f"  Prompt: {rag_usage['prompt_tokens']:,}",
                    f"  Completion: {rag_usage['completion_tokens']:,}"
                ])
        
        summary_lines.append("=" * 26)
        
        return "\n".join(summary_lines)
    
    def reset_all(self):
        """Reset token counters for all tracked components."""
        if self.azure_client and hasattr(self.azure_client, 'reset_token_usage'):
            self.azure_client.reset_token_usage()
            logger.info("Reset Azure client token usage")
        
        if self.rag_manager and hasattr(self.rag_manager, 'reset_token_tracker'):
            self.rag_manager.reset_token_tracker()
            logger.info("Reset RAG manager token usage")