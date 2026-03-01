Build a professional, modern React frontend for FinPol - an AI-Powered Fintech Compliance Monitoring System. The application should be a sophisticated dashboard for financial compliance officers to analyze transactions, assess risks, and ensure regulatory compliance.

Tech Stack:
- React 18+ with TypeScript
- Vite as build tool
- Tailwind CSS for styling
- React Router DOM for navigation
- Axios for API calls
- Recharts for data visualization
- Lucide React for icons

API Endpoints (Backend runs at /api/v1):

Transactions API:
- POST /api/v1/transactions - Create transaction with risk assessment (body: {user_id, amount, currency, transaction_type, description, recipient_account, sender_account, country, merchant_type, device_risk_score})
- POST /api/v1/transactions/analyze - Analyze transaction for risk (body: full Transaction object)
- GET /api/v1/transactions?limit=100&offset=0 - List all transactions
- GET /api/v1/transactions/{id} - Get transaction by ID
- DELETE /api/v1/transactions/{id} - Delete transaction

Compliance API:
- POST /api/v1/compliance/report/{transaction_id}?risk_score=X&risk_level=Y - Generate compliance report
- GET /api/v1/compliance/regulations - List all regulations
- POST /api/v1/compliance/regulations/search - Search regulations (body: {query})

Health API:
- GET /api/v1/health - Health check

Data Models:

TransactionCreate:
{user_id: string, amount: number, currency: string, transaction_type: "transfer"|"payment"|"withdrawal"|"deposit", description: string, recipient_account: string, sender_account: string, country: string, merchant_type: string, device_risk_score: number(0-1)}

TransactionResponse:
{id: string, user_id: string, amount: number, currency: string, transaction_type: string, description: string, recipient_account: string, sender_account: string, country: string, merchant_type: string, device_risk_score: number, timestamp: datetime, risk_score: number, risk_level: string}

RiskResponse:
{transaction_id: string, risk_score: number(0-100), risk_level: "Low"|"Medium"|"High"|"Critical", should_approve: boolean, requires_review: boolean, compliance_explanation: string}

ComplianceReport:
{transaction_id: string, compliance_status: "approved"|"review_required", regulations_applied: string[], violations: string[], recommendations: string[], llm_analysis: string, timestamp: datetime}

UI Requirements:

1. Dashboard (Home):
- Overview cards: Total Transactions, High Risk Transactions, Compliance Rate, Pending Reviews
- Recent transactions table (last 10)
- Risk distribution pie/donut chart
- Transaction volume line chart

2. Transactions Page:
- Searchable/filterable table with columns: ID, Date, User, Amount, Type, Country, Risk Score, Risk Level
- Pagination, click for details modal
- "New Transaction" button

3. Transaction Form:
- Fields: User ID, Amount, Currency dropdown, Transaction Type dropdown, Description, Recipient Account, Sender Account, Country dropdown, Merchant Type dropdown, Device Risk Score slider (0-1)

4. Transaction Detail View:
- Full transaction info, risk breakdown, compliance explanation
- Action buttons: Approve, Flag for Review, Delete

5. Compliance Page:
- Compliance reports list, regulations browser, search functionality

6. Navigation:
- Top navbar with links: Dashboard, Transactions, Compliance

Design:
- Professional financial look: deep blues, clean whites, subtle grays
- Risk colors: Green(Low), Yellow(Medium), Red(High/Critical)
- Card-based layouts with shadows
- Responsive design
- Loading states, toast notifications
