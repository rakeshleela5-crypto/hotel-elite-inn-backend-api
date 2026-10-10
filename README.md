# Hotel Elite Inn - Cloud PMS & POS Backend API

High-performance **FastAPI** & **PostgreSQL** cloud backend API designed for **Hotel Elite Inn** (Rayagada, Odisha). Fully integrates Front Desk PMS, IDS Fortune NEXT Win32 POS, Manager Mobile Operations, Store Inventory, Corporate Receivables, and Night Audit.

Built for automated continuous deployment on **Railway** with direct connectivity to **Cloudflare Pages**.

---

## 🚀 Key Features

1. **Front Desk & Reservations**:
   - Room matrix management (Deluxe, Super Deluxe, Executive Suites)
   - Walk-in reservation booking
   - Physical key handover verification & check-in/checkout flow

2. **IDS Fortune NEXT Restaurant POS**:
   - Live table management with running bill tracking
   - Kitchen Order Ticket (KOT) generation (80mm & 58mm thermal printer ready)
   - **Table Merging**: One-click merging of multiple tables for single consolidated billing
   - **Item-level Voiding**: Manager PIN authorized cancellations with statutory reasons (e.g. *Guest Disliked Taste / Food Quality Reject*)

3. **Store & Kitchen Inventory**:
   - Real-time stock monitor (Basmati Rice, Andhra Chicken, Oil, Milk, Paneer, LPG)
   - Minimum reorder level tracking and low stock alerts

4. **Corporate Accounts Receivables & Aging**:
   - Direct ledger billing for industrial corporate partners (Ashok Leyland, Utkal Alumina, Linde India, JK Paper Mills)
   - Aging status and payment recording

5. **Night Audit & Day Closures**:
   - Room charge posting, F&B settlement sync, cash drawer reconciliation, and corporate aging sign-off

---

## 🛠️ Architecture & Tech Stack

- **Framework**: FastAPI (Python 3.11+)
- **Server**: Uvicorn (ASGI)
- **Database**: PostgreSQL (Managed on Railway) via SQLAlchemy 2.0 ORM
- **Deployment Platform**: Railway (`Procfile` / Nixpacks)
- **Interactive Documentation**: Swagger UI at `/docs` and ReDoc at `/redoc`

---

## ⚙️ Environment Variables

Configure these variables in your Railway project dashboard or local `.env`:

| Variable | Description | Example |
| :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/railway` |
| `PORT` | HTTP port provided by Railway | `8000` |
| `MANAGER_PIN` | Statutory override PIN | `4321` |
| `CORS_ORIGINS` | Allowed frontend domains | `https://hotel-elite-inn.pages.dev,*` |

---

## 🏃 Local Development

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rakeshleela5-crypto/hotel-elite-inn-backend-api.git
   cd hotel-elite-inn-backend-api
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the API server**:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

4. **Access the API**:
   - API Root: `http://localhost:8000/`
   - Swagger Docs: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/health`

---

## 🌐 Deploy to Railway (3 Steps)

1. **Login to Railway**: Go to [railway.com](https://railway.com) and click **Login with GitHub**.
2. **Provision Database**: Click **+ New Project** → **Provision PostgreSQL**.
3. **Deploy API Service**: Click **+ Create** → **GitHub Repo** → select `hotel-elite-inn-backend-api`.
   - In Variables, add: `DATABASE_URL = ${{Postgres.DATABASE_URL}}`
   - Under Settings → Networking, click **Generate Domain**.
