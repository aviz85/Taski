# Taski - Task Management System

## Overview

Taski is a comprehensive task management system built with Django and Django REST Framework. This document provides information about the Taski backend system, its features, and how to use the API.

## Features

- User authentication and registration using JWT
- Create, read, update, and delete tasks
- Assign tasks to users
- Filter and search tasks
- Sort tasks by various criteria
- Token-based authentication with refresh capability

## Documentation

- [API Documentation (English)](api_documentation.md)
- [API Documentation (Hebrew)](api_documentation_he.md)
- [Technical Specifications](specs.md)

## Backend Technology Stack

- Django 5.1+
- Django REST Framework
- djangorestframework-simplejwt for JWT authentication
- django-cors-headers for CORS support
- SQLite for development database

## API Endpoints Summary

### Authentication

- `POST /api/auth/register/` - Register a new user
- `POST /api/auth/login/` - Login and get tokens
- `POST /api/auth/refresh/` - Refresh access token

### Task Management

- `GET /api/tasks/` - List all tasks
- `POST /api/tasks/` - Create a new task
- `GET /api/tasks/{id}/` - Retrieve a specific task
- `PUT /api/tasks/{id}/` - Update a task (complete update)
- `PATCH /api/tasks/{id}/` - Update a task (partial update)
- `DELETE /api/tasks/{id}/` - Delete a task

## Getting Started

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)

### Installation

1. Clone the repository
2. Create and activate a virtual environment
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Apply migrations:
   ```bash
   python manage.py migrate
   ```
5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Testing

Run the automated tests with:

```bash
python manage.py test
```

## Future Enhancements

- Email notifications for task assignments and due dates
- Task categories/labels
- Task attachments
- User roles and permissions
- Frontend integration 