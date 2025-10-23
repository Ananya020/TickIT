


# 🧭 TickIT — Smart AI-Powered IT Helpdesk Platform

TickIT is an intelligent ticket management and resolution platform that blends the efficiency of modern issue tracking with the power of AI-driven insights.  
It’s designed to streamline IT support, improve SLA compliance, and deliver actionable analytics for both end users and administrators.

---

## 🚀 Overview

### 🎯 Key Features
- **AI Ticket Classification:** Auto-categorizes incoming issues based on description and context.
- **Smart Recommendations:** Suggests potential resolutions from a knowledge base using semantic search (FAISS + Sentence Transformers).
- **SLA Risk Prediction:** Predicts possible SLA breaches based on ticket priority and open time.
- **Anomaly Detection:** Identifies unusual ticket spikes or category surges using Isolation Forest.
- **Role-Based Access:** Separate dashboards and permissions for Admin, Analyst, and End User roles.
- **Insightful Dashboard:** View KPIs, trends, and recent ticket activity in real time.
- **MySQL/SQLite Support:** Easy database setup — switch between lightweight dev or full production DBs.

---

## 🧩 Tech Stack

| Layer | Technology |
|-------|-------------|
| **Frontend** | Next.js (App Router) + TypeScript + Tailwind CSS + SWR + shadcn/ui |
| **Backend** | FastAPI + SQLAlchemy + Pydantic + PyOD + FAISS + SentenceTransformers |
| **Database** | MySQL (prod) / SQLite (dev) |
| **AI Models** | `all-MiniLM-L6-v2` (SentenceTransformer) for semantic recommendations |
| **Authentication** | JWT-based login system |
| **Logging & Monitoring** | Python `logging` module + structured logs |
| **Dev Environment** | Python 3.12 + Node.js 18+ |

---

## 🏗️ Architecture

```

helpboard/
├── backend/
│   ├── main.py                 # FastAPI entrypoint
│   ├── database/
│   │   ├── db_connect.py       # MySQL/SQLite connection setup
│   ├── routers/
│   │   ├── tickets.py          # CRUD operations for tickets
│   │   ├── classify.py         # AI classification endpoint
│   │   ├── recommend.py        # Semantic recommendation
│   │   ├── anomaly.py          # Anomaly detection (Isolation Forest)
│   │   ├── sla.py              # SLA risk predictor
│   │   ├── auth.py             # Login & user roles
│   ├── schemas/                # Pydantic models for validation
│   ├── utils/logger.py         # Centralized logging config
│   └── ...
│
├── frontend/
│   ├── app/
│   │   ├── dashboard/          # Main dashboard page
│   │   ├── tickets/[id]/       # Ticket details view
│   ├── components/
│   │   ├── kpi-card.tsx
│   │   ├── trend-chart.tsx
│   │   ├── recent-tickets-table.tsx
│   │   └── ...
│   ├── lib/api.ts              # API wrapper
│   ├── styles/
│   └── ...
│
└── README.md

````

---

## ⚙️ Setup Instructions

### 🧠 Backend Setup

1. **Create a virtual environment**
   ```
   python -m venv .venv
   source .venv/bin/activate    # or .venv\Scripts\activate on Windows
```

2. **Install dependencies**

   ```
   pip install -r requirements.txt
   ```

3. **Database setup (MySQL or SQLite)**

   * For MySQL, create a database manually:

     ```
     CREATE DATABASE helpboard;
     ```
   * Add your connection URL to `.env`:

     ```
     DATABASE_URL=mysql+pymysql://<user>:<password>@localhost/helpboard
     ```

4. **Run backend server**

   ```bash
   uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
   ```

5. **Access API Docs**

   * Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   * ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

---

### 💻 Frontend Setup

1. **Install dependencies**

   ```bash
   cd frontend
   npm install
   ```

2. **Run the development server**

   ```bash
   npm run dev
   ```

3. **Visit**

   ```
   http://localhost:3000
   ```

4. The frontend automatically connects to the backend (`http://127.0.0.1:8000`).

