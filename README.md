# Transaction Audit Dashboard

A Django-based web application for auditing financial transactions, built with Django for backend logic, HTMX for dynamic frontend updates, Django REST Framework for API exposure, and Tailwind CSS for styling.

## Features

- **Dashboard Overview**

  - Interactive pie chart showing transaction status distribution
  - Bar chart displaying top merchants by volume
  - Detailed merchant summary table with transaction counts and averages

- **Transaction Management**

  - View transaction list with pagination (10 per page)
  - Dynamic filters: merchant search, status filter
  - One-click transaction approval for pending items
  - HTMX-powered instant updates without page reload

- **Reports & Analytics**

  - Daily transaction volume tracking with line chart
  - Success rate monitoring with target line (95%)
  - Total volume calculations

- **API Endpoint**
  - REST API at `/audit-dashboard/api/transactions/`
  - Authentication required access
  - Pagination support (20 items per page)

## Technical Decisions

### Database Design

- Indexed merchant and status fields for faster filtering and searching

### Data Seeding
- Custom management command for generating sample data
- Creates realistic transaction patterns
- Handles timezone-aware timestamps

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd transaction_audit_dashboard
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

On Windows:

```bash
venv\Scripts\activate
```

On macOS/Linux:

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a Superuser

```bash
python manage.py createsuperuser
```

### 7. Seed Sample Transactions

```bash
python manage.py seed_transactions
```

### 8. Run the Development Server

```bash
python manage.py runserver
```

Access the application at http://localhost:8000/audit-dashboard/

API endpoint: http://localhost:8000/audit-dashboard/api/transactions/
