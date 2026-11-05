# Pacewisdom Job Portal — CRUD via ModelForms

A simple Django job portal with job listings and a ModelForm-based application flow. HR users can review, update and delete submitted applications.

## Features

- Display available job openings.
- Submit an application with a resume upload.
- Validate application data through a Django `ModelForm`.
- Validate phone numbers and resume file type/size.
- HR-only application list and detail pages.
- HR-only update and delete operations.
- Store PostgreSQL credentials and Django settings in a local `.env` file.

## Requirements

- Python 3.10 or newer
- PostgreSQL

## Setup on Windows (Git Bash)

1. Create and activate a virtual environment:

   ```bash
   python -m venv env
   source env/Scripts/activate
   ```

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Create your local environment file:

   ```bash
   cp .env.example .env
   ```

   Open `.env` and set `DJANGO_SECRET_KEY` to a long random value and `DB_PASSWORD` to your PostgreSQL password. Do not commit `.env` to Git.

   To generate a secret key, run:

   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(50))"
   ```

4. Create the PostgreSQL database named `jobapplication_db` (or update `DB_NAME` in `.env`). Ensure the PostgreSQL server is running.

5. Apply migrations:

   ```bash
   python manage.py migrate
   ```

6. Create an HR/admin account:

   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:

   ```bash
   python manage.py runserver
   ```

## URLs

- Job portal: `http://127.0.0.1:8000/careers/`
- Job listings: `http://127.0.0.1:8000/careers/jobs`
- Django admin: `http://127.0.0.1:8000/admin/`
- HR application list: `http://127.0.0.1:8000/careers/applications`

Create job records in Django admin. The HR application pages require a logged-in staff user; sign in through the Django admin first.

## Application form rules

- Name, email, phone and resume are captured using `ApplicationForm`.
- Phone numbers may contain digits and common phone-number separators.
- Resume formats accepted: PDF, DOC and DOCX.
- Maximum resume size: 5 MB.
- The existing model constraint allows each email address to be used only once across all applications.

## CRUD flow

- **Create:** A job applicant submits a `ModelForm`. The view validates the bound form, calls `save(commit=False)`, assigns the selected job, and saves the application.
- **Read:** HR can view the applications list and an individual application's details, including its resume link.
- **Update:** HR edits an existing application using a ModelForm bound to the existing model instance. The existing resume is retained unless a replacement is uploaded.
- **Delete:** HR confirms deletion using a POST request. The application record and its stored resume are deleted.

## Environment variables

`settings.py` loads values from the project-root `.env` file. Database name, username, password, host and port are not hard-coded in the settings module. `.env.example` is a template; the real `.env` file is ignored by Git.

For deployment, set `DJANGO_DEBUG=False` and configure `DJANGO_ALLOWED_HOSTS` with your real host names.
