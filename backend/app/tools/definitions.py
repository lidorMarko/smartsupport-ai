"""
Tool definitions for OpenAI function calling.
These define WHAT tools are available to the agent.
"""

TOOLS = [
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


def get_tools():
    """Return all available tools for the agent."""
    return TOOLS
