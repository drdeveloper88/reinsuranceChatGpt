"""
Database seeding utility for insurance documents
"""

import logging
from typing import List, Dict, Any
from app.services.vectorstore import VectorStoreService
from app.data.insurance_samples import get_sample_data
from app.models.schemas import InsuranceType, DocumentMetadata

logger = logging.getLogger(__name__)


class DataSeeder:
    """Seed initial insurance documents into the vector store"""
    
    @staticmethod
    def seed_insurance_data(vector_service: VectorStoreService) -> bool:
        """
        Seed initial insurance documents
        
        Args:
            vector_service: VectorStoreService instance
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if data already exists
            stats = vector_service.get_collection_stats()
            if stats.get("total_documents", 0) > 0:
                logger.info("Vector store already contains documents, skipping seeding")
                return True
            
            logger.info("Seeding insurance documents...")
            
            insurance_types = [
                InsuranceType.HEALTH,
                InsuranceType.PROPERTY,
                InsuranceType.AUTO,
                InsuranceType.LIFE
            ]
            
            total_docs = 0
            for insurance_type in insurance_types:
                samples = get_sample_data(insurance_type.value)
                
                if samples:
                    metadatas = []
                    for i, sample in enumerate(samples):
                        metadata = {
                            "insurance_type": insurance_type.value,
                            "document_type": "policy",
                            "source": f"Insurance Knowledge Base - {insurance_type.value}",
                            "confidentiality_level": "public",
                            "version": "1.0",
                            "keywords": extract_keywords(sample)
                        }
                        metadatas.append(metadata)
                    
                    # Add documents to vector store
                    doc_ids = vector_service.add_documents(
                        samples,
                        metadatas=metadatas,
                        namespace="insurance"
                    )
                    
                    logger.info(f"Seeded {len(samples)} {insurance_type.value} insurance documents")
                    total_docs += len(samples)
            
            logger.info(f"Successfully seeded {total_docs} total documents")
            return True
            
        except Exception as e:
            logger.error(f"Error seeding data: {str(e)}")
            return False


def extract_keywords(text: str) -> List[str]:
    """
    Extract keywords from document
    
    Simple extraction - can be improved with NLP
    """
    keywords = []
    
    # Insurance-related keywords
    key_phrases = [
        "coverage", "policy", "premium", "deductible", "claim",
        "copay", "coinsurance", "out-of-pocket", "exclusion",
        "benefit", "limit", "network", "authorization"
    ]
    
    text_lower = text.lower()
    for phrase in key_phrases:
        if phrase in text_lower:
            keywords.append(phrase)
    
    return keywords[:5]  # Limit to top 5 keywords


async def seed_on_startup(vector_service: VectorStoreService) -> None:
    """
    Called on application startup
    """
    DataSeeder.seed_insurance_data(vector_service)
