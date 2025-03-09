# API Documentation - Taski

## Overview

This document provides a comprehensive guide to the Taski API, a RESTful interface for managing tasks. The API allows users to register, login, and perform CRUD operations on tasks.

## Base URL

All API endpoints are relative to the base URL:

```
http://localhost:8000/api/
```

## Authentication

The API uses JWT (JSON Web Token) authentication. Most endpoints require authentication.

### Authentication Flow

1. Register a new user or login with existing credentials
2. Receive an access token and refresh token
3. Include the access token in the Authorization header for subsequent requests
4. When the access token expires, use the refresh token to get a new access token

### Authentication Headers

For authenticated endpoints, include the following header:

```
Authorization: Bearer <access_token>
```

## Endpoints

### Authentication

#### Register a New User

```
POST /api/auth/register/
```

##### Request Body

```json
{
  "username": "example_user",
  "email": "user@example.com",
  "password": "secure_password123"
}
```

##### Response (201 Created)

```json
{
  "user": {
    "id": 1,
    "username": "example_user",
    "email": "user@example.com"
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
  }
}
```

##### Possible Errors

- `400 Bad Request`: Missing required fields
- `400 Bad Request`: Username already exists
- `400 Bad Request`: Email already exists

#### Login

```
POST /api/auth/login/
```

##### Request Body

```json
{
  "username": "example_user",
  "password": "secure_password123"
}
```

