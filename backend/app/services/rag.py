import logging
from typing import List, Dict, Any
from langchain.chains import RetrievalQAWithSourcesChain, ConversationalRetrievalChain
from langchain.llms import OpenAI
from langchain.llms.ollama import Ollama
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from app.services.vectorstore import VectorStoreService
from app.core.config import settings, LLMType

logger = logging.getLogger(__name__)

class RAGService:
    """Service for Retrieval Augmented Generation with insurance domain context"""
    
    INSURANCE_SYSTEM_PROMPT = """You are an expert insurance consultant assistant. 
Your role is to help customers understand insurance policies, coverage options, claims procedures, and related matters.

Guidelines:
1. Be helpful, clear, and professional
2. Only provide information based on the provided documents
3. If you don't know the answer, say "I don't have information about this in my knowledge base"
4. Provide specific policy details when available
5. Explain insurance terms in simple language
6. Suggest contacting the insurance company for complex matters

Context from insurance documents will be provided below."""

    def __init__(self, vector_service: VectorStoreService):
        self.vector_service = vector_service
        self.llm = self._create_llm()
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        self.chain = self._create_chain()
        logger.info(f"RAG Service initialized with {settings.llm_type} LLM")

    def _create_llm(self):
        """Create LLM based on configuration"""
        if settings.llm_type == LLMType.OLLAMA:
            logger.info(f"Using Ollama LLM: {settings.ollama_model}")
            return Ollama(
                base_url=settings.ollama_base_url,
                model=settings.ollama_model,
                temperature=settings.llm_temperature,
                top_p=settings.llm_top_p,
            )
        elif settings.llm_type == LLMType.OPENAI:
            if not settings.openai_api_key:
                raise ValueError("OpenAI API key not configured")
            logger.info(f"Using OpenAI LLM: {settings.openai_model}")
            return OpenAI(
                openai_api_key=settings.openai_api_key,
                openai_api_base=settings.openai_api_base,
                model_name=settings.openai_model,
                temperature=settings.llm_temperature,
                max_tokens=settings.llm_max_tokens,
            )
        elif settings.llm_type == LLMType.HUGGINGFACE:
            logger.info(f"Using HuggingFace LLM: {settings.huggingface_model_name}")
            from langchain.llms import HuggingFacePipeline
            # Note: This requires additional setup, shown as example
            raise NotImplementedError("HuggingFace LLM requires local setup")
        else:
            raise ValueError(f"Unsupported LLM type: {settings.llm_type}")

    def _create_chain(self):
        """Create the RAG chain"""
        prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template=f"""{self.INSURANCE_SYSTEM_PROMPT}

Context:
{{context}}

Question: {{question}}

Answer based on the provided context:"""
        )
        
        return RetrievalQAWithSourcesChain.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_service.store.as_retriever(
                search_kwargs={
                    "k": settings.rag_top_k,
                    "filter": {"namespace": "insurance"}
                }
            ),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt_template},
        )

    def answer(self, query: str, namespace: str = "insurance") -> Dict[str, Any]:
        """Generate answer using RAG with confidence scoring"""
        try:
            if not query or not query.strip():
                raise ValueError("Query cannot be empty")
            
            result = self.chain({"question": query})
            
            # Calculate confidence based on source scores
            confidence = self._calculate_confidence(result.get("source_documents", []))
            
            return {
                "answer": result.get("answer", ""),
                "sources": [
                    {
                        "page_content": doc.page_content[:500],  # Truncate for response
                        "metadata": doc.metadata,
                    }
                    for doc in result.get("source_documents", [])
                ],
                "confidence_score": confidence,
                "model_used": str(settings.llm_type),
            }
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise

    def _calculate_confidence(self, source_documents: List) -> float:
        """Calculate confidence score based on source documents"""
        if not source_documents:
            return 0.0
        
        # Higher confidence if multiple relevant sources found
        num_sources = len(source_documents)
        base_confidence = min(0.95, 0.5 + (num_sources * 0.1))
        
        return round(base_confidence, 2)

    def stream_answer(self, query: str, namespace: str = "insurance"):
        """Stream answer chunks (for real-time UI updates)"""
        try:
            result = self.answer(query, namespace)
            answer_text = result["answer"]
            
            # Stream in chunks
            chunk_size = 50
            for i in range(0, len(answer_text), chunk_size):
                chunk = answer_text[i:i+chunk_size]
                yield {
                    "type": "text",
                    "delta": chunk,
                }
            
            # Send sources at the end
            yield {
                "type": "sources",
                "sources": result["sources"],
                "confidence_score": result["confidence_score"],
            }
            
            yield {
                "type": "done",
                "content": "Response complete"
            }
        except Exception as e:
            logger.error(f"Error streaming answer: {str(e)}")
            yield {
                "type": "error",
                "error": str(e)
            }

    def validate_query(self, query: str) -> bool:
        """Validate query for insurance context"""
        if not query or len(query) < 3:
            return False
        
        # Check if query is insurance-related (basic check)
        insurance_keywords = ['insurance', 'policy', 'claim', 'coverage', 'premium', 'deductible']
        query_lower = query.lower()
        
        return any(keyword in query_lower for keyword in insurance_keywords)
