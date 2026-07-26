# Lost and Found Portal 🔍

A full-stack web application designed for campus environments that enables students to report lost and found items with photographs, submit ownership claims, and connect with item finders through a secure, admin-verified approval workflow.

Built during my internship at **Voleergo Solutions LLP**, Infopark, Kakkanad, Ernakulam, as part of my MCA curriculum (May–July 2026).

## Features

- 📸 Report lost or found items with photographs
- 🔐 Secure JWT-based authentication
- ✅ Admin-verified approval workflow for claims
- 🔄 Fully decoupled frontend and backend — communicate via REST API only
- 📱 Responsive UI built with Tailwind CSS

## Tech Stack

**Backend**
- Python
- Django
- Django REST Framework (DRF)
- JWT Authentication
- SQLite (database)

**Frontend**
- Next.js
- Tailwind CSS
- Axios (for API calls)

## Architecture

The backend exposes secure, JWT-authenticated REST API endpoints that return JSON only — there are no server-rendered HTML templates. The frontend is a fully independent Next.js application that communicates with the backend exclusively through REST API calls using Axios.

## Project Structure
lost-found/
├── manage.py
├── db.sqlite3
├── accounts/          # User authentication app
├── claims/             # Ownership claims app
├── items/               # Lost & found items app
├── media/              # Uploaded item images
├── backend/            # Django project settings
└── frontend/            # Next.js application
## Getting Started

### Backend Setup (Django)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Setup (Next.js)
```bash
cd frontend
npm install
npm run dev
```

The frontend will run on `http://localhost:3000` and the backend on `http://localhost:8000`.

## How It Works

1. Users sign up/log in and receive a JWT token
2. Users can report a lost or found item with a photo and description
3. Other users can browse listings and submit ownership claims
4. Admins review and approve claims to connect finders with owners

## Author

Sreya R Kuttiyeri,
MCA Student

---
