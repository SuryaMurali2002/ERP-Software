# Cable TV ERP System
**CMPT 354 | Surya Murali**

A full-stack business management system for a cable TV company. Built with Flask, MySQL, and a RAG-based AI assistant powered by ChromaDB and OpenAI.

---

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.12 | Use Anaconda (recommended) |
| MySQL | 8.0+ | XAMPP works fine |
| OpenAI API Key | — | Required for the AI chatbot only |

---

## 1. Install Python (Anaconda — Recommended)

Download and install Anaconda from https://www.anaconda.com/download

Then create a dedicated environment:

```bash
conda create -n erp python=3.12 -y
conda activate erp
```

> Activate this environment every time before running the project.

---

## 2. Install Dependencies

```bash
cd ERP-Software/cable_tv_erp
pip install -r requirements.txt
```

---

## 3. Configure Environment Variables

Open `cable_tv_erp/.env` and set your database credentials and OpenAI key:

```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=cable_tv_erp
SECRET_KEY=cable-tv-erp-secret-key-cmpt354
OPENAI_API_KEY=your-openai-api-key-here
```

> If your MySQL root user has no password, leave `DB_PASSWORD=` blank.
> The OpenAI key is only required for the ERP Assistant chatbot feature.

---

## 4. Start MySQL

Make sure MySQL is running before the next steps.

- **XAMPP:** Open the XAMPP Control Panel and click **Start** next to MySQL.
- **Standalone MySQL:** Start the MySQL service from your system services.

---

## 5. Initialize the Database

From the project root (`ERP-Software/`):

```bash
python init_db.py
```

This will:
- Create the `cable_tv_erp` database
- Create all 18 tables
- Insert all seed data (users, customers, packages, subscriptions, invoices, payments, devices, tickets)

> Safe to re-run — it drops and recreates all tables each time.

---

## 6. Build the RAG Index (for AI Chatbot)

```bash
cd cable_tv_erp/scripts
python build_index.py
```

This exports all database records into a ChromaDB vector index used by the ERP Assistant. Takes approximately 30 seconds on first run.

> Only needs to be run once after seeding. Re-run if the database is reseeded directly via SQL.

---

## 7. Run the Application

```bash
cd cable_tv_erp
python app.py
```

Open your browser and navigate to:

```
http://localhost:5000
```

---

## 8. Login Credentials

### Admin Accounts
| Username | Password |
|---|---|
| admin_sara | admin_sara_pass |
| admin_james | admin_james_pass |
| admin_peter | admin_peter_pass |
| admin_lisa | admin_lisa_pass |
| admin_kevin | admin_kevin_pass |

### Employee Accounts
| Username | Password | Permissions |
|---|---|---|
| emp_mike | emp_mike_pass | HANDLE_TICKETS |
| emp_linda | emp_linda_pass | MANAGE_INVENTORY |
| emp_carlos | emp_carlos_pass | HANDLE_TICKETS |
| emp_nina | emp_nina_pass | VIEW_REPORTS |
| emp_david | emp_david_pass | MANAGE_CUSTOMERS |

> Admins have full access to all modules. Employee access is restricted to their assigned permissions.

---

## 9. Optional — Run Data Integrity Checks (CLI)

```bash
cd ERP-Software
python scripts/run_assertions.py
```

Flags:
```bash
python scripts/run_assertions.py --verbose    # shows offending rows for failures
python scripts/run_assertions.py --fix        # prints remediation guidance for LOW severity issues
```

Exit codes: `0` = all pass, `1` = HIGH failure, `2` = MEDIUM failure only.

The same checks are available in the web UI under **Admin → Integrity Checks**.

---

## Project Structure

```
ERP-Software/
├── init_db.py                  # Database creation and seed script
├── scripts/
│   └── run_assertions.py       # CLI data integrity checker
└── cable_tv_erp/
    ├── app.py                  # Flask application entry point
    ├── db.py                   # Database connection helper
    ├── config.py               # Environment variable loader
    ├── .env                    # Environment variables (configure this)
    ├── requirements.txt        # Python dependencies
    ├── routes/                 # Flask blueprints (one per module)
    │   ├── auth.py
    │   ├── dashboard.py
    │   ├── customers.py
    │   ├── employees.py
    │   ├── packages.py
    │   ├── subscriptions.py
    │   ├── billing.py
    │   ├── inventory.py
    │   ├── tickets.py
    │   ├── permissions.py
    │   ├── reports.py
    │   ├── chatbot.py
    │   ├── admin_integrity.py
    │   └── decorators.py
    ├── rag/                    # RAG pipeline for AI chatbot
    │   ├── exporter.py         # Exports DB records to text chunks
    │   ├── embedder.py         # ChromaDB vector index builder
    │   ├── retriever.py        # Semantic search
    │   ├── generator.py        # OpenAI response generation
    │   └── sync.py             # Incremental index sync hooks
    ├── scripts/
    │   └── build_index.py      # RAG index builder script
    ├── templates/              # Jinja2 HTML templates
    └── static/                 # CSS and JavaScript
```

---

## Troubleshooting

**`ModuleNotFoundError` on startup**
Make sure the `erp` conda environment is activated: `conda activate erp`

**`Can't connect to MySQL` error**
MySQL is not running. Start it via XAMPP or your system services before running `init_db.py` or `app.py`.

**Chatbot returns wrong or outdated answers**
The vector index is stale. Rebuild it:
```bash
cd cable_tv_erp/scripts
python build_index.py
```

**`chromadb` import error on Python 3.14**
Python 3.14 is not supported by ChromaDB. Use Python 3.12 via Anaconda as described in Step 1.

**Port 5000 already in use**
Change the port in `cable_tv_erp/app.py` line 87:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```
Then access the app at `http://localhost:5001`.
