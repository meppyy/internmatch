# InternMatch

## Internship Portal & Explainable Resume Ranking System

InternMatch is a web-based internship management and candidate evaluation platform designed to connect students with internship opportunities while helping recruiters evaluate applicants through resume-based skill matching.

The platform provides separate workflows for students, recruiters, and administrators. Students can manage their profiles, upload resumes, discover internships, and submit applications. Recruiters can manage internship listings, review applicants, access submitted resumes, and rank candidates using an explainable, rule-based matching system.

InternMatch also maintains independent resume snapshots for submitted applications, preserving the resume associated with an application even when a student subsequently updates their current resume.

## 1. Problem Statement

Students often have to search across multiple platforms to discover suitable internship opportunities. At the same time, recruiters may receive numerous applications and need an efficient way to identify candidates whose skills align with the requirements of a particular internship.

InternMatch aims to address both problems by providing a centralized internship portal combined with resume management, application tracking, and explainable candidate ranking.

The system compares the skills associated with student profiles against internship requirements and generates match scores to help recruiters assess candidate compatibility.

## 2. Objectives

The primary objectives of InternMatch are:

- Provide students with a centralized platform for discovering internships.
- Allow students to register and manage their professional profiles.
- Enable resume uploading, validation, text extraction, and storage.
- Allow students to search and filter internship opportunities.
- Facilitate internship applications and application-status tracking.
- Preserve the resume associated with each submitted application.
- Allow recruiters to create and manage internship listings.
- Provide recruiters with access to applicants and their submitted resumes.
- Compare student skills with internship requirements.
- Generate explainable match scores.
- Rank applicants according to their resume-internship compatibility.
- Provide administrators with tools for user and internship management.

## 3. Main Users

### Student

Students can:

- Register and log in.
- Create and manage their profiles.
- Add education, skills, projects, experience, and certifications.
- Upload PDF and DOCX resumes.
- Replace their currently uploaded resume.
- Browse available internships.
- Search and filter internship opportunities.
- View internship details and matching information.
- Apply for internships.
- Track submitted applications and their statuses.
- View or download their current resume.

### Recruiter

Recruiters can:

- Register and log in.
- Create internship listings.
- Specify internship descriptions and required skills.
- Edit and manage their own listings.
- View applicants for their internships.
- Access applicant profiles and submitted resumes.
- View candidate match scores and matching explanations.
- Sort and rank applicants.
- Update application statuses.

### Administrator

Administrators can:

- Access an administrative dashboard.
- Monitor users, students, recruiters, internships, and applications.
- View and manage user accounts.
- Enable or disable user accounts.
- Manage internship listings.
- Monitor administrative actions and moderation activity.

Administrative operations include safeguards designed to preserve application history and prevent removal of the last active administrator.

## 4. Core Features

### 4.1 Internship Portal

- User registration and role-based authentication.
- Student and recruiter profiles.
- Internship creation and management.
- Internship browsing and searching.
- Internship filtering.
- Internship detail pages.
- Student applications.
- Application history and status tracking.
- Recruiter applicant management.

### 4.2 Resume Management and Processing

- PDF and DOCX resume uploading.
- File-type and document validation.
- Maximum upload size of 10 MB.
- Resume text extraction using Python libraries.
- Detection of relevant skills from extracted resume text.
- Replacement of existing resumes.
- Private cloud-based resume storage through Supabase Storage in production.
- Independent resume snapshots for submitted applications.

**Application Resume Snapshots**

When a student submits an application, InternMatch creates an independent copy of the student's current resume and associates it with that application.

Consequently:
- An application retains the resume submitted at the time of application.
- Replacing the student's current resume does not overwrite existing application snapshots.
- Recruiters can continue accessing the original submitted resume.
- New applications can use the student's updated resume.
- Legacy applications without snapshots retain a fallback to the existing Application.resume relationship. Original resume preservation is guaranteed for applications with independent snapshots.

### 4.3 Resume Matching and Candidate Ranking

InternMatch uses a rule-based matching approach to compare student skills with internship requirements.

The system provides:

- - Skill matching based on extracted and maintained student skills.
- Case-insensitive skill comparison.
- Match percentage calculation.
- Identification of matched skills.
- Identification of missing skills.
- Human-readable matching explanations.
- Recruiter-side applicant sorting and ranking.