##### Response (200 OK)

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
}
```

##### Possible Errors

- `401 Unauthorized`: Invalid credentials

#### Refresh Token

```
POST /api/auth/refresh/
```

##### Request Body

```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
}
```

##### Response (200 OK)

```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
}
```

##### Possible Errors

- `401 Unauthorized`: Invalid or expired refresh token

#### Get Current User

```
GET /api/auth/user/
```

##### Response (200 OK)

```json
{
  "id": 1,
  "username": "example_user",
  "email": "user@example.com"
}
```

##### Possible Errors

- `401 Unauthorized`: Missing or invalid authentication token

### Tasks

#### List All Tasks

Returns tasks where the authenticated user is either the owner or assigned to the task.

```
GET /api/tasks/
```

##### Query Parameters

| Parameter | Type   | Description                                       |
|-----------|--------|---------------------------------------------------|
| status    | string | Filter by status (TODO, IN_PROGRESS, DONE)        |
| priority  | string | Filter by priority (LOW, MEDIUM, HIGH)            |
| search    | string | Search for tasks matching the query in title/description |
| ordering  | string | Order results (created_at, -created_at, due_date, etc.) |
| tag       | string | Filter by tag (returns tasks that contain this tag) |

##### Response (200 OK)

```json
[
  {
    "id": 1,
    "title": "Complete project documentation",
    "description": "Write comprehensive documentation for the project",
    "created_at": "2025-03-09T14:00:00Z",
    "due_date": "2025-03-15T23:59:59Z",
    "status": "TODO",
    "priority": "HIGH",
    "owner": 1,
    "assigned_to": 1,
    "tags": "documentation,urgent,project",
    "duration": 4.5,
    "owner_details": {
      "id": 1,
      "username": "example_user",
      "email": "user@example.com"
    },
    "assigned_to_details": {
      "id": 1,
      "username": "example_user",
      "email": "user@example.com"
    }
  },
  ...
]
```

##### Possible Errors

- `401 Unauthorized`: Missing or invalid authentication token

#### Create a New Task

```
POST /api/tasks/
```

##### Request Body

```json
{
  "title": "Implement new feature",
  "description": "Implement the login functionality",
  "due_date": "2025-03-20T18:00:00Z",
  "status": "TODO",
  "priority": "MEDIUM",
  "assigned_to": 2,
  "owner": 1,
  "tags": "feature,frontend,development",
  "duration": 8.0
}
```

You can also use `tags_list` instead of `tags` to provide tags as an array:

```json
{
  "title": "Task with tags",
  "description": "Using tags list format",
  "due_date": "2025-03-20T18:00:00Z",
  "status": "TODO",
  "priority": "MEDIUM",
  "assigned_to": 2,
  "owner": 1,
  "tags_list": ["feature", "frontend", "development"],
  "duration": 8.0
}
```

##### Response (201 Created)

```json
{
  "id": 2,
  "title": "Implement new feature",
  "description": "Implement the login functionality",
  "created_at": "2025-03-09T15:30:00Z",
  "due_date": "2025-03-20T18:00:00Z",
  "status": "TODO",
  "priority": "MEDIUM",
  "owner": 1,
  "assigned_to": 2,
  "tags": "feature,frontend,development",
  "duration": 8.0,
  "owner_details": {
    "id": 1,
    "username": "example_user",
    "email": "user@example.com"
  },
  "assigned_to_details": {
    "id": 2,
    "username": "another_user",
    "email": "another@example.com"
  }
}
```

##### Possible Errors

- `400 Bad Request`: Missing required fields
- `400 Bad Request`: Invalid data (e.g., invalid status or priority value)
- `401 Unauthorized`: Missing or invalid authentication token

#### Retrieve a Specific Task

```
GET /api/tasks/{id}/
```

##### Response (200 OK)

```json
{
  "id": 2,
  "title": "Implement new feature",
  "description": "Implement the login functionality",
  "created_at": "2025-03-09T15:30:00Z",
  "due_date": "2025-03-20T18:00:00Z",
  "status": "TODO",
  "priority": "MEDIUM",
  "owner": 1,
  "assigned_to": 2,
  "tags": "feature,frontend,development", 
  "duration": 8.0,
  "owner_details": {
    "id": 1,
    "username": "example_user",
    "email": "user@example.com"
  },
  "assigned_to_details": {
    "id": 2,
    "username": "another_user",
    "email": "another@example.com"
  }
}
```

##### Possible Errors

- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Task not found or user doesn't have access

#### Update a Task

```
PUT /api/tasks/{id}/
```

##### Request Body (Complete Update)

```json
{
  "title": "Implement new feature",
  "description": "Updated description with more details",
  "due_date": "2025-03-22T18:00:00Z",
  "status": "IN_PROGRESS",
  "priority": "HIGH",
  "assigned_to": 2,
  "owner": 1,
  "tags": "feature,frontend,development,urgent",
  "duration": 10.5
}
```

##### Response (200 OK)

Task object with updated fields.

##### Partial Update

```
PATCH /api/tasks/{id}/
```

##### Request Body (Partial Update)

```json
{
  "status": "IN_PROGRESS",
  "priority": "HIGH",
  "tags": "feature,frontend,development,urgent",
  "duration": 12
}
```

You can also update tags using the `tags_list` field:

```json
{
  "title": "Updated Task",
  "description": "Updated description",
  "tags_list": ["new", "updated", "tags"]
}
```

##### Response (200 OK)

Task object with updated fields.

##### Possible Errors

- `400 Bad Request`: Invalid data
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Task not found or user doesn't have access

#### Delete a Task

```
DELETE /api/tasks/{id}/
```

##### Response (204 No Content)

No response body.

##### Possible Errors

- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Task not found or user doesn't have access

### Task Comments

#### List Comments for a Task

Returns all comments for a specific task, where the authenticated user is either the owner or assigned to the task.

```
GET /api/tasks/{task_id}/comments/
```

##### Response (200 OK)

```json
[
  {
    "id": 1,
    "task": 2,
    "author": 1,
    "content": "This is going well, I should be done by tomorrow.",
    "created_at": "2025-03-10T09:45:00Z",
    "updated_at": "2025-03-10T09:45:00Z",
    "author_details": {
      "id": 1,
      "username": "example_user",
      "email": "user@example.com"
    }
  },
  {
    "id": 2,
    "task": 2,
    "author": 3,
    "content": "Great progress! Let me know if you need any help.",
    "created_at": "2025-03-10T10:15:00Z",
    "updated_at": "2025-03-10T10:15:00Z",
    "author_details": {
      "id": 3,
      "username": "another_user",
      "email": "another@example.com"
    }
  }
]
```

##### Possible Errors

- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User is not the owner or assignee of the task
- `404 Not Found`: Task not found

#### Add a Comment to a Task

```
POST /api/tasks/{task_id}/comments/
```

##### Request Body

```json
{
  "content": "Just updated the UI, please review when you have time."
}
```

Note that the `task` and `author` fields are automatically set by the API based on the URL and the authenticated user.

##### Response (201 Created)

```json
{
  "id": 3,
  "task": 2,
  "author": 1,
  "content": "Just updated the UI, please review when you have time.",
  "created_at": "2025-03-11T14:22:00Z",
  "updated_at": "2025-03-11T14:22:00Z",
  "author_details": {
    "id": 1,
    "username": "example_user",
    "email": "user@example.com"
  }
}
```

##### Possible Errors

- `400 Bad Request`: Missing content field
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User is not the owner or assignee of the task
- `404 Not Found`: Task not found

#### Get a Specific Comment

```
GET /api/tasks/{task_id}/comments/{id}/
```

##### Response (200 OK)

```json
{
  "id": 1,
  "task": 2,
  "author": 1,
  "content": "This is going well, I should be done by tomorrow.",
  "created_at": "2025-03-10T09:45:00Z",
  "updated_at": "2025-03-10T09:45:00Z",
  "author_details": {
    "id": 1,
    "username": "example_user",
    "email": "user@example.com"
  }
}
```

##### Possible Errors

- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User is not the owner or assignee of the task
- `404 Not Found`: Task or comment not found

#### Update a Comment

Users can only update their own comments.

```
PUT /api/tasks/{task_id}/comments/{id}/
```

##### Request Body

```json
{
  "content": "Updated comment text with more information."
}
```

##### Response (200 OK)

```json
{
  "id": 1,
  "task": 2,
  "author": 1,
  "content": "Updated comment text with more information.",
  "created_at": "2025-03-10T09:45:00Z",
  "updated_at": "2025-03-11T16:30:00Z",
  "author_details": {
    "id": 1,
    "username": "example_user",
    "email": "user@example.com"
  }
}
```

##### Possible Errors

- `400 Bad Request`: Invalid data
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User is not the author of the comment
- `404 Not Found`: Task or comment not found

#### Delete a Comment

Users can only delete their own comments.

```
DELETE /api/tasks/{task_id}/comments/{id}/
```

##### Response (204 No Content)

No response body.

##### Possible Errors

- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User is not the author of the comment
- `404 Not Found`: Task or comment not found

### Task Checklists

Task checklists help break down tasks into smaller, actionable items that can be marked as complete.

#### List Checklist Items for a Task

Returns all checklist items for a specific task, where the authenticated user is either the owner or assigned to the task.

```
GET /api/tasks/{task_id}/checklist/
```

##### Response (200 OK)

```json
[
  {
    "id": 1,
    "task": 2,
    "text": "Research existing solutions",
    "is_completed": true,
    "position": 1,
    "created_at": "2025-03-10T09:45:00Z",
    "updated_at": "2025-03-10T09:45:00Z"
  },
  {
    "id": 2,
    "task": 2,
    "text": "Design database schema",
    "is_completed": false,
    "position": 2,
    "created_at": "2025-03-10T10:15:00Z",
    "updated_at": "2025-03-10T10:15:00Z"
  }
]
```

##### Possible Errors

- `401 Unauthorized`: Missing or invalid authentication token

#### Add a Checklist Item to a Task

```
POST /api/tasks/{task_id}/checklist/
```

##### Request Body

```json
{
  "text": "Implement API endpoints"
}
```

Note that the `task` field is automatically set based on the URL, and `is_completed` defaults to false. The `position` field is automatically calculated as the next available position.

##### Response (201 Created)

```json
{
  "id": 3,
  "task": 2,
  "text": "Implement API endpoints",
  "is_completed": false,
  "position": 3,
  "created_at": "2025-03-11T14:22:00Z",
  "updated_at": "2025-03-11T14:22:00Z"
}
```

##### Possible Errors

- `400 Bad Request`: Missing text field
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: User is not the owner or assignee of the task
- `404 Not Found`: Task not found

#### Get a Specific Checklist Item

```
GET /api/tasks/{task_id}/checklist/{id}/
```

##### Response (200 OK)

```json
{
  "id": 1,
  "task": 2,
  "text": "Research existing solutions",
  "is_completed": true,
  "position": 1,
  "created_at": "2025-03-10T09:45:00Z",
  "updated_at": "2025-03-10T09:45:00Z"
}
```

##### Possible Errors

- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Task or checklist item not found

#### Update a Checklist Item

```
PUT /api/tasks/{task_id}/checklist/{id}/
```

##### Request Body

```json
{
  "text": "Research existing solutions and alternatives",
  "is_completed": true
}
```

##### Response (200 OK)

```json
{
  "id": 1,
  "task": 2,
  "text": "Research existing solutions and alternatives",
  "is_completed": true,
  "position": 1,
  "created_at": "2025-03-10T09:45:00Z",
  "updated_at": "2025-03-11T16:30:00Z"
}
```

##### Possible Errors

- `400 Bad Request`: Invalid data
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Task or checklist item not found

#### Mark a Checklist Item as Complete

```
PATCH /api/tasks/{task_id}/checklist/{id}/complete/
```

##### Response (200 OK)

```json
{
  "id": 1,
  "task": 2,
  "text": "Research existing solutions",
  "is_completed": true,
  "position": 1,
  "created_at": "2025-03-10T09:45:00Z",
  "updated_at": "2025-03-11T16:30:00Z"
}
```

##### Possible Errors

- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Task or checklist item not found

#### Mark a Checklist Item as Incomplete

```
PATCH /api/tasks/{task_id}/checklist/{id}/incomplete/
```

##### Response (200 OK)

```json
{
  "id": 1,
  "task": 2,
  "text": "Research existing solutions",
  "is_completed": false,
  "position": 1,
  "created_at": "2025-03-10T09:45:00Z",
  "updated_at": "2025-03-11T16:30:00Z"
}
```

##### Possible Errors

- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Task or checklist item not found

#### Reorder Checklist Items

```
POST /api/tasks/{task_id}/checklist/reorder/
```

##### Request Body

```json
{
  "order": [3, 1, 2]
}
```

The `order` field should be an array of checklist item IDs in the desired order.

##### Response (200 OK)

```json
[
  {
    "id": 3,
    "task": 2,
    "text": "Implement API endpoints",
    "is_completed": false,
    "position": 1,
    "created_at": "2025-03-11T14:22:00Z",
    "updated_at": "2025-03-11T16:30:00Z"
  },
  {
    "id": 1,
    "task": 2,
    "text": "Research existing solutions",
    "is_completed": true,
    "position": 2,
    "created_at": "2025-03-10T09:45:00Z",
    "updated_at": "2025-03-11T16:30:00Z"
  },
  {
    "id": 2,
    "task": 2,
    "text": "Design database schema",
    "is_completed": false,
    "position": 3,
    "created_at": "2025-03-10T10:15:00Z",
    "updated_at": "2025-03-11T16:30:00Z"
  }
]
```

##### Possible Errors

- `400 Bad Request`: Invalid order data
- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Task not found

#### Delete a Checklist Item

```
DELETE /api/tasks/{task_id}/checklist/{id}/
```

##### Response (204 No Content)

No response body.

##### Possible Errors

- `401 Unauthorized`: Missing or invalid authentication token
- `404 Not Found`: Task or checklist item not found

## Status Codes

| Status Code | Description                                             |
|-------------|---------------------------------------------------------|
| 200         | OK - Request succeeded                                 |
| 201         | Created - Resource created successfully                |
| 204         | No Content - Request succeeded (no response body)      |
| 400         | Bad Request - Invalid request or validation failed     |
| 401         | Unauthorized - Authentication required or failed       |
| 403         | Forbidden - User does not have necessary permissions   |
| 404         | Not Found - Resource not found                         |
| 500         | Internal Server Error - Server encountered an error    |

## Data Models

### Task

| Field               | Type     | Description                                |
|---------------------|----------|--------------------------------------------|
| id                  | integer  | Unique identifier                          |
| title               | string   | Title of the task                          |
| description         | string   | Detailed description of the task           |
| created_at          | datetime | When the task was created (auto-generated) |
| due_date            | datetime | When the task is due                       |
| status              | string   | Status of the task (TODO, IN_PROGRESS, DONE) |
| priority            | string   | Priority level (LOW, MEDIUM, HIGH)         |
| owner               | integer  | ID of the user who created the task        |
| assigned_to         | integer  | ID of the user assigned to the task        |
| tags                | string   | Comma-separated list of tags               |
| duration            | float    | Estimated time to complete (in hours)      |
| checklist_items     | array    | List of checklist items for the task       |
| checklist_completion| integer  | Percentage of completed checklist items (0-100) |

### User

| Field    | Type    | Description                   |
|----------|---------|-------------------------------|
| id       | integer | Unique identifier             |
| username | string  | Username for authentication   |
| email    | string  | Email address of the user     |

### ChecklistItem

| Field        | Type     | Description                                |
|--------------|----------|--------------------------------------------|
| id           | integer  | Unique identifier                          |
| task         | integer  | ID of the task this item belongs to        |
| text         | string   | Description of the checklist item          |
| is_completed | boolean  | Whether the item is completed or not       |
| position     | integer  | Position for ordering within the checklist |
| created_at   | datetime | When the item was created (auto-generated) |
| updated_at   | datetime | When the item was last updated             |

## Examples

### Example: Complete User Workflow

1. Register a new user

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "email": "newuser@example.com", "password": "password123"}'
```

