# CAREER CONNECT - Modern Job Board & Talent Recruitment Platform

**Academic Capstone Project &bull; B.Tech Computer Science and Engineering**

---

## 1. Project Overview

**CAREER CONNECT** is a full-stack, enterprise-grade Job Board and Talent Recruitment Platform designed to bridge the gap between ambitious job seekers and verified technology employers. Developed using Python **Django**, **Django REST Framework (DRF)**, **Bootstrap 5**, and **SQLite**, the platform incorporates role-based access control, real-time application lifecycle tracking, resume parsing/upload validation, multi-channel notifications, and interactive analytics dashboards.

### Key Highlights
* **3 Dedicated Portals**: Distinct dashboards and access-controlled workflows for **Platform Admins**, **Employers/Recruiters**, and **Candidates/Job Seekers**.
* **Smart 1-Click Viva Demo Bar**: Pinned at the top of the interface for instantaneous switching between Admin, Employer, and Candidate roles during evaluation and presentations.
* **Resume Management**: Verified PDF resume uploads with size and format security validation.
* **Duplicate Prevention**: Database-level unique constraint (`job`, `candidate`) preventing candidates from submitting duplicate applications.
* **Automated Notification Engine**: Instant in-app alerts triggered on status updates and new applications.
* **RESTful API Layer**: Complete CRUD APIs powered by Django REST Framework with serialized models and JSON statistics.
* **Chart.js Analytics**: Visual doughnut and bar charts visualizing application distribution and employment type breakdowns.

---

## 2. Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Backend Framework** | Python 3.14+, Django 6.1 (MVT Architecture) |
| **REST API** | Django REST Framework (DRF) 3.18+ |
| **Database** | SQLite3 (Configured with foreign keys & unique constraints) |
| **Frontend UI** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3.3 |
| **Icons & Visuals** | Bootstrap Icons 1.11.3 |
| **Data Visualization** | Chart.js 4.4 |
| **File Handling** | Django Storage Engine, Pillow 13.0, PDF Content Validation |

---

## 3. User Roles & Access Control Matrix

```
                      +-------------------+
                      |   CareerConnect   |
                      +---------+---------+
                                |
        +-----------------------+-----------------------+
        |                       |                       |
+-------v-------+       +-------v-------+       +-------v-------+
|   Candidate   |       |   Employer    |       | Platform Admin|
|   (Seeker)    |       |  (Recruiter)  |       | (Governance)  |
+-------+-------+       +-------+-------+       +-------+-------+
        |                       |                       |
* Browse & Filter Jobs  * Post Job Vacancies    * User Management
* Upload PDF Resume     * Edit/Close Listings   * Company Verification
* Submit Applications   * Review Inbound CVs    * Job Moderation
* Real-time Tracking    * Update Status (4-tier)* Platform Charts
* Withdraw Applications * Add Recruiter Notes   * System Statistics
* In-app Notifications  * Candidate Notifications* Django Superuser
```

---

## 4. Database Schema & Architecture

The database schema is structured into 4 cohesive apps:

### 1. `accounts` App
* **`User`** (`AbstractUser`):
  * `role`: `ADMIN`, `EMPLOYER`, `CANDIDATE`
  * `phone`, `bio`, `profile_picture`
* **`Company`**:
  * `name`, `slug`, `website`, `logo_url`, `industry`, `company_size`, `headquarters`, `description`, `is_verified`
* **`EmployerProfile`**:
  * One-to-One with `User`
  * ForeignKey to `Company`
  * `designation`, `is_approved`
* **`CandidateProfile`**:
  * One-to-One with `User`
  * `headline`, `skills`, `resume` (PDF file)
  * `education_degree`, `education_institution`, `graduation_year`, `cgpa_or_percentage`
  * `experience_years`, `current_location`, `github_url`, `linkedin_url`, `portfolio_url`

