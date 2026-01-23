# SmartSupport AI

A chatbot application for practicing AI agent fundamentals including RAG (Retrieval-Augmented Generation), GPT integration, function calling (tools), and prompt engineering.

## Features

- **Chat Interface** - React-based chat UI with real-time messaging
- **AI Agent with Tools** - Function calling capabilities for real actions
- **RAG as a Tool** - Agent decides when to search the knowledge base
- **Intent Classification** - Agent classifies user intent before acting
- **Prompt Engineering** - Switch between different system prompts to compare quality
- **Toggle Controls** - Enable/disable RAG and Tools independently

## Agent Tools

| Tool | Description |
|------|-------------|
| `schedule_technician` | Schedule a technician visit for water issues |
| `send_confirmation_email` | Send email confirmation to customers |
| `get_weather` | Fetch real-time weather from Open-Meteo API |
| `search_knowledge_base` | Search company documents (RAG) |

## Architecture

```
User Message
     │
     ▼
┌─────────────────────────────────┐
│     Intent Classification       │
│  (GREETING, TECHNICIAN_REQUEST, │
│   INFORMATION_REQUEST, etc.)    │
└─────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────┐
│      Tool Selection             │
│  Agent decides which tool(s)    │
│  to use based on intent         │
└─────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────┐
│      Tool Execution             │
│  - schedule_technician          │
│  - search_knowledge_base        │
│  - get_weather                  │
│  - send_confirmation_email      │
└─────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────┐
│      Response Generation        │
│  Final response to user         │
└─────────────────────────────────┘
```

## Tech Stack

**Frontend:**
- React 19 + TypeScript
- Vite
- CSS

**Backend:**
- FastAPI (Python)
- OpenAI API (GPT-4 with function calling)
- LangChain
- FAISS (vector store)

## Setup

### Prerequisites
- Node.js 18+
- Python 3.11+
- OpenAI API key

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run the server
uvicorn app.main:app --reload
```

### Frontend

```bash
npm install
npm run dev
```

## Usage

1. Start the backend server (port 8000)
2. Start the frontend dev server (port 5173)
3. Open http://localhost:5173

### Toggle Controls

| Toggle | Effect |
|--------|--------|
| **Tools ON** | Agent can use function calling (schedule, email, weather, search) |
| **Tools OFF** | Simple chat without tools |
| **RAG ON** | Agent has access to `search_knowledge_base` tool |
| **RAG OFF** | Agent cannot search the knowledge base |

### Loading Documents for RAG

```bash
# Load documents from the documents folder
curl -X POST http://localhost:8000/api/documents/load-directory \
  -H "Content-Type: application/json" \
  -d '{"directory": "./documents"}'
```

Supported formats: `.txt`, `.pdf`, `.docx`

### System Prompts

Three prompts available for comparing prompt engineering quality:

| Prompt | Description |
|--------|-------------|
| פרומפט מהונדס היטב | Well-engineered with clear instructions, structure, and examples |
| פרומפט חלש | Poor engineering - vague, minimal instructions |
| ללא הנדסת פרומפט | No engineering - just "נציג מי אביבים" |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | Send message and get AI response (with optional tools) |
| GET | `/api/prompts` | Get available system prompts |
| POST | `/api/documents/upload` | Upload a document |
| POST | `/api/documents/load-directory` | Load documents from directory |
| GET | `/api/documents/stats` | Get knowledge base stats |
| DELETE | `/api/documents/clear` | Clear knowledge base |

## Project Structure

```
smartsupport-ai/
├── src/                    # Frontend
│   ├── components/
│   │   ├── ChatWindow.tsx
│   │   ├── ChatMessage.tsx
│   │   └── ChatInput.tsx
│   ├── hooks/
│   │   └── useChat.ts
│   ├── services/
│   │   └── chatService.ts
│   └── types/
│       └── chat.ts
├── backend/
│   └── app/
│       ├── main.py
│       ├── models/
│       ├── routers/
│       │   ├── chat.py
│       │   └── documents.py
│       ├── services/
│       │   ├── openai_service.py
│       │   └── rag_service.py
│       ├── tools/
│       │   ├── definitions.py   # Tool schemas for OpenAI
│       │   └── handlers.py      # Tool implementations
│       └── prompts.py
└── documents/              # RAG documents
```

## Example Interactions

**Technician Request:**
```
User: יש לי נזילה בבית
Agent: [Classifies as TECHNICIAN_REQUEST]
       [Calls schedule_technician]
       "קבעתי לך טכנאי לתאריך... האם תרצה אישור במייל?"
```

**Information Request:**
```
User: מה התעריפים למים?
Agent: [Classifies as INFORMATION_REQUEST]
       [Calls search_knowledge_base]
       [Returns answer based on documents]
```

**Weather Query:**
```
User: מה מזג האוויר בתל אביב?
Agent: [Classifies as WEATHER_QUERY]
       [Calls get_weather]
       "מזג האוויר בתל אביב: 25°C, שמיים בהירים..."
```
