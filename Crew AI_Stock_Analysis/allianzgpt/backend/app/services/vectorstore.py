import os
from typing import List
from langchain.document_loaders import TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from app.core.config import settings


class VectorStoreService:
    def __init__(self):
        self.persist_dir = settings.chroma_persist_dir
        os.makedirs(self.persist_dir, exist_ok=True)
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key,
            openai_api_base=settings.openai_api_base,
        )
        self.store = self._load_or_create()

    def _load_or_create(self):
        return Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embeddings,
            collection_name="allianzgpt",
        )

    def add_documents(self, docs: List[str], metadatas=None, namespace="default"):
        from langchain.schema import Document

        documents = [Document(page_content=d) for d in docs]
        self.store.add_documents(documents, metadatas=metadatas, namespace=namespace)
        self.store.persist()

    def query(self, query: str, k: int = 4, namespace="default"):
        return self.store.similarity_search_with_score(query, k=k, namespace=namespace)

    def clear_namespace(self, namespace="default"):
        self.store.delete(collection_name="allianzgpt", ids=None, namespace=namespace)
        self.store.persist()
