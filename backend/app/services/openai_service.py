from openai import OpenAI
from app.config import get_settings
from app.models import ChatMessage


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
