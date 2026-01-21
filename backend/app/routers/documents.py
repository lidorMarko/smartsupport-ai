from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from app.services.rag_service import get_rag_service
import tempfile
import os

router = APIRouter(prefix="/documents", tags=["documents"])


class AddTextRequest(BaseModel):
    texts: list[str]
    metadatas: list[dict] | None = None


class LoadDirectoryRequest(BaseModel):
    directory_path: str


class AddTextResponse(BaseModel):
    chunks_added: int
    message: str


class StatsResponse(BaseModel):
    total_documents: int
    collection_name: str


@router.post("/add-text", response_model=AddTextResponse)
async def add_text(request: AddTextRequest) -> AddTextResponse:
    """
    Add raw text to the knowledge base.
    """
    try:
        rag_service = get_rag_service()
        chunks_added = rag_service.add_texts(request.texts, request.metadatas)

        return AddTextResponse(
            chunks_added=chunks_added,
            message=f"Successfully added {chunks_added} chunks to the knowledge base.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload", response_model=AddTextResponse)
async def upload_document(file: UploadFile = File(...)) -> AddTextResponse:
    """
    Upload a document (PDF, TXT, DOCX, MD) to the knowledge base.
    """
    allowed_extensions = {".pdf", ".txt", ".docx", ".doc", ".md"}
    file_ext = os.path.splitext(file.filename or "")[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported. Allowed: {', '.join(allowed_extensions)}",
        )

    try:
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_path = temp_file.name

        try:
            rag_service = get_rag_service()

            # Load based on file type
            from langchain_community.document_loaders import (
                TextLoader,
                PyPDFLoader,
                Docx2txtLoader,
            )

            if file_ext == ".pdf":
                loader = PyPDFLoader(temp_path)
            elif file_ext in [".docx", ".doc"]:
                loader = Docx2txtLoader(temp_path)
            else:  # .txt, .md
                loader = TextLoader(temp_path, encoding="utf-8")

            documents = loader.load()

            # Add source metadata
            for doc in documents:
                doc.metadata["source"] = file.filename

            chunks_added = rag_service.add_documents(documents)

            return AddTextResponse(
                chunks_added=chunks_added,
                message=f"Successfully processed '{file.filename}' and added {chunks_added} chunks.",
            )
        finally:
            # Clean up temp file
            os.unlink(temp_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/load-directory", response_model=AddTextResponse)
async def load_directory(request: LoadDirectoryRequest) -> AddTextResponse:
    """
    Load all documents from a directory into the knowledge base.
    """
    try:
        rag_service = get_rag_service()
        chunks_added = rag_service.load_directory(request.directory_path)

        return AddTextResponse(
            chunks_added=chunks_added,
            message=f"Successfully loaded directory and added {chunks_added} chunks.",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats", response_model=StatsResponse)
async def get_stats() -> StatsResponse:
    """
    Get statistics about the knowledge base.
    """
    try:
        rag_service = get_rag_service()
        stats = rag_service.get_collection_stats()

        return StatsResponse(**stats)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/clear")
async def clear_documents():
    """
    Clear all documents from the knowledge base.
    """
    try:
        rag_service = get_rag_service()
        rag_service.clear_collection()

        return {"message": "Knowledge base cleared successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
