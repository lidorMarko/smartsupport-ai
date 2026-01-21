import os
import pickle
from pathlib import Path
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
)
from langchain.schema import Document
from app.config import get_settings


class RAGService:
    def __init__(self):
        settings = get_settings()
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key,
            model=settings.openai_embedding_model,
        )
        self.persist_directory = settings.chroma_persist_directory
        self.faiss_index_path = os.path.join(self.persist_directory, "faiss_index")
        self.chunk_size = settings.chunk_size
        self.chunk_overlap = settings.chunk_overlap
        self.top_k = settings.retrieval_top_k

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )

        self.vectorstore: FAISS | None = self._load_vectorstore()
        self._document_count = 0

    def _load_vectorstore(self) -> FAISS | None:
        """Load existing FAISS index if it exists."""
        try:
            if os.path.exists(self.faiss_index_path):
                return FAISS.load_local(
                    self.faiss_index_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True,
                )
        except Exception as e:
            print(f"Could not load existing index: {e}")
        return None

    def _save_vectorstore(self):
        """Save FAISS index to disk."""
        if self.vectorstore:
            os.makedirs(self.persist_directory, exist_ok=True)
            self.vectorstore.save_local(self.faiss_index_path)

    def add_documents(self, documents: list[Document]) -> int:
        """
        Add documents to the vector store.

        Args:
            documents: List of LangChain Document objects

        Returns:
            Number of chunks added
        """
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)

        if not chunks:
            return 0

        # Add to vectorstore
        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(chunks, self.embeddings)
        else:
            self.vectorstore.add_documents(chunks)

        self._document_count += len(chunks)
        self._save_vectorstore()

        return len(chunks)

    def add_texts(self, texts: list[str], metadatas: list[dict] | None = None) -> int:
        """
        Add raw texts to the vector store.

        Args:
            texts: List of text strings
            metadatas: Optional metadata for each text

        Returns:
            Number of chunks added
        """
        documents = [
            Document(page_content=text, metadata=metadatas[i] if metadatas else {})
            for i, text in enumerate(texts)
        ]
        return self.add_documents(documents)

    def load_directory(self, directory_path: str) -> int:
        """
        Load all supported documents from a directory.

        Args:
            directory_path: Path to directory containing documents

        Returns:
            Number of chunks added
        """
        documents = []
        path = Path(directory_path)

        if not path.exists():
            raise ValueError(f"Directory not found: {directory_path}")

        # Load different file types
        for file_path in path.rglob("*"):
            if file_path.is_file():
                try:
                    if file_path.suffix in [".txt", ".md"]:
                        loader = TextLoader(str(file_path), encoding="utf-8")
                        documents.extend(loader.load())
                    elif file_path.suffix == ".pdf":
                        loader = PyPDFLoader(str(file_path))
                        documents.extend(loader.load())
                    elif file_path.suffix in [".docx", ".doc"]:
                        loader = Docx2txtLoader(str(file_path))
                        documents.extend(loader.load())
                except Exception as e:
                    print(f"Error loading {file_path}: {e}")

        if documents:
            return self.add_documents(documents)
        return 0

    def query(self, question: str, k: int | None = None) -> tuple[str, list[str]]:
        """
        Query the vector store for relevant context.

        Args:
            question: The user's question
            k: Number of results to return (defaults to settings.retrieval_top_k)

        Returns:
            Tuple of (combined context string, list of source names)
        """
        if self.vectorstore is None:
            return "", []

        k = k or self.top_k

        results = self.vectorstore.similarity_search(question, k=k)

        if not results:
            return "", []

        # Combine results into context
        context_parts = []
        sources = []

        for doc in results:
            context_parts.append(doc.page_content)
            source = doc.metadata.get("source", "Unknown")
            if source not in sources:
                sources.append(source)

        context = "\n\n---\n\n".join(context_parts)
        return context, sources

    def get_collection_stats(self) -> dict:
        """Get statistics about the vector store."""
        count = 0
        if self.vectorstore:
            count = self.vectorstore.index.ntotal
        return {
            "total_documents": count,
            "collection_name": "faiss_index",
        }

    def clear_collection(self):
        """Clear all documents from the collection."""
        self.vectorstore = None
        self._document_count = 0
        # Remove saved index
        if os.path.exists(self.faiss_index_path):
            import shutil
            shutil.rmtree(self.faiss_index_path, ignore_errors=True)


# Singleton instance
_rag_service: RAGService | None = None


def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
