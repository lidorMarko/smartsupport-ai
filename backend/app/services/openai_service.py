import json
from openai import OpenAI
from app.config import get_settings
from app.models import ChatMessage
from app.tools.definitions import get_tools
from app.tools.handlers import execute_tool


class OpenAIService:
    def __init__(self):
        settings = get_settings()
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def chat(
        self,
        messages: list[ChatMessage],
        system_prompt: str | None = None,
        context: str | None = None,
    ) -> str:
        """
        Send messages to OpenAI and get a response.

        Args:
            messages: List of chat messages
            system_prompt: Optional system prompt to set behavior
            context: Optional RAG context to include
        """
        openai_messages = []

        # Add system prompt
        if system_prompt:
            openai_messages.append({"role": "system", "content": system_prompt})
        else:
            openai_messages.append(
                {
                    "role": "system",
                    "content": "You are SmartSupport AI, a helpful assistant. Answer questions based on the provided context when available. Be concise and helpful.",
                }
            )

        # Add RAG context if available
        if context:
            openai_messages.append(
                {
                    "role": "system",
                    "content": f"Use the following context to answer the user's question:\n\n{context}",
                }
            )

        # Add conversation messages
        for msg in messages:
            openai_messages.append({"role": msg.role.value, "content": msg.content})

        response = self.client.chat.completions.create(
            model=self.model,
            messages=openai_messages,
            temperature=0.7,
            max_tokens=1000,
        )

        return response.choices[0].message.content or "I couldn't generate a response."

    async def chat_with_tools(
        self,
        messages: list[ChatMessage],
        system_prompt: str | None = None,
        context: str | None = None,
    ) -> dict:
        """
        Send messages to OpenAI with function calling support.
        Returns both the response and any tool calls made.

        This implements an agent loop:
        1. Send message to LLM with available tools
        2. If LLM wants to call a tool, execute it
        3. Send tool result back to LLM
        4. Repeat until LLM gives final response
        """
        openai_messages = []

        # Add system prompt with tool instructions
        base_prompt = system_prompt or "You are SmartSupport AI, a helpful assistant."
        tool_instructions = """

## Available Actions:
You have access to tools to help customers. When a customer needs a technician:
1. Use schedule_technician to book the appointment
2. After scheduling, ask the customer for their email address
3. Once they provide email, use send_confirmation_email to send details

Always confirm actions with the customer and be helpful."""

        openai_messages.append({"role": "system", "content": base_prompt + tool_instructions})

        # Add RAG context if available
        if context:
            openai_messages.append(
                {
                    "role": "system",
                    "content": f"Use the following context to answer the user's question:\n\n{context}",
                }
            )

        # Add conversation messages
        for msg in messages:
            openai_messages.append({"role": msg.role.value, "content": msg.content})

        tools = get_tools()
        tool_calls_made = []

        # Agent loop - keep going until we get a final response
        max_iterations = 5  # Prevent infinite loops
        for _ in range(max_iterations):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=1000,
            )

            assistant_message = response.choices[0].message

            # If no tool calls, we have our final response
            if not assistant_message.tool_calls:
                return {
                    "message": assistant_message.content or "I couldn't generate a response.",
                    "tool_calls": tool_calls_made
                }

            # Process tool calls
            openai_messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })

            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                print(f"[TOOL] Executing: {function_name}")
                print(f"[TOOL] Arguments: {arguments}")

                # Execute the tool
                result = execute_tool(function_name, arguments)

                print(f"[TOOL] Result: {result}")

                tool_calls_made.append({
                    "tool": function_name,
                    "arguments": arguments,
                    "result": result
                })

                # Add tool result to messages
                openai_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False)
                })

        # If we hit max iterations, return what we have
        return {
            "message": "I apologize, but I'm having trouble completing this request.",
            "tool_calls": tool_calls_made
        }

    async def get_embedding(self, text: str) -> list[float]:
        """Get embedding for a text string."""
        settings = get_settings()
        response = self.client.embeddings.create(
            model=settings.openai_embedding_model, input=text
        )
        return response.data[0].embedding


# Singleton instance
_openai_service: OpenAIService | None = None


def get_openai_service() -> OpenAIService:
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service
