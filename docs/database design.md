# InternMatch - Database Design

## 1. Introduction

The InternMatch system uses a relational database to store and manage information related to users, student profiles, recruiter profiles, resumes, internships, applications, skills, application resume snapshots, and administrative moderation activities.

The database provides persistent storage for the application and maintains relationships between students, recruiters, internships, applications, and their associated information.

InternMatch uses SQLAlchemy as its Object-Relational Mapping (ORM) layer and Flask-Migrate with Alembic for database schema migrations.

The application supports two database configurations:

- SQLite for local development.
- PostgreSQL for the production deployment.

Resume documents are stored separately from relational database records. The production application uses a private Supabase Storage bucket for resume objects, while database records maintain the corresponding file paths and metadata.

The database is designed to maintain data consistency, preserve application history, support role-specific functionality, and reduce unnecessary data duplication.

## 2. Database Entities

The InternMatch database contains the following major entities.

### 2.1 User

Stores basic account and authentication information for all registered users.

A user can have one of the following roles:

- Student
- Recruiter
- Administrator

Student and recruiter accounts are created through public registration. Administrator accounts are provisioned separately.

The User entity maintains the common account information shared by all user types.

### 2.2 Student Profile

Stores additional information about a student, including education, skills, experience, projects, certifications, and profile summary.

Each student profile is associated with one user account.

A student profile can have one current resume and multiple internship applications.

### 2.3 Recruiter Profile

Stores information about a recruiter and the organization they represent.

Each recruiter profile is associated with one user account.

A recruiter profile can manage multiple internship listings.

### 2.4 Resume

Stores information about resumes uploaded by students, including the original filename, storage path, and extracted text.

Each student can have one current resume record.

The actual document is stored using the configured storage backend. In production, resume documents are maintained in Supabase Storage.

### 2.5 Internship

Stores information about internship opportunities created by recruiters.

Each internship belongs to one recruiter and may receive multiple applications.

Internships also maintain their required skills through a many-to-many relationship with the Skill entity.

### 2.6 Application

Stores information about a student's application to an internship.

An application connects one student with one internship and stores information such as:

- Application date.
- Application status.
- Associated resume record, when available.
- Match score field.
- Creation and update timestamps.

The database prevents duplicate applications from the same student to the same internship through a composite uniqueness constraint.

An application may also have one associated application resume snapshot.

### 2.7 Skill

Stores individual skills that can be associated with students and internship requirements.

Examples include:

- Python
- Java
- SQL
- Git
- React
- Machine Learning
- HTML
- CSS

Skills are associated with students and internships using separate many-to-many junction tables.

### 2.8 Application Resume Snapshot

Stores an independent copy of the resume associated with a submitted application.

Each application can have zero or one associated resume snapshot.

The snapshot maintains:

- Application ID.
- Original filename.
- Independent storage path.
- Creation timestamp.

The snapshot is stored separately from the student's current Resume record.

This allows the original resume associated with an application to remain accessible even when the student replaces their current resume.

### 2.9 Moderation Action

Stores records of supported administrative actions performed within the application.

The entity maintains information such as:

- Administrator identity.
- Action type.
- Target user or internship identifier.
- Target information snapshot.
- Previous value.
- New value.
- Action timestamp.

The moderation history is designed to preserve relevant historical information even when the associated user or internship record is subsequently removed.

### 2.10 Student Skills Junction Table

The `student_skills` table implements the many-to-many relationship between StudentProfile and Skill.

A student can have multiple skills, and a skill can be associated with multiple students.

### 2.11 Internship Skills Junction Table

The `internship_skills` table implements the many-to-many relationship between Internship and Skill.

An internship can require multiple skills, and the same skill can be required by multiple internships.

## 3. Entity Attributes

The following attributes describe the entities implemented in the InternMatch database.

### 3.1 User

| Attribute | Description |
|---|---|
| user_id | Unique identifier for the user; primary key |
| name | Full name of the user |
| email | Unique email address used for authentication |
| password_hash | Hashed user password |
| role | Role of the user: student, recruiter, or administrator |
| is_active | Indicates whether the account is active |
| session_version | Version used for validating login sessions |
| created_at | Date and time when the account was created |

The email column is unique and indexed.

Passwords are stored as password hashes rather than plaintext values.

