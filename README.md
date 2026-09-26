# AI-Based Environmental Complaint Prioritization System

## 📌 Overview

The **AI-Based Environmental Complaint Prioritization System** is a campus-focused complaint management platform designed to make the reporting and resolution of environmental issues more structured, transparent, and efficient.

The system allows students, faculty, and staff to report environmental complaints through a centralized platform. Submitted complaints are analyzed using an NLP-based classification model to identify the complaint category. A rule-based priority engine then determines the urgency of the complaint, after which the system routes it to the appropriate campus department.

Staff members can process assigned complaints, update their status, and provide resolution details, while administrators can monitor complaints and view system-level analytics.

---

## 🎯 Objectives

- Provide a centralized platform for reporting campus environmental issues.
- Automatically classify complaints using Natural Language Processing (NLP).
- Determine complaint priority using explainable rules.
- Route complaints to the appropriate department.
- Allow staff to manage and resolve complaints.
- Provide users with transparent complaint tracking.
- Provide administrators with an overview of complaint trends and system activity.

---

## 👥 System Users

### 1. Campus Users

Students, faculty, and staff can:

- Register and log in.
- Submit environmental complaints.
- Select the complaint location.
- Upload optional image evidence.
- View the predicted complaint category.
- View complaint priority.
- Track complaint status.
- View previous complaints.

### 2. Staff

Authorized department staff can:

- View assigned complaints.
- Review complaint details and evidence.
- Update complaint status.
- Add response or resolution notes.
- Process complaints assigned to their department.

### 3. Administrator

Administrators can:

- View all complaints.
- Assign or reassign complaints.
- Manage users and departments.
- Monitor high-priority complaints.
- View complaint statistics and trends.
- Monitor the overall complaint resolution process.

---

## 🔄 Complaint Processing Workflow

```text
                    ┌──────────────────────┐
                    │     Campus User      │
                    │  Student / Faculty   │
                    │       / Staff        │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Submit Complaint  │
                    │  Text + Location +   │
                    │   Optional Evidence  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      FastAPI         │
                    │    Backend API       │
                    └──────────┬───────────┘
                               │
                  ┌────────────┴────────────┐
                  ▼                         ▼
        ┌──────────────────┐      ┌──────────────────┐
        │  NLP Classifier  │      │  Priority Engine │
        │                  │      │                  │
        │ Complaint →      │      │ High / Medium /  │
        │ Category         │      │ Low              │
        └────────┬─────────┘      └────────┬─────────┘
                 │                         │
                 └────────────┬────────────┘
                              ▼
                   ┌──────────────────────┐
                   │ Department Routing   │
                   │                      │
                   │ Category → Relevant │
                   │ Campus Department    │
                   └──────────┬───────────┘
                              │
                              ▼
                   ┌──────────────────────┐
                   │     MySQL Database   │
                   │                      │
                   │ Users + Complaints  │
                   │ Assignments + Status│
                   └──────────┬───────────┘
                              │
                ┌─────────────┴─────────────┐
                ▼                           ▼
      ┌──────────────────┐        ┌──────────────────┐
      │   Staff Portal   │        │  Admin Dashboard │
      │                  │        │                  │
      │ Process &        │        │ Monitor &        │
      │ Resolve          │        │ Analyze          │
      │ Complaints       │        │ Complaints       │
      └────────┬─────────┘        └────────┬─────────┘
               │                           │
               └─────────────┬─────────────┘
                             ▼
                    ┌──────────────────────┐
                    │   Complaint Status   │
                    │                      │
                    │ Pending → Assigned   │
                    │ → In Progress        │
                    │ → Resolved           │
                    └──────────────────────┘