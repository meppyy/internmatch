# InternMatch - Functional Requirements

## 1. Introduction

This document defines the functional requirements of the InternMatch system. Functional requirements describe the operations and services that the system must provide to its users.

The system has three primary user roles:

- Student
- Recruiter
- Administrator



## 2. User Registration

### FR-01 - User Registration

The system shall allow a new user to create an account.

The registration form shall collect:

- Full name
- Email address
- Password
- User role

The supported roles shall be:

- Student
- Recruiter

Administrator accounts shall be managed separately.



## 3. User Authentication

### FR-02 - User Login

The system shall allow registered users to log in using their email address and password.

### FR-03 - User Logout

The system shall allow authenticated users to securely log out of the system.

### FR-04 - Role-Based Access

The system shall provide different functionality based on the user's role. Students shall only be able to access student-specific functionality.

Recruiters shall only be able to access recruiter-specific functionality.

Administrative functionality shall only be accessible to administrators.



## 4. Student Profile Management

### FR-05 - Create Student Profile

The system shall allow students to create a profile after registration.

The profile shall contain:

- Full name
- Email address
- Phone number
- Education details
- Technical skills
- Work experience
- Projects
- Certifications
- Profile summary

### FR-06 - Update Student Profile

The system shall allow students to update their profile information.

### FR-07 - View Student Profile

The system shall allow students to view their complete profile information.



## 5. Resume Management

### FR-08 - Resume Upload

The system shall allow students to upload a resume. The system shall validate the uploaded file before storing it.

### FR-09 - Resume Replacement

The system shall allow students to replace their existing resume with an updated version.

### FR-10 - Resume Access

The system shall allow students to view or download their uploaded resume.

### FR-11 - Resume Processing

The system shall process the uploaded resume and extract relevant textual information for use by the resume matching system.


## 6. Internship Browsing

### FR-12 - View Internships

The system shall allow students to view available internship opportunities.

Each internship listing shall display relevant information such as:

- Internship title
- Company name
- Internship description
- Location
- Work mode
- Duration
- Stipend
- Required skills
- Eligibility criteria
- Application deadline

### FR-13 - Search Internships

The system shall allow students to search for internships using keywords such as internship title, company, or skill.

### FR-14 - Filter Internships

The system shall allow students to filter internship listings based on available attributes such as:

- Location
- Work mode
- Skills
- Stipend
- Duration

### FR-15 - View Internship Details

The system shall allow students to open an internship listing and view its complete details before applying.



## 7. Internship Creation and Management

### FR-16 - Create Internship

The system shall allow recruiters to create internship listings.

The recruiter shall provide information including:

- Internship title
- Company name
- Description
- Location
- Work mode
- Duration
- Stipend
- Required skills
- Eligibility criteria
- Application deadline

### FR-17 - Update Internship

The system shall allow recruiters to modify their existing internship listings.

### FR-18 - Delete Internship

The system shall allow recruiters to remove their internship listings.

### FR-19 - Manage Internship Status

The system shall allow recruiters to mark an internship as active or closed. Students shall not be able to submit new applications to a closed internship.

## 8. Internship Applications

### FR-20 - Apply for Internship

The system shall allow a registered student to apply for an active internship. The application shall use the student's profile and uploaded resume.

### FR-21 - Application Validation

Before submitting an application, the system shall verify that:

- The student is logged in.
- The internship is active.
- The application deadline has not passed.
- The student has not already applied for the same internship.

### FR-22 - Prevent Duplicate Applications

The system shall prevent a student from submitting more than one application for the same internship.

### FR-23 - Application Confirmation

After a successful application, the system shall provide confirmation to the student.

### FR-24 - View Submitted Applications

The system shall allow students to view a list of internships for which they have applied.

The list shall display information such as:

- Internship title
- Company
- Application date
- Application status
- Match score, when available

### FR-25 - Application Status

The system shall maintain the status of each internship application.

Possible application statuses shall include:

- Applied
- Under Review
- Shortlisted
- Rejected
- Selected

### FR-26 - Application Status Updates

The system shall allow authorized recruiters to update the status of applications submitted to their internships. The updated status shall be visible to the corresponding student.



## 9. Applicant Management

### FR-27 - View Applicants