### 3.2 Student Profile

| Attribute | Description |
|---|---|
| student_id | Unique identifier for the student profile; primary key |
| user_id | Reference to the associated user account; unique foreign key |
| phone | Student's contact number |
| education | Educational background |
| profile_summary | Short description of the student |
| experience | Work or internship experience |
| projects | Project information |
| certifications | Certification information |
| updated_at | Date and time when the profile was last updated |

The `user_id` column references `users.user_id`.

The unique constraint ensures that one user account cannot have multiple student profiles.

### 3.3 Recruiter Profile

| Attribute | Description |
|---|---|
| recruiter_id | Unique identifier for the recruiter profile; primary key |
| user_id | Reference to the associated user account; unique foreign key |
| company_name | Name of the organization represented by the recruiter |
| company_description | Description of the organization |
| contact_phone | Recruiter's contact number |
| updated_at | Date and time when the profile was last updated |

The `user_id` column references `users.user_id`.

The unique constraint ensures that one user account cannot have multiple recruiter profiles.

### 3.4 Resume

| Attribute | Description |
|---|---|
| resume_id | Unique identifier for the resume; primary key |
| student_id | Reference to the student who uploaded the resume; unique foreign key |
| file_name | Name of the uploaded resume file |
| file_path | Location or storage reference of the resume |
| extracted_text | Text extracted from the resume |
| uploaded_at | Date and time when the resume was uploaded |

The `student_id` column references `student_profiles.student_id`.

The unique constraint ensures that each student has at most one current Resume record.

The `file_path` column stores the location of the document. When Supabase Storage is used, the path contains the `supabase://` prefix followed by the object path.

The actual document contents are maintained in the storage backend rather than stored directly in this table.

### 3.5 Internship

| Attribute | Description |
|---|---|
| internship_id | Unique identifier for the internship; primary key |
| recruiter_id | Reference to the recruiter who created the internship |
| title | Internship title |
| company_name | Name of the company offering the internship |
| description | Detailed internship description |
| location | Internship location |
| work_mode | On-site, hybrid, or remote |
| duration | Duration of the internship |
| stipend | Stipend offered |
| eligibility | Eligibility requirements |
| required_skills | Text representation of required skills |
| deadline | Application deadline |
| status | Current internship status |
| created_at | Date and time when the internship was created |

The `recruiter_id` column references `recruiter_profiles.recruiter_id`.

The internship is associated with structured skill requirements through the `internship_skills` junction table.

### 3.6 Application

| Attribute | Description |
|---|---|
| application_id | Unique identifier for the application; primary key |
| student_id | Reference to the student who applied |
| internship_id | Reference to the internship |
| resume_id | Optional reference to the student's current Resume record |
| application_date | Date and time when the application was submitted |
| status | Current application status |
| match_score | Nullable match-score field |
| created_at | Date and time when the application record was created |
| updated_at | Date and time when the application was last updated |

Foreign key relationships:

- `student_id` references `student_profiles.student_id`.
- `internship_id` references `internships.internship_id`.
- `resume_id` references `resumes.resume_id` and is nullable.

The database enforces the following composite uniqueness constraint:

`uq_application_student_internship`

This prevents a student from applying more than once to the same internship.

The application status is maintained separately from the internship status.

The matching service currently calculates applicant match scores dynamically. The nullable `match_score` column is part of the database model, but it should not be interpreted as evidence that every dynamically calculated result is automatically persisted.

### 3.7 Skill

| Attribute | Description |
|---|---|
| skill_id | Unique identifier for the skill; primary key |
| skill_name | Name of the skill; unique |

The `skill_name` column is unique to prevent duplicate skill records.

The Skill entity participates in two many-to-many relationships:

- StudentProfile through `student_skills`.
- Internship through `internship_skills`.

### 3.8 Application Resume Snapshot

| Attribute | Description |
|---|---|
| application_id | Reference to the associated application; primary key and foreign key |
| file_name | Original filename of the submitted resume |
| file_path | Independent storage path of the application resume |
| created_at | Date and time when the snapshot was created |

The `application_id` column references `applications.application_id`.

It is both the primary key and foreign key of this table.

This design ensures a maximum of one snapshot per application.

The snapshot's file path is independent of the student's current Resume file path.

