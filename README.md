# Add Persistent Storage to a Flask Web Service Using PostgreSQL and SQLAlchemy

A Flask REST API that saves student records in PostgreSQL and retrieves them using SQLAlchemy. Records remain available after the application stops and restarts.

## Overview

Student information is submitted as JSON through a POST request and stored in the `users` table. A GET endpoint retrieves a record by its student ID. No initial student data is hardcoded in the application.

The service includes duplicate-ID detection, a unique email constraint, basic request validation, and UTC response timestamps. Postman and pgAdmin 4 were used to verify creation, database storage, retrieval, persistence after restarting Flask, and duplicate rejection.

## Technology

- Python and Flask for the HTTP API
- Flask-SQLAlchemy for database models and sessions
- PostgreSQL for persistent storage
- Psycopg 3 as the PostgreSQL driver
- Postman and pgAdmin 4 for manual verification

## Project structure

```text
.
├── app.py             # API routes, validation, and transaction handling
├── config.py          # Database connection from DATABASE_URL
├── models.py          # User model and JSON serialization
├── requirements.txt   # Python dependencies
└── docs/images/       # API and database verification screenshots
```

## Database schema

Database: `user_db` · Table: `users`

| Column | Type | Constraints |
| --- | --- | --- |
| `student_id` | `VARCHAR(20)` | Primary key |
| `name` | `VARCHAR(100)` | Not null |
| `birthday` | `DATE` | Not null |
| `email` | `VARCHAR(120)` | Unique, not null |
| `age` | `INTEGER` | Not null |

The primary key prevents duplicate student IDs. SQLAlchemy commits successful inserts to PostgreSQL and rolls back transactions when an integrity constraint fails.

## Run locally

Install Python 3.10 or later and a running PostgreSQL server. The commands below use PowerShell.

### 1. Install dependencies

```powershell
git clone https://github.com/ishtiakrongon/persistent-storage-flask-postgresql-sqlalchemy.git
cd persistent-storage-flask-postgresql-sqlalchemy
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Create the database

In pgAdmin or `psql`, connect to an existing database with a role permitted to create databases and run:

```sql
CREATE DATABASE user_db;
```

### 3. Configure the connection

Set the connection string in the terminal where you will run Flask. Replace the placeholder with your local PostgreSQL password; URL-encode any reserved characters in the username or password.

```powershell
$env:DATABASE_URL = "postgresql+psycopg://postgres:YOUR_PASSWORD@localhost:5432/user_db"
```

`config.py` reads this environment variable directly. There is no default database connection and no automatic `.env` loading. Keep real credentials out of source control.

### 4. Initialize the table

With `DATABASE_URL` set, create the tables declared by the models:

```powershell
.\.venv\Scripts\python.exe -c "from app import app; from models import db; ctx = app.app_context(); ctx.push(); db.create_all(); ctx.pop()"
```

Run this before the first request. It creates missing tables without inserting sample records. It does not migrate existing table schemas.

### 5. Start Flask

```powershell
.\.venv\Scripts\python.exe app.py
```

The service runs at `http://127.0.0.1:5000`. Use the `/info` endpoints below; the root URL has no route. The included entry point enables Flask's debugger for local development.

## API reference

| Method | Endpoint | Purpose | Success |
| --- | --- | --- | --- |
| `POST` | `/info` | Create a student record | `201 Created` |
| `GET` | `/info/<student_id>` | Retrieve a student record | `200 OK` |

### Create a record

Send `Content-Type: application/json` with all five required fields:

```json
{
  "student_id": "101",
  "name": "Ishtiak Ahmed",
  "birthday": "1997-01-08",
  "email": "ishtiak.jp@gmail.com",
  "age": 29
}
```

Example PowerShell request:

```powershell
$body = @{
    student_id = "101"
    name = "Ishtiak Ahmed"
    birthday = "1997-01-08"
    email = "ishtiak.jp@gmail.com"
    age = 29
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:5000/info" -ContentType "application/json" -Body $body
```

Example `201 Created` response:

```json
{
  "message": "User created successfully",
  "student_id": "101",
  "name": "Ishtiak Ahmed",
  "birthday": "1997-01-08",
  "email": "ishtiak.jp@gmail.com",
  "age": 29,
  "timestamp": "2026-11-07T16:35:35.859561+00:00"
}
```

### Retrieve a record

```powershell
Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:5000/info/101"
```

The `200 OK` response contains the five saved fields and a UTC `timestamp`. Timestamps are generated for each response; they are not stored creation or update times.

### Error responses

| Status | Condition | JSON `error` value |
| --- | --- | --- |
| `400` | Body is not a JSON object | `Invalid JSON body` |
| `400` | A required field is absent | `Missing required fields` |
| `400` | Birthday cannot be parsed or age fails conversion/validation | `Invalid birthday or age` |
| `404` | Requested student does not exist | `not found` |
| `409` | Student ID already exists | `Student ID already exists` |
| `409` | Database integrity constraint fails during insertion | `Student ID or email already exists` |

Birthday examples use `YYYY-MM-DD`; age should be a non-negative integer. Validation is basic: the application does not comprehensively validate field types, lengths, email format, or consistency between birthday and age. The generic integrity-error response can also represent constraints other than uniqueness.

## Verification walkthrough

The screenshots below document a local run using Postman, pgAdmin 4, and Flask. They retain the original demonstration data.

### 1. Create a new student using POST

Submit the five fields to `POST /info`. The response returns `201 Created`, the saved values, a success message, and a timestamp.

![Postman POST request creating a student with status 201](docs/images/1_POST_create_new_student.png)

### 2. Verify the stored record in PostgreSQL

Open pgAdmin's Query Tool for `user_db` and execute:

```sql
SELECT * FROM users;
```

The returned row independently confirms that the API stored the submitted data in PostgreSQL.

![pgAdmin query showing the stored student record](docs/images/1_2_pg_show_student_data.png)

### 3. Retrieve the existing student using GET

Request `GET /info/101`. A `200 OK` response returns the stored student information and a new response timestamp.

![Postman GET request returning the saved record](docs/images/2_GET_existing_student.png)

### 4. Verify persistence after restarting Flask

Stop Flask with `Ctrl+C`, start it again with the same `DATABASE_URL`, and request `/info/101` without sending another POST request. The record is still available because it resides in PostgreSQL.

![Existing student retrieved successfully after Flask restarts](docs/images/2_1_showing_existing_student_restarting_Flask.png)

### 5. Reject a duplicate student ID

Send another POST request with different student details but reuse ID `101`. The API returns `409 Conflict`:

```json
{
  "error": "Student ID already exists"
}
```

![Duplicate student ID request rejected with status 409](docs/images/3_POST_duplicate_student_id_info.png)

## Scope

This project demonstrates persistent creation and retrieval of records. It has no update/delete endpoints, authentication, authorization, or database migration tooling. Use synthetic data when running your own demo. Production deployment would require additional validation, access controls, and a production WSGI server with debug mode disabled.
