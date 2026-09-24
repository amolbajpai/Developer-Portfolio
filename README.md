# Developer Portfolio

Portfolio site for **Software Developer**. Resume content lives in SQLite and can be edited in Django Admin.
A session-aware Gemini chatbot answers questions from the stored resume and the current browser conversation.

## Requirements

- Python 3.10.5 or newer

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ for the site and http://127.0.0.1:8000/admin/ for content management.

## Chatbot and email (Admin)

Open **http://127.0.0.1:8000/admin/** → **PORTFOLIO** → **API and email configuration**.

Fill in:

- **Gemini API key** and **Gemini model name** (default `gemini-2.0-flash`)
- **Email ID**, **Email password** (Gmail app password), SMTP host/port/TLS
- **Contact inbox** — where form messages are delivered (optional; otherwise the profile email)

The contact form saves the message in SQLite and then sends it by SMTP.

The chat widget keeps a `session_key` in `sessionStorage`. Follow-up questions reuse the last 20 messages from SQLite. **New conversation** starts a fresh session.

## Excel backup

```bash
python manage.py export_portfolio --output portfolio_export.xlsx
python manage.py import_portfolio portfolio_export.xlsx
```