The document itself is stored through the configured storage backend. In production, snapshot documents are stored in Supabase Storage.

The application workflow preserves existing snapshots when the student replaces their current resume.

### 3.9 Moderation Action

| Attribute | Description |
|---|---|
| action_id | Unique identifier for the moderation action; primary key |
| admin_user_id | Optional reference to the administrator user account |
| admin_name | Administrator's name recorded at the time of the action |
| admin_email | Administrator's email recorded at the time of the action |
| action_type | Type of administrative action |
| target_user_id | Historical identifier of the affected user, when applicable |
| target_internship_id | Historical identifier of the affected internship, when applicable |
| target_snapshot | JSON-serialized identifying information about the target |
| old_value | Previous value, where applicable |
| new_value | Updated value, where applicable |
| created_at | Date and time when the action was recorded |

The `admin_user_id` column references `users.user_id` and uses `ON DELETE SET NULL`.

This allows moderation history to remain when an administrator account is deleted.

The target user and internship identifiers are deliberately not foreign keys. Their historical references are retained even when the original target records are removed.

A check constraint ensures that exactly one of `target_user_id` or `target_internship_id` is populated for a moderation record.

The `created_at` column is indexed for efficient retrieval of recent administrative actions.

## 4. Junction Tables

### 4.1 Student Skills

The `student_skills` junction table maintains the many-to-many relationship between students and skills.

| Attribute | Description |
|---|---|
| student_id | Foreign key referencing `student_profiles.student_id` |
| skill_id | Foreign key referencing `skills.skill_id` |

Both columns form a composite primary key.

This prevents the same skill from being associated with the same student more than once.

### 4.2 Internship Skills

The `internship_skills` junction table maintains the many-to-many relationship between internships and skills.

| Attribute | Description |
|---|---|
| internship_id | Foreign key referencing `internships.internship_id` |
| skill_id | Foreign key referencing `skills.skill_id` |

Both columns form a composite primary key.

This prevents duplicate skill associations for an internship.

## 5. Database Relationships

The database maintains the following relationships.

### 5.1 User and Student Profile

- One User can have zero or one StudentProfile.
- Each StudentProfile belongs to exactly one User.
- The relationship is implemented using a unique foreign key on `student_profiles.user_id`.

### 5.2 User and Recruiter Profile

- One User can have zero or one RecruiterProfile.
- Each RecruiterProfile belongs to exactly one User.
- The relationship is implemented using a unique foreign key on `recruiter_profiles.user_id`.

### 5.3 Student Profile and Resume

- One StudentProfile can have zero or one current Resume.
- Each Resume belongs to exactly one StudentProfile.
- The unique constraint on `resumes.student_id` enforces this relationship.

### 5.4 Recruiter Profile and Internship

- One RecruiterProfile can manage multiple Internships.
- Each Internship belongs to one RecruiterProfile.

### 5.5 Student Profile and Application

- One StudentProfile can submit multiple Applications.
- Each Application belongs to one StudentProfile.

### 5.6 Internship and Application

- One Internship can receive multiple Applications.
- Each Application belongs to one Internship.

Together, the StudentProfile, Internship, and Application relationships represent the many-to-many association between students and internships through application records.

### 5.7 Student Profile and Skill

- One StudentProfile can have multiple Skills.
- One Skill can be associated with multiple StudentProfiles.
- The `student_skills` junction table implements this relationship.

### 5.8 Internship and Skill

- One Internship can require multiple Skills.
- One Skill can be required by multiple Internships.
- The `internship_skills` junction table implements this relationship.

### 5.9 Application and Resume

- One Resume may be referenced by multiple Applications.
- Each Application may reference zero or one Resume through its nullable `resume_id` column.

This relationship is retained for existing application records and compatibility with the current Resume model.

### 5.10 Application and Application Resume Snapshot

- One Application can have zero or one ApplicationResumeSnapshot.
- Each ApplicationResumeSnapshot belongs to exactly one Application.
- The `application_id` column in `application_resume_snapshots` is both its primary key and foreign key.

The foreign key uses `ON DELETE CASCADE`.

The SQLAlchemy relationship also defines `all, delete-orphan` cascade behaviour.

This supports cleanup of the corresponding snapshot record when its parent application is deleted through the ORM.