The system shall allow recruiters to view the students who have applied to their internship listings.

For each applicant, the system shall display information such as:

- Student name
- Profile information
- Resume
- Application date
- Application status
- Match score, when available

### FR-28 - View Applicant Resume

The system shall allow recruiters to access the resume submitted by an applicant for evaluation.

### FR-29 - Review Applicant Profile

The system shall allow recruiters to view relevant student profile information while reviewing an application.

### FR-30 - Update Application Status

The system shall allow recruiters to update the status of an applicant's application.

### FR-31 - Applicant Ranking

The system shall provide recruiters with a ranked list of applicants for an internship based on the calculated resume-internship match score.

### FR-32 - Sort Applicants

The system shall allow recruiters to sort applicants based on relevant attributes such as:

- Match score
- Application date
- Application status

## 10. Resume Matching and Ranking

### FR-33 - Resume Text Extraction

The system shall extract readable text from uploaded resumes. The extracted text shall be used for further resume analysis.

### FR-34 - Resume Preprocessing

The system shall preprocess extracted resume text before matching.

Preprocessing may include:

- Converting text to a consistent case.
- Removing unnecessary characters.
- Removing irrelevant words.
- Normalizing text.

### FR-35 - Skill Extraction

The system shall identify relevant skills and keywords from a student's resume.

Examples may include:

- Programming languages
- Frameworks
- Libraries
- Databases
- Development tools
- Technical concepts

### FR-36 - Internship Requirement Processing

The system shall process the skills and requirements specified for an internship.

### FR-37 - Resume-Internship Matching

The system shall compare the information extracted from a student's resume with the requirements of an internship.

### FR-38 - Match Score Generation

The system shall generate a numerical match score representing the degree of compatibility between a student's resume and an internship. The score shall be presented in a consistent format, such as a percentage.

### FR-39 - Matched Skills

The system shall identify and display important skills or keywords that are present in both the student's resume and the internship requirements.

### FR-40 - Missing Skills

The system shall identify important internship requirements that are not found in the student's resume, where applicable.

### FR-41 - Match Explanation

The system shall provide information explaining the major factors contributing to the candidate's match score.

For example:

```
Match Score: 82%

Matched Skills:
- Python
- SQL
- Git
- Pandas

Missing Skills:
- Docker
```

### FR-42 - Candidate Ranking

The system shall rank applicants for an internship using their calculated match scores. Applicants with their respective scores shall be presented in a structured order for recruiter review.

### FR-43 - Ranking Update

The system shall update applicant rankings when relevant resume or internship requirement information changes.


## 11. Administrator Functions

### FR-44 - View Users

The system shall allow administrators to view registered users.

### FR-45 - Manage Users

The system shall allow administrators to manage user accounts.

Administrative actions may include:

- Viewing user information
- Disabling user accounts
- Removing user accounts when necessary

### FR-46 - Manage Internship Listings

The system shall allow administrators to view and manage internship listings.

### FR-47 - Monitor Applications

The system shall allow administrators to monitor application records within the system.


## 12. Notifications and System Messages

### FR-48 - Success Messages

The system shall provide appropriate confirmation messages after successful operations.

Examples include:

- Registration successful
- Login successful
- Resume uploaded successfully
- Application submitted successfully
- Internship created successfully

### FR-49 - Error Messages

The system shall display clear error messages when an operation cannot be completed.

Examples include:

- Invalid login credentials
- Invalid file format
- Missing required information
- Duplicate application
- Internship no longer available


## 13. Data Validation

### FR-50 - Input Validation

The system shall validate user-provided information before storing or processing it.

### FR-51 - File Validation

The system shall validate uploaded resume files based on supported file types and applicable size restrictions.

### FR-52 - Required Fields

The system shall ensure that required fields are completed before allowing important operations such as registration, internship creation, and application submission.



## 14. Search and Data Retrieval

### FR-53 - Internship Search Results

The system shall display internship search results that satisfy the student's search or filtering criteria.

### FR-54 - Applicant Retrieval

The system shall retrieve and display applicants associated with a recruiter's internship listing.

### FR-55 - Application Retrieval

The system shall allow students and authorized recruiters to retrieve relevant application information according to their roles.