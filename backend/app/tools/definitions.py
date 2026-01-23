"""
Tool definitions for OpenAI function calling.
These define WHAT tools are available to the agent.
"""

# Core tools that are always available (when tools are enabled)
CORE_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "schedule_technician",
            "description": "Schedule a technician visit for a customer. Use this when the customer requests a technician, reports a leak, or needs help with water meter issues.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "The reason for the technician visit (e.g., 'בדיקת נזילה', 'בעיה במונה', 'לחץ מים נמוך')"
                    },
                    "preferred_date": {
                        "type": "string",
                        "description": "Preferred date for the visit (optional)"
                    }
                },
                "required": ["reason"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather information for a city in Israel. Use this when customers ask about weather, or to provide context about water usage during hot/cold days.",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name in Israel (e.g., 'תל אביב', 'ירושלים', 'חיפה', 'Tel Aviv', 'Jerusalem', 'Haifa')"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_confirmation_email",
            "description": "Send an email confirmation to the customer with appointment or request details. Use this AFTER scheduling a technician and AFTER the customer provides their email address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "Customer's email address"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject"
                    },
                    "details": {
                        "type": "string",
                        "description": "Details to include in the email (appointment time, reason, etc.)"
                    }
                },
                "required": ["email", "subject", "details"]
            }
        }
    }
]

# RAG tool - only included when RAG is enabled
RAG_TOOL = {
    "type": "function",
    "function": {
        "name": "search_knowledge_base",
        "description": "Search the company knowledge base for information about Mei Avivim water company services, billing, procedures, policies, and FAQs. Use this when the customer asks questions about company services, billing, how things work, or needs factual information that might be in company documents.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query - what information to look for (e.g., 'תעריפי מים', 'איך לשלם חשבון', 'שעות פעילות')"
                }
            },
            "required": ["query"]
        }
    }
}


def get_tools(include_rag: bool = True) -> list:
    """
    Return available tools for the agent.

    Args:
        include_rag: Whether to include the knowledge base search tool
    """
    tools = CORE_TOOLS.copy()
    if include_rag:
        tools.append(RAG_TOOL)
    return tools
