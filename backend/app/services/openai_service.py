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
        include_rag: bool = True,
    ) -> dict:
        """
        Send messages to OpenAI with function calling support.
        Returns both the response and any tool calls made.

        This implements an agent loop:
        1. Send message to LLM with available tools
        2. If LLM wants to call a tool, execute it
        3. Send tool result back to LLM
        4. Repeat until LLM gives final response

        Args:
            messages: List of chat messages
            system_prompt: Optional system prompt to set behavior
            include_rag: Whether to include the knowledge base search tool
        """
        openai_messages = []

        # Add system prompt with intent classification and tool instructions
        base_prompt = system_prompt or "You are SmartSupport AI, a helpful assistant."
        tool_instructions = """

## Your Role
You are an intelligent customer service agent for Mei Avivim (מי אביבים) water company.
You must first understand the customer's INTENT before taking any action.

## Step 1: Intent Classification
Before responding, classify the customer's intent into one of these categories:

| Intent | Description | Action |
|--------|-------------|--------|
| GREETING | Hello, hi, שלום, היי | Respond warmly, no tools needed |
| TECHNICIAN_REQUEST | Reports leak, no water, meter problem, needs טכנאי | Use `schedule_technician` |
| INFORMATION_REQUEST | Questions about services, billing, procedures, prices | Use `search_knowledge_base` |
| WEATHER_QUERY | Asks about weather, מזג אוויר | Use `get_weather` |
| EMAIL_PROVIDED | Customer provides email after scheduling | Use `send_confirmation_email` |
| GENERAL_CHAT | Small talk, thanks, goodbye | Respond naturally, no tools needed |
| UNCLEAR | Cannot determine intent | Ask clarifying question |

## Step 2: Execute Based on Intent

### For TECHNICIAN_REQUEST:
Trigger words: נזילה, נזילת מים, בעיה במונה, לחץ מים נמוך, אין מים, בעיה בצינור, טכנאי, צריך טכנאי
1. Acknowledge the issue
2. Use `schedule_technician` with the reason
3. After success, ask for email: "האם תרצה לקבל אישור במייל? אם כן, אנא שלח לי את כתובת האימייל שלך"

### For INFORMATION_REQUEST:
Trigger: Questions about company services, billing, how to pay, tariffs, opening hours, procedures
1. Use `search_knowledge_base` with relevant query
2. Answer based on the results
3. If no results found, apologize and suggest contacting support

### For WEATHER_QUERY:
1. Use `get_weather` with the city name
2. Include the water-related tip from the response

### For EMAIL_PROVIDED (after technician scheduling):
1. Use `send_confirmation_email` with:
   - The provided email
   - Subject: "אישור תור לטכנאי - מי אביבים"
   - Details: Include confirmation number, date, time from previous scheduling

## Important Rules:
- ALWAYS classify intent first before acting
- Use tools when appropriate - don't just describe what you would do
- Speak in Hebrew (עברית) when the customer writes in Hebrew
- Be concise and helpful
- If the knowledge base has no relevant info, say so honestly"""

        openai_messages.append({"role": "system", "content": base_prompt + tool_instructions})

        # Add conversation messages
        for msg in messages:
            openai_messages.append({"role": msg.role.value, "content": msg.content})

        # Get tools - conditionally include RAG tool based on setting
        tools = get_tools(include_rag=include_rag)
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
