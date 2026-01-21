# SmartSupport AI

A chatbot application for practicing AI agent fundamentals including RAG (Retrieval-Augmented Generation), GPT integration, and prompt engineering.

## Features

- **Chat Interface** - React-based chat UI with real-time messaging
- **RAG Support** - Load documents and use them as context for responses
- **Prompt Engineering** - Switch between different system prompts to see how prompt quality affects responses
- **Toggle RAG** - Compare responses with and without document context

## Tech Stack

**Frontend:**
- React 19 + TypeScript
- Vite
- CSS

**Backend:**
- FastAPI (Python)
- OpenAI API (GPT-4)
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
| POST | `/api/chat` | Send message and get AI response |
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
│       └── prompts.py
└── documents/              # RAG documents
```