The matching system is designed to provide interpretable results rather than relying on an opaque machine-learning prediction.

### 4.4 Administration and Access Control

- Role-based access to student, recruiter, and administrator functionality.
- Recruiter ownership verification for internship and applicant access.
- Protected application-resume access.
- User account management.
- Internship moderation.
- Administrative action recording.

## 5. Technology Stack

| Component | Technology |
|---|---|
| Frontend | HTML, CSS, JavaScript |
| Backend | Python, Flask |
| ORM | Flask-SQLAlchemy, SQLAlchemy |
| Production Database | PostgreSQL |
| Local Database Fallback | SQLite |
| Database Migrations | Flask-Migrate, Alembic |
| Resume Parsing | pypdf, python-docx |
| Skill Extraction | Python |
| Matching and Ranking | Python, rule-based skill matching |
| Resume Object Storage | Supabase Storage |
| Production Hosting | Render |
| Application Server | Gunicorn |
| Testing | pytest |
| Version Control | Git |
| Repository Hosting | GitHub |

## 6. System Workflow

### Student Workflow

```text
Register / Login
       |
       v
Create Student Profile
       |
       v
Add Skills and Information
       |
       v
Upload Resume
       |
       v
Resume Validation
       |
       v
Resume Text Extraction
       |
       v
Browse / Search Internships
       |
       v
View Internship Details
       |
       v
Apply for Internship
       |
       v
Create Application Resume Snapshot
       |
       v
Track Application Status
```

### Recruiter Workflow

```text
Register / Login
       |
       v
Create Internship
       |
       v
Define Required Skills
       |
       v
Receive Applications
       |
       v
View Applicants
       |
       v
Access Application Resume Snapshots
       |
       v
View Match Scores and Explanations
       |
       v
Rank Applicants
       |
       v
Update Application Status
```

### Administrator Workflow

```text
Administrator Login
       |
       v
Admin Dashboard
       |
       v
Monitor Users and Internships
       |
       v
Manage User Accounts
       |
       v
Moderate Internship Listings
       |
       v
Monitor Applications
       |
       v
Record Administrative Actions
```

## 7. Resume Processing and Matching Pipeline

The implemented resume processing and matching workflow follows this structure:

```text
Student Resume (PDF / DOCX)
             |
             v
       File Validation
             |
             v
      Text Extraction
             |
             v
      Skill Extraction
             |
             v
    Student Skill Profile
             |
             |
Internship Requirements
             |
             v
       Skill Comparison
             |
             v
       Match Calculation
             |
             v
      Match Percentage
             |
             v
     Matched / Missing Skills
             |
             v
    Explanation Generation
             |
             v
       Applicant Ranking
```

### Matching Calculation

The system calculates compatibility using the proportion of required internship skills matched by the student's profile.

**Match Percentage = (Number of Matched Required Skills / Total Required Skills) × 100**

The matching implementation:

- Uses the internship's structured skill relationships as the primary source of requirements.
- Supports the existing comma-separated required-skills field as a fallback.
- Normalizes skill comparisons using case-insensitive matching.
- Identifies matched and missing skills.
- Generates explanations based on actual matching results.
- Supports recruiter-side sorting by match score.

When no required skills are specified, the system does not generate an artificial percentage.

This is a rule-based matching system. It does not claim to use a trained machine-learning model or semantic similarity prediction.

## 8. Database and Storage Architecture

### Database

InternMatch uses SQLAlchemy for database management and Flask-Migrate/Alembic for schema migrations.

The application supports:

- SQLite as the default local development database.
- PostgreSQL through the `DATABASE_URL` environment variable.

The production deployment uses PostgreSQL.

### Resume Storage

Resume files are managed through a storage abstraction that supports local filesystem storage and Supabase Storage.

In production, InternMatch uses a private Supabase Storage bucket.

The storage implementation supports:

- Resume uploads.
- File retrieval.
- Independent application resume copies.
- Resume replacement.
- Backend-aware file deletion.

Database records store the resume's file path and metadata, while the actual resume documents are stored as objects in the configured storage backend.

### Application Resume Snapshots

