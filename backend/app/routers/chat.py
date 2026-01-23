from fastapi import APIRouter, HTTPException
from app.models import ChatRequest, ChatResponse
from app.services.openai_service import get_openai_service
from app.services.rag_service import get_rag_service
from app.prompts import get_prompt_by_key

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Send a message and get an AI response.

    If use_tools is True, the agent can use tools (function calling)
    to perform actions like scheduling technicians, sending emails, or searching the knowledge base.

    If use_rag is True AND use_tools is True, the agent will have access to the
    `search_knowledge_base` tool and can decide when to use it based on intent.

    If use_rag is True AND use_tools is False, RAG context is automatically injected (legacy mode).
    """
    try:
        openai_service = get_openai_service()

        # Get the selected system prompt
        system_prompt = get_prompt_by_key(request.prompt_key)
        print(f"[PROMPT] Using: {request.prompt_key}")
        print(f"[TOOLS] Enabled: {request.use_tools}")
        print(f"[RAG] Enabled: {request.use_rag}")

        # Get AI response - with or without tools
        if request.use_tools:
            # Use agent with function calling
            # RAG is now a tool - the agent decides when to search
            result = await openai_service.chat_with_tools(
                messages=request.messages,
                system_prompt=system_prompt,
                include_rag=request.use_rag,  # Pass RAG toggle to include/exclude the tool
            )

            # Extract sources from tool calls if knowledge base was searched
            sources = None
            if result["tool_calls"]:
                for tc in result["tool_calls"]:
                    if tc["tool"] == "search_knowledge_base" and tc["result"].get("sources"):
                        sources = tc["result"]["sources"]
                        break

            return ChatResponse(
                message=result["message"],
                sources=sources,
                tool_calls=result["tool_calls"] if result["tool_calls"] else None,
            )
        else:
            # Simple chat without tools - use legacy RAG injection if enabled
            context = None
            sources = None

            if request.use_rag:
                try:
                    rag_service = get_rag_service()
                    # Get the last user message for RAG query
                    user_messages = [m for m in request.messages if m.role.value == "user"]
                    if user_messages:
                        rag_query = user_messages[-1].content
                        print(f"[RAG LEGACY] Query: {rag_query}")
                        context, sources = rag_service.query(rag_query)
                        print(f"[RAG LEGACY] Found: {len(context) if context else 0} chars")
                except Exception as e:
                    print(f"[RAG LEGACY] Error: {e}")

            response = await openai_service.chat(
                messages=request.messages,
                system_prompt=system_prompt,
                context=context,
            )
            return ChatResponse(
                message=response,
                sources=sources,
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