### 2. `jobs` App
* **`Job`**:
  * ForeignKey to `employer` (`User`) and `company` (`Company`)
  * `title`, `description`, `required_skills`, `location`, `is_remote`
  * `employment_type` (`FULL_TIME`, `PART_TIME`, `INTERNSHIP`, `CONTRACT`)
  * `experience_level` (`ENTRY`, `MID`, `SENIOR`, `LEAD`)
  * `min_salary`, `max_salary`, `salary_negotiable`
  * `vacancies`, `deadline`, `status` (`ACTIVE`, `CLOSED`, `EXPIRED`)
  * `is_featured`, `is_approved`, `views_count`
* **`Application`**:
  * ForeignKey to `job` (`Job`) and `candidate` (`User`)
  * `resume` (snapshot or profile resume)
  * `cover_letter`
  * `status` (`PENDING`, `SHORTLISTED`, `SELECTED`, `REJECTED`)
  * `employer_notes` (Interview feedback/schedule)
  * **Constraint**: `unique_together = ('job', 'candidate')`

### 3. `notifications` App
* **`Notification`**:
  * `recipient`, `sender`, `title`, `message`
  * `notification_type` (`STATUS_CHANGE`, `NEW_APPLICATION`, `JOB_ALERT`, `SYSTEM`)
  * `target_url`, `is_read`, `created_at`

### 4. `api` App
* Serializers and ViewSets for `Job`, `Application`, `Company`, `Notification`, and `DashboardStats`.

---

## 5. REST API Documentation

Base URI: `/api/v1/`

| Endpoint | Method | Role | Description |
| :--- | :--- | :--- | :--- |
| `/api/v1/jobs/` | `GET` | Public | List active and approved jobs (supports `q`, `location`, `skills`, `type`, `exp`, `min_salary` query parameters). |
| `/api/v1/jobs/{id}/` | `GET` | Public | Retrieve single job details. |
| `/api/v1/jobs/` | `POST` | Employer/Admin | Create new job vacancy. |
| `/api/v1/jobs/{id}/` | `PUT/PATCH`| Employer/Admin | Update job listing. |
| `/api/v1/jobs/{id}/` | `DELETE` | Employer/Admin | Delete job listing. |
| `/api/v1/applications/` | `GET` | Authenticated | Candidates see their applications; Employers see applicants for their jobs. |
| `/api/v1/applications/` | `POST` | Candidate | Submit job application. Enforces duplicate check. |
| `/api/v1/applications/{id}/` | `PATCH` | Employer | Update status (`PENDING`, `SHORTLISTED`, `SELECTED`, `REJECTED`) & notes. |
| `/api/v1/applications/{id}/` | `DELETE`| Candidate | Withdraw application. |
| `/api/v1/companies/` | `GET` | Public | List partner companies. |
| `/api/v1/notifications/` | `GET` | Authenticated | List user notifications. |
| `/api/v1/notifications/mark_all_read/`| `POST` | Authenticated | Mark all notifications as read. |
| `/api/v1/stats/` | `GET` | Authenticated | Dynamic dashboard statistics and chart data tailored to user role. |

---

## 6. Setup & Installation Guide

### Prerequisites
* Python 3.10 or higher
* `pip` package manager

### Steps to Run Locally

```bash
# 1. Open terminal inside project directory
cd "task 4"

# 2. (Optional) Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 3. Install required packages
pip install -r requirements.txt

# 4. Apply database migrations
python manage.py migrate

# 5. Populate realistic initial sample data
python manage.py seed_data

# 6. Run automated test suite
python manage.py test

# 7. Start the development server
python manage.py runserver
```

Open your browser at: **`http://127.0.0.1:8000/`**

---

## 7. Demo Accounts & Credentials

For academic presentations, college vivas, or quick testing, use either the **1-Click Demo Bar** at the top of every page, or log in with these credentials:

