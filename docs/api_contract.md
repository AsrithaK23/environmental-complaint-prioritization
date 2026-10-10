# API Contract — Campus Environmental Complaint & Response System

**Owner:** Person 3 (Backend) · **Consumers:** Person 4 (Frontend), Person 2 (ML service)
**Status:** DRAFT v0.1 — items marked **[DECISION]** need team confirmation before coding.

Base URL (dev): `http://localhost:8000`
All backend endpoints are prefixed with `/api`. Responses are JSON unless stated.

---

## 0. Shared constants (single source of truth)

Every teammate must use these **exact strings**. One character of difference breaks routing.

### Categories (returned by Person 2's service)
```
Waste Management
Water / Sanitation
Air Pollution
Noise Pollution
Energy-related Issues
Greenery / Landscaping
Other
```
> Matches `docs/category_definitions.md` and the labels already in `dataset/raw/complaints_raw.csv` (Person 1). These are the exact strings; the shorter names in the original overview ("Energy", "Greenery") are NOT used.

### Priority
```
HIGH   MEDIUM   LOW
```

### Status
```
Pending   Assigned   In Progress   Resolved   Rejected
```

### Roles
```
USER   STAFF   ADMIN
```

### Category → Department routing **[DECISION]**
| Category | Department |
|---|---|
| Waste Management | Housekeeping |
| Water / Sanitation | Maintenance |
| Greenery / Landscaping | Garden / Landscaping |
| Energy-related Issues | Electrical / Maintenance |
| Air Pollution | Maintenance *(proposed — not in original spec)* |
| Noise Pollution | Administration *(proposed — not in original spec)* |
| Other | Administration *(proposed — not in original spec)* |

---

## 1. Conventions

- **Auth:** `Authorization: Bearer <access_token>` on every endpoint except register and login.
- **Errors:** `{"detail": "human readable message"}` with status:
  `400` bad input · `401` not logged in / bad token · `403` wrong role or not your data · `404` not found · `409` conflict (e.g. email exists, illegal status change) · `413` image too large · `415` bad image type · `422` validation error · `503` dependency unavailable.
- **Timestamps:** ISO-8601 UTC, e.g. `2026-10-10T12:30:00Z`.
- **Pagination (list endpoints):** `?page=1&page_size=20` → response `{"items": [...], "total": 57, "page": 1, "page_size": 20}`.

### Object: User
```json
{
  "id": 1,
  "name": "Amrutesh",
  "college_id": "CS2024001",
  "email": "a@college.edu",
  "role": "USER",
  "department": null,
  "created_at": "2026-10-10T12:00:00Z"
}
```

### Object: Complaint
```json
{
  "id": 42,
  "user_id": 1,
  "complaint_text": "Garbage near hostel B not collected for three days",
  "category": "Waste Management",
  "category_confidence": 0.91,
  "priority": "HIGH",
  "priority_reason": "Waste Management + 'three days' + repeat of 2 earlier complaints",
  "location": "Hostel B",
  "has_image": true,
  "image_url": "/api/complaints/42/image",
  "assigned_department": "Housekeeping",
  "assigned_staff": null,
  "status": "Pending",
  "resolution_note": null,
  "created_at": "2026-10-10T12:30:00Z",
  "updated_at": "2026-10-10T12:30:00Z"
}
```
Notes:
- `assigned_staff` is `null` or `{"id": 7, "name": "Ravi"}`.
- `image_url` is `null` when no image was uploaded. The image is **not public**: the frontend must fetch it with the Bearer token (e.g. via `fetch` → blob → object URL), not a plain `<img src>`.
- `category_confidence` is `null` if the ML service was unavailable and the fallback category was used.
- `priority_reason`, `category_confidence`, `resolution_note` are **additions** to the DB columns in the original spec (needed so the UI can show the resolution note and explain priority).

---

## 2. Authentication

### POST `/api/auth/register`  *(public)*
Request:
```json
{ "name": "...", "college_id": "...", "email": "...", "password": "min 8 chars" }
```
Response `201`: User object. Role is **always `USER`**; any `role` sent by the client is ignored.
Errors: `409` email or college_id already registered · `422` validation.

### POST `/api/auth/login`  *(public)*
Request: `{ "email": "...", "password": "..." }`
Response `200`:
```json
{ "access_token": "<jwt>", "token_type": "bearer", "expires_in": 3600, "user": { ...User } }
```
Errors: `401` invalid credentials.

### POST `/api/auth/logout`
Response `200`: `{"message": "Logged out"}`. Tokens are stateless; **the frontend must delete its stored token**.

### GET `/api/auth/me`  *(extra, for the frontend)*
Response `200`: User object for the current token. Use on page reload to restore session and role.

---

## 3. Complaints (any logged-in user)

### POST `/api/complaints`   — **multipart/form-data**, not JSON
| Field | Type | Rules |
|---|---|---|
| `complaint_text` | string | required, 10–2000 chars |
| `location` | string | required, 2–100 chars **[DECISION: free text vs fixed list of campus locations]** |
| `image` | file | optional; `image/jpeg`, `image/png`, `image/webp`; max 5 MB |

Backend does: validate → save image → call ML service → priority engine → routing → save (status `Pending`).
Response `201`: Complaint object (category, priority, department already filled in).
Errors: `415` bad type · `413` too large · `422` validation.
If the ML service is down, the complaint is **still saved** with category `Other`, `category_confidence: null`.