2. Login

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "newuser", "password": "password123"}'
```

3. Get user information

```bash
curl -X GET http://localhost:8000/api/auth/user/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
```

4. Create a task (using access token)

```bash
curl -X POST http://localhost:8000/api/tasks/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..." \
  -H "Content-Type: application/json" \
  -d '{"title": "New Task", "description": "Task description", "due_date": "2025-04-01T12:00:00Z", "status": "TODO", "priority": "MEDIUM", "assigned_to": 1, "owner": 1, "tags": "example,test", "duration": 2.5}'
```

5. List all tasks

```bash
curl -X GET http://localhost:8000/api/tasks/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
```

6. Filter tasks by status

```bash
curl -X GET "http://localhost:8000/api/tasks/?status=TODO" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
```

7. Filter tasks by tag

```bash
curl -X GET "http://localhost:8000/api/tasks/?tag=urgent" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
```

8. Update a task

```bash
curl -X PATCH http://localhost:8000/api/tasks/1/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..." \
  -H "Content-Type: application/json" \
  -d '{"status": "IN_PROGRESS", "tags_list": ["important", "in-progress"]}'
```

9. Delete a task

```bash
curl -X DELETE http://localhost:8000/api/tasks/1/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
```

10. Add a checklist item to a task

```bash
curl -X POST http://localhost:8000/api/tasks/1/checklist/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..." \
  -H "Content-Type: application/json" \
  -d '{"text": "Review code changes"}'
```

11. Mark a checklist item as complete

```bash
curl -X PATCH http://localhost:8000/api/tasks/1/checklist/1/complete/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..."
```

12. Reorder checklist items

```bash
curl -X POST http://localhost:8000/api/tasks/1/checklist/reorder/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1..." \
  -H "Content-Type: application/json" \
  -d '{"order": [3, 1, 2]}'
```

## Notes

- Access tokens expire after 15 minutes. Use the refresh token to get a new access token.
- All datetime fields should be in ISO 8601 format with timezone information.
- For filtering and searching tasks, you can combine multiple query parameters.
- Tags can be provided either as comma-separated values (`tags`) or as an array (`tags_list`).
- The duration field represents the estimated time in hours to complete the task.
- The checklist_completion field provides a quick way to see what percentage of a task's checklist items are completed. 