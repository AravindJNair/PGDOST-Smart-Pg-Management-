# PGDOST — PG Management Platform

A full-stack web application for managing Paying Guest (PG) accommodations. Built as a final year project.

## 🏠 Overview

PGDOST connects **residents**, **PG owners**, and **administrators** through dedicated dashboards — handling everything from property discovery to rent payments and complaints.

## 🚀 Features

- **Residents** — Browse & filter PG listings, apply for rooms, track payments, raise complaints, log visitors
- **Owners** — List properties & rooms, approve bookings, generate invoices, manage complaints
- **Admin** — Manage all users, properties, and system-wide oversight

## 🛠️ Tech Stack

| Layer     | Technology                          |
|-----------|-------------------------------------|
| Backend   | Django 6 · Django REST Framework    |
| Auth      | JWT (SimpleJWT)                     |
| Frontend  | HTML5 · Vanilla CSS · JavaScript    |
| Database  | SQLite (dev) · PostgreSQL (prod)    |

## 📁 Project Structure

```
pgdost/
├── backend/                  # Django REST API
│   ├── accounts/             # User auth & profiles
│   ├── properties/           # Property & room management
│   ├── bookings/             # Booking & applications
│   ├── payments/             # Invoices & payments
│   ├── complaints/           # Complaint tracking
│   ├── visitors/             # Visitor log
│   └── pgdost_backend/       # Django project settings
└── frontend/                 # Static HTML/CSS/JS
    ├── pages/                # All HTML pages
    ├── css/                  # Stylesheets
    └── scripts/              # JavaScript files
```

## ⚙️ Local Setup

### Backend (Django)

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend

Open with **Live Server** (VS Code extension) at `localhost:5500` or any static file server.

### Environment Variables

Create a `.env` file in `backend/` for production:

```
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False
```

## 🔑 Default Roles

| Role       | Login Page              |
|------------|-------------------------|
| Resident   | `/pages/login.html`     |
| Owner      | `/pages/owner-login.html` |
| Admin      | `/pages/admin-dashboard.html` |

## 📸 Screenshots

*Landing page with smart search, property cards, and role-based dashboards.*

---

**Made with ❤️ by AravindJNair**
