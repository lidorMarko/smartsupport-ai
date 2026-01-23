"""
Tool handlers - the actual implementation of each tool.
These define HOW each tool works when called.
"""

import random
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from app.config import get_settings


# City coordinates for Israel (latitude, longitude)
ISRAEL_CITIES = {
    # Hebrew names
    "תל אביב": (32.0853, 34.7818),
    "ירושלים": (31.7683, 35.2137),
    "חיפה": (32.7940, 34.9896),
    "באר שבע": (31.2530, 34.7915),
    "אילת": (29.5577, 34.9519),
    "נתניה": (32.3215, 34.8532),
    "אשדוד": (31.8044, 34.6553),
    "ראשון לציון": (31.9642, 34.8044),
    "פתח תקווה": (32.0841, 34.8878),
    "הרצליה": (32.1663, 34.8463),
    # English names
    "tel aviv": (32.0853, 34.7818),
    "jerusalem": (31.7683, 35.2137),
    "haifa": (32.7940, 34.9896),
    "beer sheva": (31.2530, 34.7915),
    "eilat": (29.5577, 34.9519),
    "netanya": (32.3215, 34.8532),
    "ashdod": (31.8044, 34.6553),
    "rishon lezion": (31.9642, 34.8044),
    "petah tikva": (32.0841, 34.8878),
    "herzliya": (32.1663, 34.8463),
}


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
    Send a confirmation email to the customer via Gmail SMTP.
    """
    # Validate email format (basic check)
    if "@" not in email or "." not in email:
        return {
            "success": False,
            "message": "כתובת האימייל אינה תקינה"
        }

    settings = get_settings()

    # Check if email credentials are configured
    if not settings.smtp_email or not settings.smtp_password:
        print("[EMAIL] SMTP credentials not configured, simulating send")
        return {
            "success": True,
            "message": f"(סימולציה) אימייל נשלח לכתובת {email}"
        }

    try:
        # Create the email message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.smtp_email
        msg["To"] = email

        # Create HTML email body
        html_body = f"""
        <html dir="rtl">
        <body style="font-family: Arial, sans-serif; direction: rtl;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">מי אביבים - אישור</h2>
                <div style="background: #f3f4f6; padding: 20px; border-radius: 8px;">
                    {details.replace(chr(10), '<br>')}
                </div>
                <p style="margin-top: 20px; color: #6b7280; font-size: 14px;">
                    תודה שפנית לשירות הלקוחות של מי אביבים.
                </p>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(details, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        # Send via Gmail SMTP
        print(f"[EMAIL] Connecting to Gmail SMTP...")
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(settings.smtp_email, settings.smtp_password)
            server.sendmail(settings.smtp_email, email, msg.as_string())

        print(f"[EMAIL] Successfully sent to: {email}")
        return {
            "success": True,
            "message": f"אימייל נשלח בהצלחה לכתובת {email}"
        }

    except smtplib.SMTPAuthenticationError:
        print("[EMAIL] Authentication failed - check SMTP credentials")
        return {
            "success": False,
            "message": "שגיאת אימות - בדוק את הגדרות האימייל"
        }
    except Exception as e:
        print(f"[EMAIL] Error sending email: {e}")
        return {
            "success": False,
            "message": f"שגיאה בשליחת האימייל: {str(e)}"
        }


def get_weather(city: str) -> dict:
    """
    Get current weather for a city in Israel using Open-Meteo API (free, no API key needed).
    """
    # Normalize city name to lowercase for lookup
    city_lower = city.lower().strip()

    # Try to find coordinates for the city
    coords = ISRAEL_CITIES.get(city_lower) or ISRAEL_CITIES.get(city.strip())

    if not coords:
        # Default to Tel Aviv if city not found
        coords = ISRAEL_CITIES["תל אביב"]
        city = "תל אביב"

    latitude, longitude = coords

    try:
        # Call Open-Meteo API (free, no key required)
        url = f"https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current_weather": True,
            "timezone": "Asia/Jerusalem"
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        current = data.get("current_weather", {})
        temp = current.get("temperature", "N/A")
        windspeed = current.get("windspeed", "N/A")
        weather_code = current.get("weathercode", 0)

        # Translate weather codes to Hebrew descriptions
        weather_descriptions = {
            0: "שמיים בהירים ☀️",
            1: "בעיקר בהיר 🌤️",
            2: "מעונן חלקית ⛅",
            3: "מעונן ☁️",
            45: "ערפל 🌫️",
            48: "ערפל כבד 🌫️",
            51: "טפטוף קל 🌧️",
            53: "טפטוף 🌧️",
            55: "טפטוף כבד 🌧️",
            61: "גשם קל 🌧️",
            63: "גשם 🌧️",
            65: "גשם כבד 🌧️",
            80: "ממטרים קלים 🌦️",
            81: "ממטרים 🌦️",
            82: "ממטרים כבדים 🌦️",
            95: "סופת רעמים ⛈️",
        }

        description = weather_descriptions.get(weather_code, "לא ידוע")

        # Add water-related tip based on weather
        if temp != "N/A" and float(temp) > 30:
            tip = "🔥 מזג אוויר חם! מומלץ לשתות הרבה מים ולהשקות צמחים בשעות הערב."
        elif temp != "N/A" and float(temp) < 10:
            tip = "❄️ מזג אוויר קר. שימו לב לצינורות חשופים שעלולים להקפיא."
        elif weather_code in [61, 63, 65, 80, 81, 82]:
            tip = "🌧️ יורד גשם. זה הזמן לבדוק שמערכת הניקוז תקינה."
        else:
            tip = "💧 זכרו לשמור על צריכת מים אחראית."

        return {
            "success": True,
            "city": city,
            "temperature": f"{temp}°C",
            "description": description,
            "wind_speed": f"{windspeed} קמ\"ש",
            "tip": tip,
            "message": f"מזג האוויר ב{city}: {temp}°C, {description}. {tip}"
        }

    except requests.RequestException as e:
        print(f"[WEATHER] API error: {e}")
        return {
            "success": False,
            "message": f"לא הצלחתי לקבל מידע על מזג האוויר. נסה שוב מאוחר יותר."
        }


def search_knowledge_base(query: str) -> dict:
    """
    Search the company knowledge base using RAG.
    This is now a tool that the agent decides when to use.
    """
    from app.services.rag_service import get_rag_service

    print(f"[RAG TOOL] Searching for: {query}")

    try:
        rag_service = get_rag_service()
        context, sources = rag_service.query(query)

        if not context:
            return {
                "success": True,
                "found": False,
                "message": "לא נמצא מידע רלוונטי במאגר הידע.",
                "context": "",
                "sources": []
            }

        print(f"[RAG TOOL] Found {len(context)} chars from {len(sources)} sources")

        return {
            "success": True,
            "found": True,
            "context": context,
            "sources": sources,
            "message": f"נמצא מידע רלוונטי מ-{len(sources)} מקורות."
        }

    except Exception as e:
        print(f"[RAG TOOL] Error: {e}")
        return {
            "success": False,
            "found": False,
            "message": f"שגיאה בחיפוש במאגר הידע: {str(e)}",
            "context": "",
            "sources": []
        }


# Map function names to their handlers
TOOL_HANDLERS = {
    "schedule_technician": schedule_technician,
    "send_confirmation_email": send_confirmation_email,
    "get_weather": get_weather,
    "search_knowledge_base": search_knowledge_base,
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