### 5.11 User and Moderation Action

- One User may be referenced as the administrator for multiple ModerationAction records.
- Each ModerationAction may reference zero or one administrator account.
- If the administrator account is deleted, `admin_user_id` becomes NULL.
- The recorded administrator name and email remain available for historical identification.

The target user and internship identifiers in ModerationAction are historical references rather than foreign-key relationships.

## 6. Entity Relationship Diagram

The following diagram represents the relationships implemented in the current database schema.

```mermaid
erDiagram

    USER ||--o| STUDENT_PROFILE : has
    USER ||--o| RECRUITER_PROFILE : has

    STUDENT_PROFILE ||--o| RESUME : maintains

    RECRUITER_PROFILE ||--o{ INTERNSHIP : manages

    STUDENT_PROFILE ||--o{ APPLICATION : submits
    INTERNSHIP ||--o{ APPLICATION : receives

    RESUME o|--o{ APPLICATION : referenced_by

    APPLICATION ||--o| APPLICATION_RESUME_SNAPSHOT : preserves

    STUDENT_PROFILE ||--o{ STUDENT_SKILLS : has
    SKILL ||--o{ STUDENT_SKILLS : associated_with

    INTERNSHIP ||--o{ INTERNSHIP_SKILLS : requires
    SKILL ||--o{ INTERNSHIP_SKILLS : associated_with

    USER o|--o{ MODERATION_ACTION : performs

    USER {
        int user_id PK
        string name
        string email UK
        string password_hash
        string role
        boolean is_active
        int session_version
        datetime created_at
    }

    STUDENT_PROFILE {
        int student_id PK
        int user_id FK UK
        string phone
        text education
        text profile_summary
        text experience
        text projects
        text certifications
        datetime updated_at
    }

    RECRUITER_PROFILE {
        int recruiter_id PK
        int user_id FK UK
        string company_name
        text company_description
        string contact_phone
        datetime updated_at
    }

    RESUME {
        int resume_id PK
        int student_id FK UK
        string file_name
        string file_path
        text extracted_text
        datetime uploaded_at
    }

    INTERNSHIP {
        int internship_id PK
        int recruiter_id FK
        string title
        string company_name
        text description
        string location
        string work_mode
        string duration
        string stipend
        text eligibility
        text required_skills
        date deadline
        string status
        datetime created_at
    }

    APPLICATION {
        int application_id PK
        int student_id FK
        int internship_id FK
        int resume_id FK
        datetime application_date
        string status
        float match_score
        datetime created_at
        datetime updated_at
    }

    SKILL {
        int skill_id PK
        string skill_name UK
    }

    STUDENT_SKILLS {
        int student_id PK, FK
        int skill_id PK, FK
    }

    INTERNSHIP_SKILLS {
        int internship_id PK, FK
        int skill_id PK, FK
    }

    APPLICATION_RESUME_SNAPSHOT {
        int application_id PK, FK
        string file_name
        string file_path
        datetime created_at
    }

    MODERATION_ACTION {
        int action_id PK
        int admin_user_id FK
        string admin_name
        string admin_email
        string action_type
        int target_user_id
        int target_internship_id
        text target_snapshot
        text old_value
        text new_value
        datetime created_at
    }
```

The diagram represents the database structure and cardinalities rather than application-level authorization or all ORM cascade behaviours.

## 7. Data Integrity and Constraints

The database uses primary keys, foreign keys, unique constraints, and check constraints to maintain data integrity.

### 7.1 Primary Keys

Every major entity has a primary key that uniquely identifies each record.

The junction tables use composite primary keys to prevent duplicate associations.

The ApplicationResumeSnapshot entity uses `application_id` as its primary key.

### 7.2 Foreign Keys

Foreign keys maintain relationships between:

- StudentProfile and User.
- RecruiterProfile and User.
- Resume and StudentProfile.
- Internship and RecruiterProfile.
- Application and StudentProfile.
- Application and Internship.
- Application and Resume.
- ApplicationResumeSnapshot and Application.
- StudentSkills and StudentProfile/Skill.
- InternshipSkills and Internship/Skill.
- ModerationAction and User.

### 7.3 Unique Constraints

The following unique constraints are implemented:

