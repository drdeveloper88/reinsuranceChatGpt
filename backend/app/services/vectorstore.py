import os
from typing import List, Dict, Any, Optional
import logging
from langchain.document_loaders import TextLoader
from langchain.embeddings import HuggingFaceEmbeddings, OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.schema import Document
from app.core.config import settings, EmbeddingType

logger = logging.getLogger(__name__)

class VectorStoreService:
    """Service for managing vector store operations"""
    
    def __init__(self):
        self.persist_dir = settings.chroma_persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)
        self.embeddings = self._create_embeddings()
        self.store = self._load_or_create()
        logger.info(f"Vector store initialized with {settings.embedding_type} embeddings")

    def _create_embeddings(self):
        """Create embeddings based on configuration"""
        if settings.embedding_type == EmbeddingType.SENTENCE_TRANSFORMER:
            logger.info(f"Using SentenceTransformer embeddings: {settings.embedding_model}")
            return HuggingFaceEmbeddings(model_name=settings.embedding_model)
        elif settings.embedding_type == EmbeddingType.OPENAI:
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            logger.info("Using OpenAI embeddings")
            return OpenAIEmbeddings(
                openai_api_key=settings.openai_api_key,
                openai_api_base=settings.openai_api_base,
            )
        else:
            raise ValueError(f"Unsupported embedding type: {settings.embedding_type}")

    def _load_or_create(self):
        """Load existing vector store or create new one"""
        return Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embeddings,
            collection_name=settings.milvus_collection,
        )

    def add_documents(
        self, 
        docs: List[str], 
        metadatas: Optional[List[Dict[str, Any]]] = None,
        namespace: str = "default"
    ) -> List[str]:
        """Add documents to vector store with metadata"""
        try:
            if not docs:
                raise ValueError("No documents provided")
            
            # Validate document sizes
            for i, doc in enumerate(docs):
                if len(doc) > 50000:
                    logger.warning(f"Document {i} exceeds 50KB, truncating")
                    docs[i] = doc[:50000]
            
            documents = [Document(page_content=d, metadata=m or {}) for d, m in zip(docs, metadatas or [{}] * len(docs))]
            
            # Add namespace metadata
            for doc in documents:
                doc.metadata['namespace'] = namespace
            
            doc_ids = self.store.add_documents(documents)
            self.store.persist()
            
            logger.info(f"Added {len(docs)} documents to namespace '{namespace}'")
            return doc_ids
        except Exception as e:
            logger.error(f"Error adding documents: {str(e)}")
            raise

    def query(
        self, 
        query: str, 
        k: int = 5,
        namespace: str = "default",
        similarity_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """Query similar documents with optional filtering"""
        try:
            if not query or not query.strip():
                raise ValueError("Query cannot be empty")
            
            results = self.store.similarity_search_with_score(query, k=k)
            
            # Filter by namespace
            filtered_results = [
                {
                    "page_content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score,
                }
                for doc, score in results
                if doc.metadata.get("namespace") == namespace and score >= similarity_threshold
            ]
            
            return filtered_results[:k]
        except Exception as e:
            logger.error(f"Error querying documents: {str(e)}")
            raise

    def delete_documents(self, document_ids: List[str]) -> bool:
        """Delete specific documents"""
        try:
            if not document_ids:
                raise ValueError("No document IDs provided")
            
            self.store.delete(ids=document_ids)
            self.store.persist()
            
            logger.info(f"Deleted {len(document_ids)} documents")
            return True
        except Exception as e:
            logger.error(f"Error deleting documents: {str(e)}")
            raise

    def clear_namespace(self, namespace: str = "default") -> bool:
        """Clear all documents in a namespace"""
        try:
            # Get all documents in namespace
            all_docs = self.store.get(where={"namespace": namespace})
            if all_docs and all_docs.get("ids"):
                self.store.delete(ids=all_docs["ids"])
                self.store.persist()
                logger.info(f"Cleared namespace '{namespace}'")
            return True
        except Exception as e:
            logger.error(f"Error clearing namespace: {str(e)}")
            raise

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics"""
        try:
            collection = self.store._collection
            return {
                "total_documents": collection.count(),
                "collection_name": collection.name,
                "metadata_schema": collection.metadata,
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {str(e)}")
            return {"error": str(e)}
