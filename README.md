# SpendWise
> *"Because money shouldn't just vanish"*

A simple, responsive web application built with **Python**, **Django**, and **MySQL** to record, manage, and analyze personal expenses in Indian Rupees (**₹**).

Developed based on the [Product Requirements Document (PRD)](./PRD.md).

---

## 🚀 Key Features

* **Authentication & Privacy**: Single-user private access protected by Django authentication with no public user registration.
* **Dashboard Summary**:
  * **Today's Expenses**: Total expenses recorded today.
  * **This Week**: Total spent during current calendar week (Monday to Sunday).
  * **This Month**: Total spent during the current calendar month.
  * **Total Transactions**: Total number of recorded entries.
* **Visual Analytics (Chart.js)**:
  * **Weekly Spending Bar Chart**: Monday through Sunday daily breakdown with exact amounts on hover.
  * **Monthly Category Doughnut Chart**: Breakdown of spending by category for the current month.
  * **Monthly Trend Line Chart**: Daily cumulative spending throughout the month.
  * **Monthly Summary Metrics**: Total spending, daily average spending (calculated over elapsed days including today), and highest-spending category.
* **Expense Management**:
  * **Add Expense**: Server and client validated form with ₹ input prefix.
  * **Edit Expense**: Modify details with instant feedback.
  * **Delete Expense**: Deletion confirmation screen with item details.
* **Expense Table**:
  * Filter by category and custom date ranges.
  * Search expenses by description note.
  * Sort by date (newest/oldest) or amount (highest/lowest).
  * Pagination with parameter persistence.
  * Mobile-friendly responsive design (desktop table and mobile transaction cards).
* **Predefined Categories**:
  1. Food
  2. Fuel
  3. Travel
  4. Shopping
  5. Bills
  6. Entertainment
  7. Gym
  8. Hospital
* **Indian Rupee Formatting**: Consistent Indian numbering system across all views and charts (e.g., `₹180`, `₹1,200`, `₹25,000`, `₹1,25,000`).

---

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| **Backend** | Python 3.10+ / Django 5+ / Django 6 |
| **Database** | MySQL (with PyMySQL driver) / SQLite (development fallback) |
| **Frontend** | HTML5, CSS3 (responsive grid & flexbox, custom CSS) |
| **Interactivity** | Vanilla JavaScript |
| **Charts** | Chart.js 4 (bundled locally in `static/vendor/`) |

---

## 📦 Getting Started

### 1. Clone & Set Up Virtual Environment

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment (`.env`)

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

* **To run with local SQLite** (quick start):
  Keep `DB_ENGINE=sqlite3` and `USE_MYSQL=False`.
* **To run with MySQL** (as specified in PRD):
  Set `DB_ENGINE=mysql`, `USE_MYSQL=True`, and supply your MySQL `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`.

### 3. Run Migrations & Initialize App

```bash
# Run database migrations (creates tables & seeds 8 predefined categories)
python manage.py migrate

# Initialize admin account and optionally sample data
python manage.py init_app --sample-data
```

> **Default Credentials:**
> * **Username:** `admin`
> * **Password:** `admin123`

You can change them by setting `ADMIN_USER` and `ADMIN_PASS` in your `.env` or running `python manage.py createsuperuser`.

### 4. Start Development Server

```bash
python manage.py runserver 0.0.0.0:8000
```

Open your browser and navigate to:
**`http://localhost:8000/`**

---

## 🐳 Running with Docker & MySQL

To run both MySQL 8 and the Django web application in isolated containers:

```bash
docker compose up --build
```

The database will be automatically provisioned, migrated, and seeded with categories.

---

## 🧪 Running the Automated Test Suite

A comprehensive test suite covering currency formatting, model validations, authentication, CRUD operations, filtering, and analytics calculations is included:

```bash
python manage.py test
```

---

## 📂 Project Structure

```
├── config/                      # Django project configuration
│   ├── __init__.py              # PyMySQL driver registration
│   ├── settings.py              # Environment-driven settings & DB config
│   ├── urls.py                  # Root URL declarations
│   └── wsgi.py
├── expenses/                    # Core expense management application
│   ├── management/commands/     # init_app command to seed data & users
│   ├── migrations/              # Database migrations (including categories seed)
│   ├── templatetags/            # Indian Rupee (inr) custom template filters
│   ├── forms.py                 # Expense form with validations
│   ├── models.py                # Category and Expense models
│   ├── tests.py                 # 15 automated test cases
│   ├── urls.py                  # URLs for dashboard, expenses, auth
│   ├── utils.py                 # format_inr utility function
│   └── views.py                 # Views for dashboard analytics & CRUD
├── static/
│   ├── css/
│   │   └── style.css            # Responsive modern styles
│   └── vendor/
│       └── chart.umd.min.js     # Bundled Chart.js
├── templates/
│   ├── base.html                # Base layout with nav & Rupee JS helper
│   └── expenses/
│       ├── dashboard.html       # Dashboard with summary & charts
│       ├── expense_confirm_delete.html # Deletion confirmation
│       ├── expense_form.html    # Add/Edit form
│       ├── expense_list.html    # Table with filters, search, pagination
│       └── login.html           # Authentication login
├── .env.example                 # Example environment variables
├── Dockerfile                   # Production Docker image build
├── docker-compose.yml           # MySQL + Django orchestration
├── requirements.txt             # Pinned Python dependencies
└── README.md
```
