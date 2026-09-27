# InternMatch - Database Design

## 1. Introduction

The InternMatch system requires a relational database to store and manage information related to users, student profiles, recruiter profiles, resumes, internships, applications, and skills.

The database will provide persistent storage for the application and maintain relationships between students, recruiters, internships, and applications.

The initial development version of InternMatch will use SQLite as the database system, with SQLAlchemy used as the Object-Relational Mapping (ORM) layer.

The database is designed to support the major operations of the system while maintaining data consistency and reducing unnecessary duplication.


## 2. Database Entities

The InternMatch database will contain the following major entities:

### 2.1 User

Stores the basic account and authentication information of all registered users.

A user can have one of the following roles:

- Student
- Recruiter
- Administrator

### 2.2 Student Profile

Stores additional information about a student, including education, skills, experience, projects, and certifications Each student profile is associated with one user account.

### 2.3 Recruiter Profile

Stores information about a recruiter and the organization they represent. Each recruiter profile is associated with one user account.

### 2.4 Resume

Stores information about resumes uploaded by students, including the file location and extracted text. A student can have one active resume in the initial version of the system.

### 2.5 Internship

Stores information about internship opportunities created by recruiters. Each internship belongs to one recruiter.

### 2.6 Application

Stores information about a student's application to an internship. An application connects one student with one internship and stores information such as application date, status, and match score.

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


## 3. Entity Attributes

The following attributes will be used for the major entities in the InternMatch database.

### 3.1 User

| Attribute | Description |
|---|---|
| user_id | Unique identifier for the user |
| name | Full name of the user |
| email | Unique email address used for authentication |
| password_hash | Hashed user password |
| role | Role of the user: Student, Recruiter, or Administrator |
| created_at | Date and time when the account was created |



### 3.2 Student Profile

| Attribute | Description |
|---|---|
| student_id | Unique identifier for the student profile |
| user_id | Reference to the associated user account |
| phone | Student's contact number |
| education | Educational background |
| profile_summary | Short description of the student |
| experience | Work or internship experience |
| projects | Project information |
| certifications | Certification information |
| updated_at | Date and time when the profile was last updated |



### 3.3 Recruiter Profile

| Attribute | Description |
|---|---|
| recruiter_id | Unique identifier for the recruiter profile |
| user_id | Reference to the associated user account |
| company_name | Name of the organization represented by the recruiter |
| company_description | Description of the organization |
| contact_phone | Recruiter's contact number |
| updated_at | Date and time when the profile was last updated |



### 3.4 Resume

| Attribute | Description |
|---|---|
| resume_id | Unique identifier for the resume |
| student_id | Reference to the student who uploaded the resume |
| file_name | Name of the uploaded resume file |
| file_path | Location where the resume is stored |
| extracted_text | Text extracted from the resume |
| uploaded_at | Date and time when the resume was uploaded |



### 3.5 Internship

| Attribute | Description |
|---|---|
| internship_id | Unique identifier for the internship |
| recruiter_id | Reference to the recruiter who created the internship |
| title | Internship title |
| company_name | Name of the company offering the internship |
| description | Detailed internship description |
| location | Internship location |
| work_mode | On-site, hybrid, or remote |
| duration | Duration of the internship |
| stipend | Stipend offered |
| eligibility | Eligibility requirements |
| required_skills | Skills required for the internship |
| deadline | Application deadline |
| status | Current internship status |
| created_at | Date and time when the internship was created |



### 3.6 Application

| Attribute | Description |
|---|---|
| application_id | Unique identifier for the application |
| student_id | Reference to the student who applied |
| internship_id | Reference to the internship |
| resume_id | Resume submitted with the application |
| application_date | Date and time when the application was submitted |
| status | Current application status |
| match_score | Resume-internship compatibility score |
| created_at | Date and time when the application record was created |
| updated_at | Date and time when the application was last updated |



### 3.7 Skill

| Attribute | Description |
|---|---|
| skill_id | Unique identifier for the skill |
| skill_name | Name of the skill |


