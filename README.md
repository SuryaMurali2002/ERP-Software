# Cable TV ERP System
**CMPT 354 Final Project | Surya Murali**

A full-stack business management system for a cable TV company. It covers customers, packages and subscriptions, billing, inventory, support tickets, reporting and role-based access control. It also includes a RAG-based AI assistant that answers questions about the company's data. Built with Flask, MySQL, ChromaDB and OpenAI.

## Demo Videos

- **Implementation walkthrough:** https://youtu.be/fE4QIfQb6jc
- **Presentation:** https://youtu.be/LxETC_P5YFQ

Database normalization write-up: [Database Normalization.pdf](Database%20Normalization.pdf)

---

## Features

| Module | What it does |
|---|---|
| **Customers** | Create, view, edit customers and track account status |
| **Employees & Permissions** | Manage staff; role-based access (Admin vs. Employee with granular permissions) |
| **Packages & Subscriptions** | Define channel packages and subscribe customers to them |
| **Billing** | Invoices with line items, payments, and payment allocations across invoices |
| **Inventory** | Items, devices, device assignments to customers, stock transactions |
| **Support Tickets** | Open, assign and resolve customer tickets |
| **Reports** | 10 SQL reports showcasing a range of query techniques |
| **ERP Assistant** | Chatbot that answers questions over live ERP data using RAG |
| **Integrity Checks** | 12 SQL assertions that verify data consistency (web UI + CLI) |

**Role-based access:** Admins have full access. Employees are limited to their assigned permission: `HANDLE_TICKETS`, `MANAGE_INVENTORY`, `VIEW_REPORTS` or `MANAGE_CUSTOMERS`.

---

## Database Design

18 tables, created and seeded by `init_db.py`:

| Domain | Tables |
|---|---|
| Users & access | `User`, `Admin`, `Employee`, `Permission`, `RoleHasPermission` |
| Customers & services | `Customer`, `Package`, `Subscription`, `Ticket` |
| Billing | `Invoice`, `InvoiceLineItem`, `Payment`, `PaymentAllocation` |
| Inventory | `Item`, `Device`, `DeviceAssignment`, `InventoryTransaction`, `TransactionLine` |

`Admin` and `Employee` specialize `User` (ISA hierarchy). Customers are decoupled from system users. Payments are split across invoices via `PaymentAllocation`. Three database triggers enforce business rules: `prevent_duplicate_active_subscription`, `auto_mark_invoice_paid` and `prevent_negative_stock`. See the [normalization report](Database%20Normalization.pdf) for the functional-dependency analysis.

---

## SQL Queries Showcased (Reports page)

| Report | Technique |
|---|---|
| Active Customer Subscriptions by Monthly Price | Selection, projection, multi-table join, ORDER BY |
| Monthly Revenue Summary | Aggregation (`GROUP BY`) |
| Customers with Outstanding Balances | Nested subquery |
| Employees Who Have Not Handled Any Ticket | `NOT EXISTS` |
| Customers Subscribed to Every Available Package | **Division** via double `NOT EXISTS` |
| Invoice Payment Completion Status | `LEFT JOIN` with aggregation (balance remaining) |
| Current Device Assignment Status | Four-table join |
| Inventory Stock Level per Item | Conditional aggregation (inbound vs. outbound) |
| Ticket Resolution Rate by Employee | Aggregation with `CASE` |
| Admin Permission Summary | Joins and aggregation |

The overdue-accounts report also includes a **Reactivate Eligible Accounts** action.

---

## AI Assistant (RAG)

The ERP Assistant answers natural-language questions about the data.

```
MySQL records → exporter → text chunks → embedder (ChromaDB) → retriever → generator (OpenAI) → answer
```

- **Incremental sync:** create/update operations update the vector index automatically (`rag/sync.py`).
- **Persistent chat history** per user.
- **Evaluation suite** in `cable_tv_erp/eval/` with ground-truth questions and keyword scoring. Run from `cable_tv_erp/`:
  ```python
  from eval.eval_runner import run_eval
  run_eval(top_k=5, dry_run=True)   # retrieval only, no OpenAI call
  ```

---