- Unique User email.
- Unique StudentProfile user reference.
- Unique RecruiterProfile user reference.
- Unique Resume student reference.
- Unique Skill name.
- Unique student-internship application combination.
- Unique application reference in ApplicationResumeSnapshot through its primary key.

### 7.4 Check Constraints

The ModerationAction table includes a check constraint ensuring that exactly one target is specified:

- A target user identifier; or
- A target internship identifier.

Both cannot be NULL or populated simultaneously.

### 7.5 Cascade Behaviour

The application uses ORM relationships and database foreign-key actions to manage related records.

Examples include:

- Deleting a User through the ORM cascades deletion to its associated student or recruiter profile.
- Student profile deletion through its ORM relationship cascades to its associated current resume and applications.
- Recruiter profile deletion through its ORM relationship cascades to managed internships.
- Application deletion through the ORM cascades to its application resume snapshot.
- Database deletion of an Application also triggers the snapshot foreign-key `ON DELETE CASCADE`.
- Deleting a referenced administrator User sets `ModerationAction.admin_user_id` to NULL.

Application-level deletion safeguards protect records with application history. Recruiter and administrator workflows restrict deletion of internships that already have applications, while student accounts with application history are protected from deletion.

## 8. Resume Storage Architecture

Resume documents are stored separately from relational database records.

The application implements a storage abstraction supporting:

1. Local filesystem storage.
2. Supabase Storage.

### 8.1 Local Development Storage

During local development, resume documents can be stored on the local filesystem.

The configured upload directory is used to organize the stored files.

### 8.2 Production Storage

The production application uses Supabase Storage.

Resume objects are stored in a private bucket configured through environment variables.

The storage implementation generates unique object paths using the student identifier and a UUID-based filename.

The database stores a storage reference rather than the file's binary contents.

### 8.3 Current Resume Replacement

When a student replaces their current resume:

1. The uploaded document is validated.
2. Its text is extracted.
3. A new resume object is stored.
4. The existing Resume record is updated to reference the new object.
5. The database transaction is committed.
6. The previous current-resume object is scheduled for cleanup.

Cleanup failure is logged so that the issue can be investigated without silently treating the deletion as successful.

### 8.4 Application Resume Snapshots

When a student submits an application and has a current resume, the application workflow creates an independent copy of that document.

The copy receives its own UUID-based object path and is stored using the configured storage backend.

The corresponding `ApplicationResumeSnapshot` record stores the new filename and storage path.

This ensures that:

- The student's current resume and the application's snapshot are separate objects.
- Replacing the current resume does not overwrite the original application snapshot.
- Recruiters can retrieve the original submitted resume.
- New applications can use a subsequently updated resume.

Resume retrieval is performed through the application after checking the user's role and, for recruiter access, ownership of the relevant internship.

## 9. Database Implementation and Migration Management

InternMatch uses SQLAlchemy for database operations and Flask-Migrate/Alembic for schema migration management.

The application supports SQLite locally and PostgreSQL in production.

Database connection configuration is obtained through the `DATABASE_URL` environment variable when provided.

When no hosted database URL is configured, the application uses its local SQLite database.

Database schema changes are maintained as version-controlled migration scripts.

### Application Resume Snapshot Migration

The application resume snapshot table was introduced through the following Alembic migration:

| Attribute | Value |
|---|---|
| Revision ID | `2332dec4fb2a` |
| Parent Revision | `65afd14f62b4` |
| New Table | `application_resume_snapshots` |
| Primary Key | `application_id` |
| Foreign Key | `applications.application_id` |
| Delete Behaviour | `ON DELETE CASCADE` |

The migration creates the snapshot table with the filename, storage path, and creation timestamp.

The production database was verified on 26 November 2026, and its current Alembic revision was confirmed as `2332dec4fb2a`.

## 10. Conclusion

The InternMatch database is designed to support the complete internship application workflow, including user management, internship management, resume processing, application submission, matching, and administrative monitoring.

The database maintains relationships between students, recruiters, internships, applications, and skills through relational constraints and junction tables.

The application resume snapshot mechanism extends the original database design by preserving the resume associated with each submitted application independently of the student's current resume.

The system uses PostgreSQL in production, SQLite for local development, and private Supabase Storage for production resume objects.

This database design reflects the current implementation and provides a foundation for future improvements and maintenance of the InternMatch system.