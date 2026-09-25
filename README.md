# InternMatch

## Internship Portal & Resume Ranking System

InternMatch is a web-based platform designed to help students discover and apply for internship opportunities while providing recruiters with a structured system for evaluating and ranking candidates based on resume-job compatibility.


## 1. Problem Statement

Students often have to search across multiple platforms to find suitable internship opportunities. At the same time, recruiters may receive a large number of applications and need an efficient way to identify candidates whose skills and experience are relevant to a particular internship.

InternMatch aims to address both problems by combining an internship portal with a resume-based candidate ranking system.


## 2. Objectives

The main objectives of InternMatch are:

- Provide students with a centralized platform for discovering internships.
- Allow students to create and manage their profiles.
- Allow students to upload their resumes.
- Allow students to search and filter internship opportunities.
- Allow students to apply for internships and track their applications.
- Allow recruiters to create and manage internship listings.
- Allow recruiters to view internship applicants.
- Compare candidate resumes with internship requirements.
- Generate a match score for each candidate.
- Rank applicants based on their resume-internship compatibility.


## 3. Main Users

### Student

Students will be able to:

- Register and log in.
- Create and manage their profile.
- Add education, skills, projects, and experience.
- Upload a resume.
- Browse available internships.
- Search and filter internships.
- View internship details.
- Apply for internships.
- Track application status.
- View their resume match information.

### Recruiter

Recruiters will be able to:

- Register and log in.
- Create internship listings.
- Specify internship requirements.
- Edit and manage their listings.
- View applicants.
- View applicant resumes and profiles.
- View candidate match scores.
- Rank applicants.

### Administrator

Administrators will be able to:

- Manage users.
- Manage internship listings.
- Monitor applications.
- Remove inappropriate or invalid content.


## 4. Core Features

### Internship Portal

- User registration and authentication
- Student profiles
- Recruiter profiles
- Internship creation
- Internship browsing
- Internship search and filtering
- Internship applications
- Application status tracking

### Resume Management

- Resume upload
- Resume storage
- Resume text extraction
- Extraction of relevant resume information such as skills, education, projects, and experience

### Resume Ranking

- Comparison of resumes with internship requirements
- Skill and keyword matching
- Match score generation
- Applicant ranking
- Explanation of major matching factors


## 5. Technology Stack

| Component          | Technology            |
| ------------------ | --------------------- |
| Frontend           | HTML, CSS, JavaScript |
| Backend            | Python Flask          |
| Database           | SQLite                |
| Database ORM       | SQLAlchemy            |
| Resume Processing  | Python                |
| Matching / Ranking | Python, scikit-learn  |
| Testing            | pytest                |
| Version Control    | Git                   |
| Repository         | GitHub                |


## 6. System Workflow

### For Students 

```
Register / Login
       |
       v
Create Profile
       |
       v
Upload Resume
       |
       v
Browse Internships
       |
       v
View Internship
       |
       v
Apply
       |
       v
Track Application
```

### For Recruiters

```
Register / Login
       |
       v
Create Internship
       |
       v
Define Requirements
       |
       v
Receive Applications
       |
       v
View Applicants
       |
       v
Resume Matching
       |
       v
Candidate Ranking
```


## 7. Planned Processing Pipeline

The resume ranking component will compare information extracted from a student's resume with the requirements of a selected internship.

```
  Resume / Internship Description
            |
            v
       Text Extraction
            |
            v
        Preprocessing
            |
            v
      Skill / Keyword Extraction
            |
            v
       Feature Generation
            |
            v
     Similarity Calculation
            |
            v
        Match Score
            |
            v
     Applicant Ranking
```
The ranking system will be designed to provide an interpretable match score and information about the factors contributing to the score. The exact matching algorithm will be finalized and evaluated during implementation.

## 8. Documentation

Planned documentation includes:

- Software Requirements Specification (SRS)
- Functional and non-functional requirements
- System architecture
- Database design
- Use case diagrams
- Class diagrams
- Sequence diagrams
- Activity diagrams
- Data flow diagrams
- Testing documentation


## 9. Project Status

InternMatch is currently in the initial development phase. The project repository, Python environment, Flask application structure, and initial project documentation have been established. The next stages of development will focus on system design, database implementation, authentication, internship management, application management, resume processing, candidate matching, ranking, and testing.