## Prerequisites

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.12 | Anaconda recommended |
| MySQL | 8.0+ | XAMPP works fine |
| OpenAI API Key | — | Required for the AI chatbot only |

## Setup

### 1. Create a Python environment

Install Anaconda from https://www.anaconda.com/download, then:

```bash
conda create -n erp python=3.12 -y
conda activate erp
```

### 2. Install dependencies

```bash
cd ERP-Software/cable_tv_erp
pip install -r requirements.txt
```

### 3. Configure environment variables

Copy the template, then edit it:

```bash
cp .env.example .env        # Windows: copy .env.example .env
```

```
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=cable_tv_erp
SECRET_KEY=cable-tv-erp-secret-key-cmpt354
OPENAI_API_KEY=your-openai-api-key-here
```

> If your MySQL root user has no password, leave `DB_PASSWORD=` blank. The OpenAI key is only needed for the chatbot.
### 4. Start MySQL

- **XAMPP:** open the Control Panel and click **Start** next to MySQL.
- **Standalone:** start the MySQL service.

### 5. Initialize the database

From the project root (`ERP-Software/`):

```bash
python init_db.py
```

Creates the `cable_tv_erp` database, all 18 tables, the triggers, and the seed data. Safe to re-run: it drops and recreates all tables.

### 6. Build the RAG index (for the chatbot)

```bash
cd cable_tv_erp/scripts
python build_index.py
```

Takes about 30 seconds. Re-run if the database is reseeded directly via SQL.

### 7. Run the application

```bash
cd cable_tv_erp
python app.py
```

Open http://localhost:5000

---

## Login Credentials

### Admins
| Username | Password |
|---|---|
| admin_sara | admin_sara_pass |
| admin_james | admin_james_pass |
| admin_peter | admin_peter_pass |
| admin_lisa | admin_lisa_pass |
| admin_kevin | admin_kevin_pass |

### Employees
| Username | Password | Permission |
|---|---|---|
| emp_mike | emp_mike_pass | HANDLE_TICKETS |
| emp_linda | emp_linda_pass | MANAGE_INVENTORY |
| emp_carlos | emp_carlos_pass | HANDLE_TICKETS |
| emp_nina | emp_nina_pass | VIEW_REPORTS |
| emp_david | emp_david_pass | MANAGE_CUSTOMERS |

---

## Data Integrity Checks

```bash
python scripts/run_assertions.py              # run all 12 checks
python scripts/run_assertions.py --verbose    # show offending rows
python scripts/run_assertions.py --fix        # remediation guidance for LOW severity issues
```

Exit codes: `0` all pass, `1` HIGH failure, `2` MEDIUM failure only. The same checks are available in the web UI under **Admin → Integrity Checks**.

---

## Project Structure

```
ERP-Software/
├── init_db.py                  # Database creation and seed script
├── Database Normalization.pdf  # Normalization write-up
├── scripts/
│   └── run_assertions.py       # CLI data integrity checker
└── cable_tv_erp/
    ├── app.py                  # Flask entry point
    ├── db.py                   # Database connection helper
    ├── config.py               # Environment variable loader
    ├── .env.example            # Environment template
    ├── requirements.txt
    ├── routes/                 # Flask blueprints (one per module)
    ├── rag/                    # exporter, embedder, retriever, generator, sync
    ├── eval/                   # RAG evaluation suite and results
    ├── scripts/build_index.py  # RAG index builder
    ├── templates/              # Jinja2 templates
    └── static/                 # CSS and JavaScript
```

---

## Troubleshooting

**`ModuleNotFoundError` on startup**: activate the environment: `conda activate erp`.

**`Can't connect to MySQL`**: MySQL isn't running. Start it before `init_db.py` or `app.py`.

**Chatbot gives wrong or outdated answers**: rebuild the index with `python build_index.py` in `cable_tv_erp/scripts`.

**`chromadb` import error on Python 3.14**: ChromaDB doesn't support 3.14. Use Python 3.12.

**Port 5000 in use**: change the port in `cable_tv_erp/app.py` (`app.run(..., port=5001)`) and visit `http://localhost:5001`.
