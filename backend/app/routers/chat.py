from fastapi import APIRouter, HTTPException
from app.models import ChatRequest, ChatResponse
from app.services.openai_service import get_openai_service
from app.services.rag_service import get_rag_service
from app.prompts import get_prompt_by_key

router = APIRouter(prefix="/chat", tags=["chat"])


def build_rag_query(messages: list) -> str:
    """
    Build a RAG query from recent conversation context.
    Uses last few messages to maintain context for follow-up questions.
    """
    # Get last 3 user messages for context (or fewer if not available)
    user_messages = [m for m in messages if m.role.value == "user"]
    recent_messages = user_messages[-3:] if len(user_messages) > 3 else user_messages

    # Combine them into a single query for better RAG retrieval
    if len(recent_messages) == 1:
        return recent_messages[0].content

    # For follow-up questions, combine recent context
    query_parts = [m.content for m in recent_messages]
    return " | ".join(query_parts)


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a message and get an AI response.

    If use_rag is True, the system will search for relevant context
    from the document store before generating a response.
    """
    try:
        openai_service = get_openai_service()
        context = None
        sources = None

        # Get the selected system prompt
        system_prompt = get_prompt_by_key(request.prompt_key)
        print(f"[PROMPT] Using: {request.prompt_key}")

        # Get RAG context if enabled
        if request.use_rag:
            try:
                rag_service = get_rag_service()
                # Build query from recent conversation for better context
                rag_query = build_rag_query(request.messages)
                print(f"[RAG] Query: {rag_query}")

                if rag_query:
                    context, sources = rag_service.query(rag_query)
                    print(f"[RAG] Found context: {len(context) if context else 0} chars")
                    print(f"[RAG] Sources: {sources}")
                    if context:
                        print(f"[RAG] Context preview: {context[:200]}...")
            except Exception as e:
                # RAG failed, continue without context
                print(f"[RAG] Error (continuing without context): {e}")

        # Get AI response with selected prompt
        response = await openai_service.chat(
            messages=request.messages,
            system_prompt=system_prompt,
            context=context if context else None,
        )

        return ChatResponse(
            message=response,
            sources=sources if sources else None,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/simple", response_model=ChatResponse)
async def chat_simple(request: ChatRequest) -> ChatResponse:
    """
    Simple chat without RAG - direct OpenAI call.
    """
    try:
        openai_service = get_openai_service()
        system_prompt = get_prompt_by_key(request.prompt_key)
        response = await openai_service.chat(
            messages=request.messages,
            system_prompt=system_prompt,
        )

        return ChatResponse(message=response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
