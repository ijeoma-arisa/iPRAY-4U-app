# iPRAY 4U

**Prayer requests, organized.**

🌐 **Try iPRAY 4U:** [ipray4u.app](https://ipray4u.app)

## About
*"Can you pray for me?"*

**iPRAY 4U** helps you keep track of the prayer requests shared by the people in your life. Instead of keeping requests scattered across your Notes app, text messages, or memory, iPRAY 4U keeps every request for the people you care about in one place.

Organize prayer requests by person, group people by relationship, and stay intentional about praying for family, friends, and more. iPRAY 4U was built to make it easier to faithfully remember and follow through on the prayer requests entrusted to you.

## Features
- Organize prayer requests by person and relationship
- Manage people and their prayer requests
- Track which prayer requests you've already prayed for
- Access your prayer requests from your own secure account

## Screenshots

<p align="center">
  <img src="images/homepage-1.png" alt="Homepage" width="85%">
</p>

<p align="center">
  <img src="images/dashboard.png" alt="Prayer Requests Dashboard" width="85%">
</p>

## Tech Stack

**Frontend:** HTML, CSS, JavaScript

**Backend:** Python, Flask

**Database:** PostgreSQL

**Authentication:** Supabase Auth

**Deployment:** Render

**Testing & CI/CD:** pytest, GitHub Actions

## Prerequisites
* Python 3.12
* Recommended: virtual environment

## Installation

### Clone the repository

```bash
git clone <repository-url>

cd <project-folder>
```

### Create and activate virtual environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

macOS/Linux:

```bash
source venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

## Environment Variables
Create a `.env` file in the project root and configure the following variables:

```env
DATABASE_URL=
SECRET_KEY=
SUPABASE_URL=
SUPABASE_PUBLISHABLE_KEY=
```

## Run Locally
Start the Flask development server:

```bash
flask run
```

If Flask does not detect the app automatically, run:

```bash
flask --app wsgi run
```

The production deployment uses:

```bash
gunicorn wsgi:app
```

## Testing
Run the test suite:

```bash
pytest tests
```