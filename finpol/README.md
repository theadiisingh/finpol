# FinPol - Financial Compliance AI

A production-ready fintech AI project for financial compliance and risk assessment.

## Tech Stack

### Backend
- FastAPI (Python)
- LangChain + FAISS for AI/RAG
- Rule-based Risk Engine
- Pydantic for data validation

### Frontend
- React + TypeScript
- Vite
- Tailwind CSS
- React Router

## Project Structure

```
finpol/
├── backend/           # FastAPI backend
│   ├── app/
│   │   ├── api/      # API routes
│   │   ├── models/   # Pydantic models
│   │   ├── services/ # Business logic
│   │   ├── rag/      # RAG system
│   │   ├── utils/    # Utilities
│   │   └── core/     # Core functionality
│   ├── tests/        # Tests
│   └── Dockerfile
├── frontend/         # React frontend
│   ├── src/
│   │   ├── pages/   # Page components
│   │   ├── components/ # Reusable components
│   │   └── services/ # API services
│   └── package.json
└── README.md
```

## Getting Started

### Backend

```
bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Configure your .env file
uvicorn app.main:app --reload
```

### Frontend

```
bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### Docker

```
bash
# Backend only
cd backend
docker-compose up

# Full stack (add your own docker-compose)
```

## API Endpoints

- `GET /api/v1/health` - Health check
- `POST /api/v1/transactions` - Create transaction
- `GET /api/v1/transactions` - List transactions
- `POST /api/v1/transactions/{id}/analyze` - Analyze transaction
- `GET /api/v1/compliance/reports` - Get compliance reports
- `GET /api/v1/compliance/regulations` - Get regulations

## License

MIT