---

## 🤖 AI Components

| Component               | Model                                    | Purpose                                                 |
| ----------------------- | ---------------------------------------- | ------------------------------------------------------- |
| **Auto Classification** | `SentenceTransformer (all-MiniLM-L6-v2)` | Understands and classifies tickets based on description |
| **Recommendations**     | FAISS + Semantic Embeddings              | Finds similar tickets from historical data              |
| **Anomaly Detection**   | PyOD Isolation Forest                    | Detects spikes in ticket volume                         |
| **SLA Prediction**      | Rule-based + ML-ready placeholder        | Estimates risk of breach for ongoing tickets            |

> 💡 All AI models are lightweight and run locally — perfect for MVP and hackathon use.

---

## 🔐 Roles and Access

| Role         | Permissions                                               |
| ------------ | --------------------------------------------------------- |
| **Admin**    | Full access to analytics, anomaly detection, SLA overview |
| **Analyst**  | View dashboards and insights                              |
| **End User** | Create tickets, view own tickets, get AI suggestions      |

---

## 📊 Dashboard Overview

**KPIs**

* Total Tickets
* Open Tickets
* Resolved Today
* Avg. Resolution Time

**Trend Chart**

* Tracks open/resolved tickets daily
* Powered by `recharts` with live data or mock fallback

**Recent Tickets**

* Displays last 10 created tickets

---

## 🌍 Alignment with SDGs (UN Sustainable Development Goals)
```

| Goal                                                 | Contribution                                                      |
| ---------------------------------------------------- | ----------------------------------------------------------------- |
| **SDG 8 – Decent Work & Economic Growth**            | Reduces downtime, improving IT productivity                       |
| **SDG 9 – Industry, Innovation, and Infrastructure** | Integrates AI for smarter, scalable infrastructure management     |
| **SDG 12 – Responsible Consumption**                 | Automates repetitive work, minimizing resource usage              |
| **SDG 16 – Peace, Justice, and Strong Institutions** | Improves transparency and accountability in IT support operations |
```
---

## 📈 Scalability Roadmap

* **Phase 1:** Local MVP (SQLite + local model inference)
* **Phase 2:** Migrate to cloud-hosted MySQL + Hugging Face endpoint
* **Phase 3:** Add role-based multi-tenant support
* **Phase 4:** Integrate with enterprise tools (e.g., Jira, Slack, ServiceNow)
* **Phase 5:** Deploy on Docker + CI/CD (GitHub Actions)

---

## 🧪 Example API Endpoints

| Endpoint                    | Method | Description                        |
| --------------------------- | ------ | ---------------------------------- |
| `/tickets/create`           | `POST` | Create new ticket                  |
| `/tickets/{id}`             | `GET`  | Get ticket details                 |
| `/tickets/update/{id}`      | `PUT`  | Update ticket info                 |
| `/dashboard/metrics`        | `GET`  | Get KPI metrics                    |
| `/dashboard/trends`         | `GET`  | Get ticket trends                  |
| `/classify/ticket`          | `POST` | AI-based ticket classification     |
| `/recommend/resolutions`    | `POST` | Fetch recommended resolutions      |
| `/anomaly/detect_anomalies` | `GET`  | Detect unusual spikes (Admin only) |

---

## 🧰 Mock Mode for Demo (Hackathon Safe)

If APIs are not fully working, the app gracefully falls back to **mock data**:

* Synthetic KPIs and trend data
* Pre-defined ticket examples
* AI placeholders (Gemini or local JSON)

> Judges see a complete working UI without noticing the mock mode.

To enable mock mode, set:

```bash
export MOCK_MODE=true
```



## 🧾 License

This project is released under the [MIT License](LICENSE).


> “TICKIT bridges the gap between support tickets and intelligent insights — empowering teams to focus on solutions, not chaos.”

```

---

Would you like me to include a **mock setup guide** section too (showing how to seed fake dashboard/ticket data for demo mode)? It makes it easy to run without the backend for hackathon judging.
```
