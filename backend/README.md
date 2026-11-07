# Campus Environmental Complaint & Response System
## Backend — Person 3

The backend for the **Campus Environmental Complaint & Response System** is responsible for authentication, complaint management, database operations, AI-based complaint classification, priority calculation, department assignment, and providing REST APIs for the frontend.

The backend acts as the central connection between the frontend (Person 4), NLP/AI service (Person 2), and database.

---

## Table of Contents

- [Project Overview](#project-overview)
- [My Responsibilities — Person 3](#my-responsibilities--person-3)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Backend Features](#backend-features)
- [Project Structure](#project-structure)
- [Database Design](#database-design)
- [Authentication and Authorization](#authentication-and-authorization)
- [Complaint Processing Workflow](#complaint-processing-workflow)
- [AI/ML Integration](#aiml-integration)
- [Priority Engine](#priority-engine)
- [Department Assignment](#department-assignment)
- [Complaint Status Lifecycle](#complaint-status-lifecycle)
- [API Endpoints](#api-endpoints)
- [Environment Configuration](#environment-configuration)
- [Local Setup and Execution](#local-setup-and-execution)
- [API Documentation](#api-documentation)
- [Production Deployment](#production-deployment)
- [Frontend Integration](#frontend-integration)
- [Error Handling](#error-handling)
- [Security Considerations](#security-considerations)
- [Current Deployment Status](#current-deployment-status)
- [Future Improvements](#future-improvements)
- [Team Responsibilities](#team-responsibilities)

---

## Project Overview

The Campus Environmental Complaint & Response System is designed to help students, faculty, and campus staff report environmental issues and track their resolution.

Users can submit complaints in natural language along with a location and optional image evidence.

The backend processes each complaint by:

1. Validating the incoming complaint.
2. Saving optional image evidence.
3. Sending complaint text to the NLP classification service.
4. Receiving the predicted complaint category.
5. Calculating complaint priority using explainable backend rules.
6. Automatically assigning the complaint to the appropriate department.
7. Saving the complaint and its details in the database.
8. Making the complaint available to authorized users, staff, and administrators.

The system also provides authentication, role-based access control, complaint tracking, staff management, and administrative analytics.

---

## My Responsibilities — Person 3

**Person 3: Backend, Authentication, Database & Complaint Management Logic**

My primary responsibility is developing and maintaining the backend infrastructure and business logic.

### Responsibilities

- Developing the FastAPI backend.
- Implementing user registration and login.
- Implementing password hashing and JWT authentication.
- Managing user roles: `USER`, `STAFF`, and `ADMIN`.
- Connecting the backend to the database.
- Designing and maintaining database tables.
- Integrating Person 2's NLP classification service.
- Developing the rule-based complaint priority engine.
- Implementing automatic department assignment.
- Managing complaint creation and retrieval.
- Implementing staff complaint management and status updates.
- Implementing administrator operations and analytics.
- Handling optional complaint image uploads.
- Providing REST API endpoints for Person 4's frontend.
- Deploying the backend to Render.
- Maintaining backend logic while preserving the agreed API contract.

### Responsibility Boundaries

| Team member | Responsibility |
|---|---|
| Person 1 | Dataset collection, cleaning, and preparation |
| Person 2 | NLP model training, classification, and ML service |
| **Person 3 — Backend** | Authentication, database, APIs, priority logic, routing, and backend integration |
| Person 4 | Frontend portals, UI components, and frontend integration |

The backend does not handle React UI design or NLP model training.

---

## System Architecture

```text
                    CAMPUS USER
                        |
                        v
              PERSON 4 — FRONTEND
                User / Staff / Admin
                        |
                        v
               PERSON 3 — BACKEND
                 FastAPI REST API
                        |
         +--------------+--------------+
         |              |              |
         v              v              v
 Authentication   Complaint Logic   Admin / Staff
   JWT & Roles     & Validation      Operations
         |              |
         |              v
         |        PERSON 2 — NLP
         |         ML Classification
         |              |
         |<-------------+
         |
         v
       Priority Engine
         |
         v
   Department Routing
         |
         v
      TiDB Cloud
   MySQL-Compatible DB
```

### Architecture Explanation

The frontend communicates only with the backend APIs.

The backend is responsible for coordinating all major operations. It sends complaint text to Person 2's ML service and receives the predicted category.

The backend then applies priority rules, determines the appropriate department, and stores the complaint in the database.

The database stores users, complaints, assignment information, status, and resolution details.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming language |
| FastAPI | REST API framework |
| Uvicorn | ASGI server |
| Pydantic | Request validation and configuration |
| JWT | Authentication tokens |
| Password hashing | Secure password storage |
| HTTPX | Communication with the ML service |
| MySQL-compatible SQL | Database operations |
| TiDB Cloud | Hosted production database |
| Render | Backend hosting and deployment |
| GitHub | Version control and collaboration |
| Swagger UI | API testing and documentation |

---

## Backend Features

### 1. Authentication

- User registration.
- User login.
- Password hashing.
- JWT access token generation.
- Token-based authentication.
- User identity retrieval.
- Role-based access control.

### 2. Complaint Management

- Complaint submission.
- Complaint category classification.
- Priority calculation.
- Department assignment.
- Optional image upload.
- Complaint retrieval.
- User complaint history.
- Complaint status updates.
- Resolution notes.

### 3. Staff Management

- Department-specific complaint access.
- Complaint acceptance and assignment.
- Complaint status updates.
- Resolution and rejection handling.

### 4. Administration

- Complaint overview.
- User management.
- Staff and department management.
- Complaint assignment.
- Administrative analytics.

### 5. ML Integration

- External NLP service integration.
- Complaint category prediction.
- Confidence score handling.
- Timeout handling.
- Retry mechanism.
- Fallback classification when the service is unavailable.

---

## Project Structure

The backend follows a modular structure that separates authentication, complaint logic, database operations, and ML integration.

```text
environmental-complaint-prioritization/
│
├── backend/
│   └── app/
│       ├── main.py
│       ├── config.py
│       │
│       ├── auth/
│       │   ├── routes.py
│       │   ├── schemas.py
│       │   └── security.py
│       │
│       ├── complaints/
│       │   ├── routes.py
│       │   ├── schemas.py
│       │   └── service.py
│       │
│       ├── admin/
│       │   └── routes.py
│       │   ├── schemas.py
│       │
│       ├── ml/
│       │   └── classifier.py
│       │
│       ├── priority/
│       │   └── priority_engine.py
│       │
│       └── database/
│           ├── connection.py
│           └── models.py
│
├── database/
│   ├── schema.sql
│   └── seed.sql
│
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

**Note:** The structure above represents the intended backend organization. Refer to the actual repository for the latest files and implementation details.

---

## Database Design

The backend uses a MySQL-compatible relational database.

- **Local development:** MySQL
- **Production:** TiDB Cloud

The production database is hosted separately from the Render backend.

### Database Name

```text
campus_complaints
```

### Users Table

Stores user account information.

| Column | Description |
|---|---|
| `id` | Primary key |
| `name` | User's name |
| `college_id` | Unique college identification |
| `email` | Unique email address |
| `password_hash` | Hashed password |
| `role` | USER, STAFF, or ADMIN |
| `department` | Department for staff users |
| `created_at` | Account creation timestamp |

### Complaints Table

Stores environmental complaints and their processing information.

| Column | Description |
|---|---|
| `id` | Complaint primary key |
| `user_id` | User who submitted the complaint |
| `complaint_text` | Complaint description |
| `category` | ML-predicted category |
| `category_confidence` | Classification confidence |
| `priority` | HIGH, MEDIUM, or LOW |
| `priority_reason` | Explanation of priority |
| `location` | Complaint location |
| `image_path` | Optional image storage path |
| `assigned_department` | Responsible department |
| `assigned_staff` | Staff member assigned to complaint |
| `status` | Complaint status |
| `resolution_note` | Resolution or rejection explanation |
| `created_at` | Complaint creation time |
| `updated_at` | Last update time |

### Database Relationships

- One user can submit multiple complaints.
- Each complaint belongs to one user.
- A complaint can optionally be assigned to a staff member.
- Staff members are represented in the users table with the `STAFF` role.

Foreign key relationships and indexes are used to maintain data integrity and support complaint retrieval.

---

## Authentication and Authorization

The backend uses JWT-based authentication.

### Registration

Endpoint:

```http
POST /api/auth/register
```

A user provides:

- Name
- College ID
- Email
- Password

The password is hashed before storage.

Public registration creates users with the `USER` role. Staff and administrator accounts are managed through authorized administrative operations.

### Login

Endpoint:

```http
POST /api/auth/login
```

Successful login returns an access token.

Example response:

```json
{
  "access_token": "<access-token>",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": 1,
    "name": "Example User",
    "college_id": "COLLEGE001",
    "email": "user@example.com",
    "role": "USER"
  }
}
```

The frontend must use the token when calling protected endpoints.

### Authorization Header

```http
Authorization: Bearer <access_token>
```

### User Roles

| Role | Access |
|---|---|
| USER | Submit complaints and access their own complaints |
| STAFF | Access and manage complaints assigned to their department |
| ADMIN | Manage users, departments, complaints, assignments, and analytics |

Authorization is enforced by the backend, not merely by frontend visibility.

---

## Complaint Processing Workflow

When a user submits a complaint, the backend performs the following operations:

### Step 1 — Receive Complaint

The backend receives:

- Complaint text
- Location
- Optional image

### Step 2 — Validate Input

The backend validates required fields and request constraints.

### Step 3 — Handle Image

If an image is provided:

- Validate the image type.
- Check the maximum file size.
- Store the image.
- Save its path in the database.

Images are evidence for staff verification. The system does not use image AI for classification.

### Step 4 — Classify Complaint

The backend sends complaint text to Person 2's NLP service.

The ML service returns a category and confidence score.

### Step 5 — Calculate Priority

The backend priority engine analyzes the complaint using explainable rules.

### Step 6 — Assign Department

The backend determines the department responsible for the complaint based on its category.

### Step 7 — Store Complaint

The backend saves the complaint in the database with:

- Category
- Confidence
- Priority
- Priority reason
- Location
- Department
- Status
- User ID
- Image path, if available

New complaints are created with the `Pending` status.

### Step 8 — Return Response

The backend returns the created complaint to the frontend.

---

## AI/ML Integration

Person 3's backend integrates with Person 2's NLP service.

### ML Service

Production service:

```text
https://environmental-complaint-nlp-api.vercel.app
```

Prediction endpoint:

```http
POST /predict
```

The backend sends raw complaint text to the prediction service.

Example request:

```json
{
  "text": "Garbage has not been collected near the hostel for three days."
}
```

Example response:

```json
{
  "category": "Waste Management",
  "confidence": 0.91
}
```

The exact category strings are shared between the dataset, ML service, and backend.

### Supported Categories

```text
Waste Management
Water / Sanitation
Air Pollution
Noise Pollution
Energy-related Issues
Greenery / Landscaping
Other
```

### ML Service Reliability

The backend includes:

- Configurable request timeout.
- One retry after timeout or server-side failure.
- Response validation.
- Category validation.
- Confidence validation.
- Fallback behavior.

If the ML service is unavailable or returns invalid data, the backend falls back to:

```text
Category: Other
Confidence: null
```

The complaint can still be submitted and stored.

This prevents temporary ML service failures from blocking complaint submission.

---

## Priority Engine

The backend priority engine is rule-based and explainable.

It does not train another machine learning model.

The engine analyzes complaint text and contextual information to assign:

```text
HIGH
MEDIUM
LOW
```

### Critical Safety Indicators

Recognized critical hazards can immediately trigger HIGH priority.

Examples include:

- Fire or burning hazards.
- Electrical hazards.
- Gas or chemical hazards.
- Sewage overflow.
- Unsafe drinking water.
- Serious injury indicators.

### Severity Indicators

The engine also identifies non-emergency indicators such as:

- Water leaks.
- Blocked drains.
- Overflow.
- Waste accumulation.
- Stagnant water or mosquitoes.
- Smoke, dust, or foul smell.
- Lighting faults.
- Fallen trees or branches.
- Noise disturbances.

### Additional Context

The priority engine supports additional scoring factors:

- Repeated similar complaints.
- Number of affected people.
- Sensitive locations such as hostels, laboratories, kitchens, and classrooms.
- Time the complaint remains unresolved.

### Priority Thresholds

The current engine maps scores to priority as follows:

| Score | Priority |
|---|---|
| 0–1 | LOW |
| 2–3 | MEDIUM |
| 4 or above | HIGH |

Critical safety indicators can trigger HIGH priority immediately.

### Explainability

The engine generates a reason explaining the priority decision.

This allows staff and administrators to understand why a complaint was marked HIGH, MEDIUM, or LOW.

**Important:** The priority engine is rule-based. It does not perform full natural-language understanding, and keyword matching may not interpret every complaint perfectly. Its rules can be improved as more realistic complaint scenarios are evaluated.

---

## Department Assignment

The backend automatically routes complaints based on their predicted category.

| Category | Assigned Department |
|---|---|
| Waste Management | Housekeeping |
| Water / Sanitation | Maintenance |
| Greenery / Landscaping | Garden / Landscaping |
| Energy-related Issues | Electrical / Maintenance |
| Air Pollution | Maintenance |
| Noise Pollution | Administration |
| Other | Administration |

Department routing is performed by the backend, not the frontend.

This ensures that complaints are assigned consistently.

---

## Complaint Status Lifecycle

Complaints follow a defined status lifecycle.

```text
Pending
   |
   v
Assigned
   |
   v
In Progress
   |
   v
Resolved
```

A complaint can also be rejected through authorized staff or administrator operations.

### Supported Statuses

```text
Pending
Assigned
In Progress
Resolved
Rejected
```

### Status Transitions

| Current Status | Allowed Next Status |
|---|---|
| Pending | Assigned, Rejected |
| Assigned | In Progress, Rejected |
| In Progress | Resolved, Rejected |
| Resolved | Final |
| Rejected | Final |

When a complaint is resolved or rejected, a resolution note is required according to the API contract.

---

## API Endpoints

The backend exposes REST APIs under:

```text
/api
```

### Base URLs

Local development:

```text
http://localhost:8000
```

Production:

```text
https://environmental-complaint-prioritization.onrender.com
```

### Health Check

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Check backend availability |

Example response:

```json
{
  "status": "ok"
}
```

### Authentication

| Method | Endpoint | Purpose | Authentication |
|---|---|---|---|
| POST | `/api/auth/register` | Register a new user | Public |
| POST | `/api/auth/login` | Authenticate user | Public |
| POST | `/api/auth/logout` | Logout | Authenticated |
| GET | `/api/auth/me` | Get current user | Authenticated |

### Complaint Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/complaints` | Submit a complaint |
| GET | `/api/complaints/my` | Get current user's complaints |
| GET | `/api/complaints/{id}` | Get complaint details |
| GET | `/api/complaints/{id}/image` | Retrieve complaint image |
| PATCH | `/api/complaints/{id}/status` | Update complaint status |

Complaint submission uses `multipart/form-data` because an optional image can be uploaded.

### Staff Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/staff/complaints` | Get department-specific complaints |
| PATCH | `/api/complaints/{id}/status` | Accept, update, resolve, or reject a complaint |

Staff access is restricted by department.

### Admin Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/admin/complaints` | View complaints |
| PATCH | `/api/admin/complaints/{id}/assign` | Assign department or staff |
| GET | `/api/admin/users` | View users |
| POST | `/api/admin/users` | Create staff or administrator accounts |
| PATCH | `/api/admin/users/{id}` | Update user role or department |
| GET | `/api/admin/analytics` | View complaint analytics |

**Note:** This endpoint list follows the shared API contract. Use the deployed Swagger documentation as the final authority for the exact request schemas and current endpoint behavior.

---

## Environment Configuration

The backend uses environment variables for database credentials, JWT configuration, ML integration, image uploads, and CORS.

### Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | Database connection string |
| `JWT_SECRET` | Secret used for JWT signing |
| `JWT_EXPIRE_MINUTES` | JWT token expiration in minutes |
| `ML_SERVICE_URL` | NLP service base URL |
| `ML_TIMEOUT_SECONDS` | ML request timeout |
| `ML_USE_STUB` | Enable or disable ML fallback stub |
| `UPLOAD_DIR` | Directory for image uploads |
| `MAX_IMAGE_MB` | Maximum image upload size |
| `CORS_ORIGINS` | Allowed frontend origins |

### Example `.env`

Create a `.env` file in the project root.

```env
DATABASE_URL=your_database_connection_string

JWT_SECRET=your_long_random_secret
JWT_EXPIRE_MINUTES=60

ML_SERVICE_URL=https://environmental-complaint-nlp-api.vercel.app
ML_TIMEOUT_SECONDS=5
ML_USE_STUB=false

UPLOAD_DIR=backend/uploads
MAX_IMAGE_MB=5

CORS_ORIGINS=http://localhost:5173
```

Replace placeholder values with your own configuration.

**Never commit `.env` files, database passwords, JWT secrets, or access tokens to GitHub.**

For production, configure environment variables through the hosting provider's environment settings.

---

## Local Setup and Execution

### Prerequisites

- Python 3.11 or compatible Python version.
- Git.
- MySQL for local database development.
- Access to the NLP service or a development stub configuration.

### 1. Clone the Repository

```bash
git clone https://github.com/AsrithaK23/environmental-complaint-prioritization.git
```

Navigate to the project:

```bash
cd environmental-complaint-prioritization
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it in Git Bash:

```bash
source .venv/Scripts/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create the `.env` file in the project root and configure the required values.

Ensure the database exists and the database connection string is correct.

### 5. Run the Backend

```bash
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

The backend will run locally at:

```text
http://localhost:8000
```

### 6. Open API Documentation

```text
http://localhost:8000/docs
```

Use Swagger UI to test endpoints.

---

## API Documentation

FastAPI automatically generates interactive API documentation.

### Swagger UI

Local:

```text
http://localhost:8000/docs
```

Production:

[Open Production API Documentation](https://environmental-complaint-prioritization.onrender.com/docs)

Swagger allows developers to:

- Inspect available endpoints.
- View request and response schemas.
- Register users.
- Test authentication.
- Authorize protected endpoints.
- Submit complaints.
- Verify responses.

The Swagger documentation is particularly useful for Person 4 during frontend integration.

---

## Production Deployment

The backend is deployed using **Render**.

### Deployment Details

| Component | Service |
|---|---|
| Backend hosting | Render |
| Production database | TiDB Cloud |
| Backend framework | FastAPI |
| Server | Uvicorn |

### Render Configuration

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
```

The backend connects to TiDB Cloud using the configured database connection string.

### Production Environment Variables

Configure the following through Render's environment variable settings:

- `DATABASE_URL`
- `JWT_SECRET`
- `JWT_EXPIRE_MINUTES`
- `ML_SERVICE_URL`
- `ML_TIMEOUT_SECONDS`
- `ML_USE_STUB`
- `UPLOAD_DIR`
- `MAX_IMAGE_MB`
- `CORS_ORIGINS`

Do not store production credentials directly in source code.

### Production Backend URL

```text
https://environmental-complaint-prioritization.onrender.com
```

### Production Health Check

```text
https://environmental-complaint-prioritization.onrender.com/api/health
```

Expected response:

```json
{
  "status": "ok"
}
```

### Free Hosting Considerations

The Render free instance may spin down after periods of inactivity. This can cause slower responses when the service starts again.

The free instance also does not provide persistent disks. Local image uploads may therefore be lost after certain redeployments or restarts.

For reliable long-term image storage, external object storage should be considered.

---

## Frontend Integration

Person 4's frontend should communicate with the backend using the production API URL.

### Production API Base URL

```text
https://environmental-complaint-prioritization.onrender.com/api
```

### Recommended Frontend Configuration

The frontend should store the backend URL in its own environment configuration.

For example, in a Vite frontend:

```env
VITE_API_BASE_URL=https://environmental-complaint-prioritization.onrender.com/api
```

The frontend should:

1. Register and authenticate users through the backend.
2. Store and use the returned access token according to the team's security decisions.
3. Include the Bearer token in protected API requests.
4. Submit complaints using `multipart/form-data`.
5. Retrieve complaints using the backend endpoints.
6. Display the category, priority, department, and status returned by the backend.
7. Handle API errors appropriately.

### Important Integration Rule

The frontend must not independently calculate complaint priority or department assignment.

These decisions belong to the backend.

The frontend should display the values returned by the API.

---

## Error Handling

The backend returns JSON error responses.

Example:

```json
{
  "detail": "Human-readable error message"
}
```

Common HTTP status codes include:

| Status Code | Meaning |
|---|---|
| 200 | Successful request |
| 201 | Resource created |
| 400 | Invalid request or business rule |
| 401 | Authentication required or invalid credentials |
| 403 | Insufficient permissions |
| 404 | Resource not found |
| 409 | Conflict |
| 413 | Image too large |
| 415 | Unsupported image type |
| 422 | Validation error |
| 503 | Dependency unavailable |

The exact status code for a particular error depends on the endpoint implementation.

---

## Security Considerations

The backend implements authentication and authorization to protect user and complaint data.

Important security practices include:

- Passwords are stored as hashes, not plaintext.
- JWT secrets are kept in environment variables.
- Protected endpoints require authentication.
- Staff access is restricted to their assigned department.
- Users should only access their own complaints unless authorized otherwise.
- Admin operations require administrator privileges.
- Uploaded images are validated.
- Production credentials must never be committed to GitHub.
- Database access credentials should be rotated if exposed.
- Access tokens should not be shared in screenshots, logs, or public repositories.

The backend should continue to be reviewed for security as frontend integration and testing progress.

---

## Current Deployment Status

The following core backend functionality has been deployed and verified:

| Feature | Status |
|---|---|
| FastAPI backend deployment | Verified |
| Render hosting | Verified |
| TiDB Cloud connection | Verified |
| Database tables | Created and verified |
| User registration | Tested successfully |
| User login | Tested successfully |
| JWT token generation | Tested successfully |
| Complaint submission | Tested successfully |
| ML classification integration | Tested successfully |
| Priority calculation | Tested successfully |
| Department assignment | Tested successfully |
| Complaint database persistence | Tested successfully |
| CORS configuration | Configured and deployed |

Registration, login, and complaint submission were tested against the deployed backend. The resulting user and complaint records were also verified in TiDB Cloud.

The backend is now ready for continued frontend integration and targeted improvements to internal business logic.

---

## Future Improvements

Potential improvements include:

- Refining priority rules using more realistic complaint scenarios.
- Improving priority scoring using complaint recurrence and impact data.
- Improving ML failure monitoring and logging.
- Adding automated backend tests.
- Improving API error consistency.
- Adding persistent image storage.
- Improving complaint analytics.
- Reviewing API performance and database indexes.
- Adding stronger production monitoring.
- Improving deployment reliability.

These improvements should be introduced without unnecessarily breaking the existing API contract.

---

## Team Responsibilities

### Person 1 — Dataset and Data Preparation

Responsible for collecting, cleaning, and preparing complaint data for model training.

### Person 2 — NLP and AI Model

Responsible for training the complaint classification model and exposing the prediction service.

### Person 3 — Backend, Authentication, Database and Logic

Responsible for:

- Authentication.
- Database.
- REST APIs.
- Complaint processing.
- ML service integration.
- Priority engine.
- Department routing.
- Backend deployment.

### Person 4 — Frontend and Portals

Responsible for:

- User portal.
- Staff portal.
- Admin portal.
- Frontend components.
- API integration.
- User experience.

---

## Final Note

The backend serves as the central processing layer of the Campus Environmental Complaint & Response System.

It connects the frontend, NLP classification service, priority engine, department routing logic, and database to provide a complete complaint management workflow.

The core backend deployment and integration have been completed. Future backend development will focus primarily on improving internal logic, reliability, security, and performance while maintaining compatibility with the agreed API contract.

---

**Backend Developer: Person 3**
**Project:** Campus Environmental Complaint & Response System
**Backend Framework:** FastAPI
**Deployment:** Render
**Database:** TiDB Cloud
**Repository:** [environmental-complaint-prioritization](https://github.com/AsrithaK23/environmental-complaint-prioritization)