| Role | Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **Platform Admin** | `admin` | `admin123` | Full control: user deactivation, job approval, company verification, Django Admin (`/admin/`). |
| **Employer (Google)** | `techlead_google` | `pass123` | Hiring manager for Google Cloud India. Can post jobs, review resumes, shortlist/hire. |
| **Employer (Microsoft)** | `hr_microsoft` | `pass123` | Recruiter for Microsoft IDC. |
| **Employer (AWS)** | `aws_recruiter` | `pass123` | Cloud Talent Lead at Amazon Web Services. |
| **Employer (Razorpay)** | `razorpay_hr` | `pass123` | FinTech recruiter at Razorpay Payments. |
| **Candidate (Full Stack)**| `rahul_sharma` | `pass123` | Has applied for Google & Razorpay. Shows Shortlisted and Selected statuses. |
| **Candidate (AI/ML)** | `priya_patel` | `pass123` | Shortlisted at Microsoft IDC Copilot Platforms. |
| **Candidate (DevOps)** | `aman_verma` | `pass123` | Selected / Offer Extended at AWS. |
| **Candidate (Fresher)** | `vikram_singh` | `pass123` | B.Tech CSE 2026 Fresher. Applied for Campus Trainee. |

---

## 8. College Viva / Examiner Q&A Guide

### Q1: Why did you choose Django for this project?
**Answer:** Django follows the Model-View-Template (MVT) pattern and the "batteries-included" philosophy. It provides robust built-in authentication, an Object-Relational Mapper (ORM) that prevents SQL injections, CSRF protection, and a production-grade admin panel. Combined with Django REST Framework, we can power both server-rendered web views and RESTful JSON APIs from a single backend.

### Q2: How did you implement Role-Based Access Control (RBAC)?
**Answer:** We extended Django's `AbstractUser` model in `accounts.User` by adding a `role` field (`ADMIN`, `EMPLOYER`, `CANDIDATE`). In views and API endpoints, we implemented role-checking decorators (`@login_required`), model properties (`is_candidate`, `is_employer`, `is_platform_admin`), and DRF custom permissions (`IsEmployerOrReadOnly`).

### Q3: How do you prevent a candidate from applying multiple times to the same job?
**Answer:** At the database level, the `Application` model specifies `unique_together = ('job', 'candidate')`. In the views and DRF serializers, we query `Application.objects.filter(job=job, candidate=request.user).exists()` before creating an entry and return an informative message if already submitted.

### Q4: How is resume security handled?
**Answer:** Resumes are validated both in Django forms and model validation:
1. File extension validation restricts uploads strictly to `.pdf`.
2. File size validation enforces a strict 5MB limit to prevent server disk saturation.
3. Resumes are stored under Django's `MEDIA_ROOT/resumes/` and only linked to authenticated candidates and the corresponding employer.

### Q5: How does the notification system work?
**Answer:** We have an asynchronous-ready `Notification` model with foreign key to recipient. Whenever an employer modifies an applicant's status (e.g. from `PENDING` to `SHORTLISTED` or `SELECTED`), a post-save signal or view action automatically creates a `Notification` object for the candidate. Similarly, when a candidate applies, the hiring manager receives an alert. The frontend navbar displays an unread count badge updated dynamically.

---

## 9. Deliverables Verification Checklist

- [x] Complete Responsive Frontend (HTML5, CSS3, JavaScript, Bootstrap 5)
- [x] Django Backend with clean app separation (`accounts`, `jobs`, `notifications`, `api`)
- [x] Connected Database Schema with constraints and ForeignKeys
- [x] Functional REST APIs with DRF serializers and ViewSets
- [x] Candidate Module (Register, Profile, Education, Skills, PDF Resume, Apply, Status Tracker, Withdraw)
- [x] Employer Module (Register, Company Profile, Post Job, Edit/Delete, View Applicants, Status Update)
- [x] Job Management (Filters: Title, Location, Skills, Type, Experience, Salary)
- [x] Application Management with Duplicate Prevention
- [x] Admin Dashboard with Chart.js visual statistics
- [x] In-app Notification System
- [x] Seed data command (`python manage.py seed_data`)
- [x] Unit and Integration Automated Tests (`python manage.py test`) passing with OK
- [x] Viva Documentation & README.md

---
&copy; 2026 CareerConnect &bull; Computer Science & Engineering Final Year Capstone Project