The `application_resume_snapshots` table maintains the independent resume associated with a submitted application.

Each application can have one associated resume snapshot.

The snapshot references the application through its primary-key relationship and preserves the submitted filename and storage path.

## 9. Local Setup and Installation

### Prerequisites

- Python
- Git
- pip

### Clone the Repository

```bash
git clone https://github.com/meppyy/internmatch.git
cd internmatch
```

### Create a Virtual Environment

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

The following environment variables are supported:

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Flask application secret key; required in production |
| `APP_ENV` | Application environment (`development` or `production`) |
| `DATABASE_URL` | Database connection URL |
| `UPLOAD_FOLDER` | Local upload directory |
| `STORAGE_BACKEND` | Resume storage backend (`local` or `supabase`) |
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_SECRET_KEY` | Supabase server-side secret key |
| `SUPABASE_STORAGE_BUCKET` | Supabase Storage bucket name |

When `DATABASE_URL` is not configured, the application defaults to a local SQLite database.

The default local storage backend is `local`. Supabase credentials are required when `STORAGE_BACKEND=supabase`.

Never commit production secrets or expose Supabase secret keys in source code or documentation.

### Apply Database Migrations

```bash
flask --app run:app db upgrade
```

### Run the Application

```bash
python run.py
```

The development application will be accessible at:

```text
http://127.0.0.1:5000
```

## 10. Testing

InternMatch uses pytest for automated testing.

The test suite covers areas including:

- Student registration and authentication.
- Student profile management.
- Resume uploads and validation.
- Resume replacement.
- Supabase storage integration through mocked storage tests.
- Internship management.
- Application submission.
- Application resume snapshots.
- Recruiter access and ownership.
- Matching and ranking.
- Administrative functionality.

Run the complete test suite using:

```bash
pytest -q
```

Automated local test results and manual production smoke-test results should be recorded separately.

## 11. Deployment

InternMatch is deployed through Render and uses a PostgreSQL database with Supabase Storage for resume objects.

### Production Configuration

The production environment uses:

- Render for application hosting.
- PostgreSQL for relational database persistence.
- Supabase Storage for resume object storage.
- A private Supabase Storage bucket.
- Gunicorn as the WSGI application server.
- Alembic migrations managed through Flask-Migrate.

### Production Verification

The following production checks were manually verified on 26 November 2026:

- Successful Render deployment of the `feature/web-deployment` branch.
- PostgreSQL connection and expected Alembic revision `2332dec4fb2a`.
- Student authentication and internship discovery.
- Resume PDF/DOCX upload and validation.
- Application submission.
- Recruiter applicant and resume access.
- Application resume snapshot preservation after current-resume replacement.
- Recruiter ownership-based access restrictions.
- Rule-based matching and applicant ranking.
- Administrative dashboard functionality.
- Supabase private bucket configuration.
- Independent storage and retrieval of current resumes and application snapshots.

These results represent manual production smoke tests, not a claim that automated pytest tests were executed against the production database.

## 12. Limitations and Future Improvements

The current implementation has several limitations and potential areas for improvement:

- Scanned PDF OCR is not currently implemented.
- Resume text extraction is limited to supported PDF and DOCX documents.
- The matching engine uses rule-based skill overlap rather than semantic similarity or a trained machine-learning model.
- Matching accuracy depends on the completeness and quality of extracted and manually maintained skill information.
- Advanced semantic resume analysis and expanded experience-based scoring remain potential future improvements.

Future development can explore more sophisticated resume analysis while retaining the transparency and explainability of the current matching system.

## 13. Project Status

InternMatch has progressed beyond its initial development phase and is deployed as a working web application.

The main student, recruiter, and administrator workflows have been implemented and manually verified in the production environment.

Major implemented components include:

- Role-based authentication and access control.
- Student and recruiter profile management.
- Internship creation, discovery, and management.
- Resume validation, processing, and storage.
- Independent application resume snapshots.
- Student application tracking.
- Recruiter applicant management.
- Rule-based matching and candidate ranking.
- Administrative user and internship management.
- PostgreSQL production database.
- Supabase-based resume object storage.
- Automated regression tests and project documentation.

The project will continue to be improved through additional testing, documentation refinement, production hardening, and future feature development.