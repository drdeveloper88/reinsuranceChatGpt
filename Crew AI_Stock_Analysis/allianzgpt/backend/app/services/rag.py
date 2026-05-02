from typing import List
from langchain.chains import RetrievalQAWithSourcesChain
from langchain.llms import OpenAI
from app.services.vectorstore import VectorStoreService
from app.core.config import settings

class RAGService:
    def __init__(self, vector_service: VectorStoreService):
        self.vector_service = vector_service
        self.llm = OpenAI(
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.openai_api_base,
            model_name=settings.openai_model,
            temperature=0.1,
            max_tokens=1024,
        )

        self.chain = RetrievalQAWithSourcesChain.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=self.vector_service.store.as_retriever(
                search_kwargs={"k": 4}
            ),
            return_source_documents=True,
        )

    def answer(self, query: str):
        result = self.chain({"question": query})
        return {
            "answer": result.get("answer", ""),
            "sources": [
                {
                    "page_content": doc.page_content,
                    "metadata": doc.metadata,
                }
                for doc in result.get("source_documents", [])
            ],
        }