### GET `/api/complaints/my`
Own complaints, newest first. Query: `status` (optional), pagination.
Response `200`: paginated list of Complaint.

### GET `/api/complaints/{id}`
Allowed: the owner, STAFF of the complaint's `assigned_department`, or ADMIN. Otherwise `403`.
Response `200`: Complaint object.

### GET `/api/complaints/{id}/image`
Same access rule as above. Response: the image file (`Content-Type` of the stored image). `404` if no image.

---

## 4. Staff (role STAFF)

### GET `/api/staff/complaints`
Only complaints where `assigned_department` equals the staff member's own department (enforced server-side).
Query: `status`, `priority` (optional), pagination. Sorted by priority (HIGH first), then oldest first.
Response `200`: paginated list of Complaint.

### PATCH `/api/complaints/{id}/status`  *(STAFF of that department, or ADMIN)*
Request:
```json
{ "status": "In Progress", "resolution_note": "optional, required for Resolved/Rejected" }
```
Allowed transitions:
| From | To |
|---|---|
| Pending | Assigned, Rejected |
| Assigned | In Progress, Rejected |
| In Progress | Resolved, Rejected |
| Resolved / Rejected | *(final — no changes)* |

- `Pending → Assigned` sets `assigned_staff` to the calling staff member ("accept").
- `Resolved` and `Rejected` **require** a non-empty `resolution_note`.
Response `200`: updated Complaint.
Errors: `403` other department · `409` illegal transition · `422` missing note.

---

## 5. Admin (role ADMIN)

### GET `/api/admin/complaints`  *(extra)*
All complaints. Query: `status`, `priority`, `category`, `department`, pagination.

### PATCH `/api/admin/complaints/{id}/assign`  *(extra)*
Request: `{ "department": "Maintenance", "staff_id": 7 }` (`staff_id` optional; if given, must be STAFF of that department).
Response `200`: updated Complaint.

### GET `/api/admin/users`  *(extra)*
Query: `role`, `department`, pagination. Response: paginated list of User.

### POST `/api/admin/users`  *(extra — the only way to create STAFF/ADMIN)*
Request: `{ "name", "college_id", "email", "password", "role": "STAFF", "department": "Housekeeping" }`
Response `201`: User. `department` required when role is `STAFF`.

### PATCH `/api/admin/users/{id}`  *(extra)*
Request (all optional): `{ "role", "department", "name" }`. Response `200`: User.

### GET `/api/admin/analytics`
Response `200`:
```json
{
  "totals": { "total": 120, "pending": 30, "assigned": 20, "in_progress": 25, "resolved": 40, "rejected": 5, "high_priority": 18 },
  "by_category":   [ { "category": "Waste Management", "count": 40 } ],
  "by_location":   [ { "location": "Hostel B", "count": 12 } ],
  "by_department": [ { "department": "Housekeeping", "count": 40 } ],
  "pending_vs_resolved": { "pending": 30, "resolved": 40 },
  "monthly_trend": [ { "month": "2026-09", "count": 35 } ]
}
```
`high_priority` counts HIGH complaints that are not Resolved/Rejected.

---

## 6. ML service contract (Person 2 → Person 3) **[DECISION — Person 2 to confirm]**

Person 2 exposes the whole pipeline (preprocessing + TF-IDF + classifier) as an HTTP service. Person 3's backend is the **only** client. Preprocessing happens inside the service; the backend sends raw text.

Base URL (dev): `http://localhost:8001` (configurable via `ML_SERVICE_URL`).

### POST `/predict`
Request: `{ "text": "The garbage near hostel B hasn't been collected for three days." }`
Response `200`: `{ "category": "Waste Management", "confidence": 0.91 }`

Rules for Person 2:
- `category` must be **exactly** one of the 7 strings in section 0.
- `confidence` is a float 0–1 (probability of the predicted class).
- Empty/invalid text → `422`. Unexpected failure → `5xx` with `{"detail": "..."}`.
- Model loads once at service startup, not per request.
- Target latency: under 1 second per request.

### GET `/health`
Response `200`: `{ "status": "ok" }`

### Backend behaviour (Person 3)
- Timeout 5 s, 1 retry on timeout/5xx.
- If still failing: category `Other`, confidence `null`, log the error, **do not fail the user's submission**.
- If the service returns a category not in the list: treated as `Other`.
- Dev switch: `ML_USE_STUB=true` returns a keyword-based placeholder so nobody is blocked.

---

## 7. Backend environment variables

| Variable | Example |
|---|---|
| `DATABASE_URL` | `mysql+pymysql://user:pass@localhost:3306/campus_complaints` |
| `JWT_SECRET` | long random string |
| `JWT_EXPIRE_MINUTES` | `60` |
| `ML_SERVICE_URL` | `http://localhost:8001` |
| `ML_TIMEOUT_SECONDS` | `5` |
| `ML_USE_STUB` | `false` |
| `UPLOAD_DIR` | `backend/uploads` |
| `MAX_IMAGE_MB` | `5` |
| `CORS_ORIGINS` | `http://localhost:5173` |

---

## 8. Open decisions (answer before coding)

1. Category strings (section 0) now follow Person 1's `category_definitions.md` — Person 2 and Person 4 to confirm.
2. Departments for Air Pollution, Noise Pollution, Other — whole team.
3. `location`: free text or a fixed dropdown list — Persons 3 and 4.
4. ML service request/response shape and port (section 6) — Person 2.
5. Added DB columns: `resolution_note`, `priority_reason`, `category_confidence` — Person 3 (informational for Person 4).
