"""
Tool handlers - the actual implementation of each tool.
These define HOW each tool works when called.
"""

import random
from datetime import datetime, timedelta


def schedule_technician(reason: str, preferred_date: str = None) -> dict:
    """
    Schedule a technician visit.
    In a real system, this would integrate with a scheduling system.
    For demo purposes, we simulate a successful booking.
    """
    # Simulate scheduling - in real life this would call a scheduling API
    if preferred_date:
        scheduled_date = preferred_date
    else:
        # Schedule for 2-3 days from now
        days_ahead = random.randint(2, 4)
        scheduled_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%d/%m/%Y")

    # Random time slot
    time_slots = ["08:00-10:00", "10:00-12:00", "12:00-14:00", "14:00-16:00"]
    scheduled_time = random.choice(time_slots)

    # Generate confirmation number
    confirmation_number = f"TEC-{random.randint(10000, 99999)}"

    return {
        "success": True,
        "confirmation_number": confirmation_number,
        "scheduled_date": scheduled_date,
        "scheduled_time": scheduled_time,
        "reason": reason,
        "message": f"טכנאי נקבע לתאריך {scheduled_date} בין השעות {scheduled_time}. מספר אישור: {confirmation_number}"
    }


def send_confirmation_email(email: str, subject: str, details: str) -> dict:
    """
    Send a confirmation email to the customer.
    In a real system, this would use an email service (SendGrid, SES, etc.)
    For demo purposes, we simulate sending.
    """
    # Validate email format (basic check)
    if "@" not in email or "." not in email:
        return {
            "success": False,
            "message": "כתובת האימייל אינה תקינה"
        }

    # Simulate sending email - in real life this would call an email API
    print(f"[EMAIL] Sending to: {email}")
    print(f"[EMAIL] Subject: {subject}")
    print(f"[EMAIL] Details: {details}")

    return {
        "success": True,
        "message": f"אימייל נשלח בהצלחה לכתובת {email}"
    }


# Map function names to their handlers
TOOL_HANDLERS = {
    "schedule_technician": schedule_technician,
    "send_confirmation_email": send_confirmation_email,
}


def execute_tool(tool_name: str, arguments: dict) -> dict:
    """Execute a tool by name with the given arguments."""
    handler = TOOL_HANDLERS.get(tool_name)
    if not handler:
        return {"success": False, "message": f"Unknown tool: {tool_name}"}

    try:
        return handler(**arguments)
    except Exception as e:
        return {"success": False, "message": f"Tool execution error: {str(e)}"}
