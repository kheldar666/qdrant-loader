"""Service for chunking documents."""

import logging
from typing import List
from qdrant_loader.core.document import Document
from qdrant_loader.core.chunking_strategy import ChunkingStrategy
from qdrant_loader.config import GlobalConfig, Settings

class ChunkingService:
    """Service for chunking documents into smaller pieces."""
    
    def __init__(self, config: GlobalConfig, settings: Settings):
        """Initialize the chunking service.
        
        Args:
            config: Global configuration
            settings: Application settings
        """
        self.config = config
        self.settings = settings
        self.validate_config()
        self.logger = logging.getLogger(__name__)
        self.chunking_strategy = ChunkingStrategy(
            settings=self.settings,
            chunk_size=config.chunking.chunk_size,
            chunk_overlap=config.chunking.chunk_overlap
        )
    
    def validate_config(self) -> None:
        """Validate the configuration.
        
        Raises:
            ValueError: If chunk size or overlap parameters are invalid.
        """
        if self.config.chunking.chunk_size <= 0:
            raise ValueError("Chunk size must be greater than 0")
        if self.config.chunking.chunk_overlap < 0:
            raise ValueError("Chunk overlap must be non-negative")
        if self.config.chunking.chunk_overlap >= self.config.chunking.chunk_size:
            raise ValueError("Chunk overlap must be less than chunk size")
    
    def chunk_document(self, document: Document) -> List[Document]:
        """Chunk a document into smaller pieces.
        
        Args:
            document: The document to chunk
            
        Returns:
            List of chunked documents
        """
        if not document.content:
            # Return a single empty chunk if document has no content
            empty_doc = document.copy()
            empty_doc.metadata.update({
                "chunk_index": 0,
                "total_chunks": 1
            })
            return [empty_doc]

        try:
            return self.chunking_strategy.chunk_document(document)
        except Exception as e:
            self.logger.error(f"Error chunking document: {str(e)}")
            raise e 