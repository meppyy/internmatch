# Software Requirements Specification

## InternMatch

### Internship Portal and Resume Ranking System


## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) document defines the functional and non-functional requirements of InternMatch.

InternMatch is a web-based internship portal that enables students to discover and apply for internship opportunities while allowing recruiters to manage internship listings and evaluate applicants using a resume-based matching and ranking system.

This document serves as a reference for the design, development, testing, and evaluation of the system.

### 1.2 Scope

InternMatch will provide a centralized platform for students and recruiters.

Students will be able to:

- Create and manage their profiles.
- Upload resumes.
- Browse internship opportunities.
- Search and filter internships.
- Apply for internships.
- Track application status.
- View resume-internship matching information.

Recruiters will be able to:

- Create and manage internship listings.
- Specify internship requirements.
- View applicants.
- Access applicant resumes and profiles.
- View candidate match scores.
- Rank applicants.

Administrators will be able to manage users, internship listings, and application records.

The system will also include a resume processing and ranking component that extracts relevant information from resumes and compares it with internship requirements.

### 1.3 Intended Audience

This document is intended for:

- Project developers
- Project testers
- Project evaluators
- Faculty members
- Future maintainers of the system

### 1.4 Definitions and Abbreviations

| Term | Definition |
|---|---|
| InternMatch | The internship portal and resume ranking system |
| Student | A user who searches and applies for internships |
| Recruiter | A user who creates internships and evaluates applicants |
| Administrator | A user responsible for managing the system |
| Resume | A document containing a student's education, skills, experience, projects, and other relevant information |
| Match Score | A numerical measure representing compatibility between a resume and an internship |
| Ranking | Ordering applicants based on their calculated match scores |
| SRS | Software Requirements Specification |
| ORM | Object-Relational Mapping |
| UI | User Interface |
| API | Application Programming Interface |

## 2. Overall Description

### 2.1 Product Perspective

InternMatch is a standalone web-based application consisting of multiple interconnected modules.

The major components of the system are:

- User authentication
- Student profile management
- Recruiter management
- Internship management
- Application management
- Resume management
- Resume processing
- Resume matching and ranking
- Administrative management

The system will use a layered and modular design so that individual components can be developed, tested, and maintained independently.

The high-level interaction between the major components is:

```
                    ┌──────────────────┐
                    │      Users       │
                    │                  │
                    │ Students         │
                    │ Recruiters       │
                    │ Administrators   │
                    └────────┬─────────┘
                             |
                             v
                    ┌──────────────────┐
                    │   Web Interface  │
                    │   HTML/CSS/JS    │
                    └────────┬─────────┘
                             |
                             v
                    ┌──────────────────┐
                    │   Flask Backend  │
                    └────────┬─────────┘
                             |
              ┌──────────────┼──────────────┐
              |              |              |
              v              v              v
       ┌────────────┐ ┌──────────────┐ ┌──────────────┐
       │  Database  │ │    Resume    │ │   Matching   │
       │   SQLite   │ │  Processing  │ │    Engine    │
       └────────────┘ └──────────────┘ └──────────────┘
```

### 2.2 Product Functions

The major functions of InternMatch are:

**User Management**
- User registration
- User login and logout
- Role-based access
- Profile management

**Internship Management**
- Create internship listings
- View internship listings
- Search internships
- Filter internships
- Update internship listings
- Delete internship listings
- Manage internship status

**Application Management**
- Submit applications
- Prevent duplicate applications
- View submitted applications
- Track application status
- Update application status

**Resume Management**
- Upload resumes
- Validate resume files
- Replace resumes
- Extract resume text
- Process relevant resume information

**Resume Matching and Ranking**
- Process internship requirements
- Extract relevant skills and keywords
- Compare resume information with internship requirements
- Generate match scores
- Identify matched and missing skills
- Rank applicants

**Administration**
- Manage users
- Manage internship listings
- Monitor applications
- Manage inappropriate or invalid content


### 2.3 User Classes and Characteristics

**Students**

Students are the primary users seeking internship opportunities. Students are expected to have basic computer and web browsing skills.

Students can use the system to:

- Maintain their profiles
- Upload resumes
- Discover internships
- Apply for internships
- Track applications
- Review matching information

**Recruiter**

Recruiters represent organizations offering internship opportunities.

Recruiters can use the system to:

- Create internship listings
- Define internship requirements
- Review applications
- Access applicant resumes
- View match scores
- Rank applicants

**Administrator**

Administrators are responsible for managing and monitoring the platform.

Administrators can:

- Manage user accounts
- Manage internship listings
- Monitor application records
- Remove invalid content


### 2.4 Operating Environment

The initial version of InternMatch will operate in a local development environment.

The expected environment includes:

- Operating System: Windows, Linux, or macOS
- Backend: Python
- Web Framework: Flask
- Database: SQLite
- Frontend: Modern web browser
- Development Environment: Visual Studio Code or another suitable IDE

The application will be accessible through a standard web browser.


### 2.5 Design and Implementation Constraints

The following constraints apply to the initial implementation:

- Python will be used for backend development.
- Flask will be used as the web framework.
- SQLite will be used as the initial relational database.
- The application will initially be developed and tested locally.
- Uploaded resumes must conform to supported file formats.
- The resume ranking system will depend on the information available in resumes and internship descriptions.
- The system should be designed in a modular manner to support future expansion.

### 2.6 Assumptions and Dependencies

The system is based on the following assumptions:

- Users provide valid registration and profile information.
- Recruiters provide accurate internship information and requirements.
- Students upload readable and relevant resumes.
- Users have access to a compatible web browser.
- The initial development environment has Python and the required project dependencies installed.
- Resume processing depends on the availability of extractable text from uploaded documents.

The system may depend on third-party Python libraries for database management, document processing, and matching functionality.


### 2.7 General System Workflow

```
User Registration
       |
       v
User Authentication
       |
       ├───────────────┐
       |               |
       v               v
    Student         Recruiter
       |               |
       v               v
Upload Resume    Create Internship
       |               |
       v               v
Browse Internships  Define Requirements
       |               |
       v               |
    Apply         Receive Applications
       |               |
       |               v
       |         Resume Processing
       |               |
       |               v
       |         Match Score
       |               |
       |               v
       |         Applicant Ranking
       |               |
       └───────┬───────┘
               v
        Application Management
```



## 3. Specific Requirements

This section describes the specific functional and non-functional requirements that the InternMatch system must satisfy.

The detailed functional requirements are maintained separately in `docs/requirements.md`.



### 3.1 Functional Requirements

The system shall provide the following major functional capabilities:

#### User Management

- User registration
- User login and logout
- Role-based access control
- Student profile management
- Recruiter profile management

#### Internship Management

- Internship creation
- Internship viewing
- Internship searching
- Internship filtering
- Internship updating
- Internship deletion
- Internship status management

#### Application Management

- Internship application submission
- Duplicate application prevention
- Application validation
- Application history
- Application status tracking
- Application status updates

#### Resume Management

- Resume upload
- Resume validation
- Resume replacement
- Resume viewing
- Resume text extraction
- Resume information processing

#### Resume Matching and Ranking

- Internship requirement processing
- Skill and keyword extraction
- Resume-internship comparison
- Match score generation
- Matched skill identification
- Missing skill identification
- Match explanation
- Applicant ranking

#### Administration

- User management
- Internship listing management
- Application monitoring
- Content management



### 3.2 Non-Functional Requirements

The system shall also satisfy the following non-functional requirements:

#### Usability

The user interface should be simple, clear, and easy to navigate for students and recruiters.

#### Performance

The system should provide reasonable response times for common operations such as logging in, browsing internships, viewing profiles, and retrieving applications under normal usage conditions.

#### Security

The system shall:

- Protect user credentials.
- Restrict access to role-specific functionality.
- Validate user input.
- Validate uploaded files.
- Prevent unauthorized access to protected resources.

#### Reliability

The system should maintain consistency of user, internship, resume, and application data during normal system operation.

#### Maintainability

The software should use a modular structure that allows individual components to be modified, tested, or extended without significantly affecting unrelated components.

#### Scalability

The system architecture should allow future expansion of features and support for additional users and internship listings.

#### Compatibility

The system should function correctly on commonly used modern web browsers.

#### Explainability

The resume ranking component should provide understandable information about the major factors contributing to a candidate's match score.



### 3.3 Data Requirements

The system shall store and manage information associated with the following entities:

#### User

- User ID
- Name
- Email
- Password
- Role

#### Student Profile

- Student ID
- Education
- Skills
- Experience
- Projects
- Certifications
- Resume

#### Recruiter Profile

- Recruiter ID
- Organization
- Contact information
- Profile information

#### Internship

- Internship ID
- Recruiter ID
- Title
- Company
- Description
- Location
- Work mode
- Duration
- Stipend
- Required skills
- Eligibility criteria
- Application deadline
- Status

#### Application

- Application ID
- Student ID
- Internship ID
- Application date
- Application status
- Match score

#### Resume

- Resume ID
- Student ID
- File path
- Extracted text
- Upload date



### 3.4 External Interface Requirements

#### User Interface

The system shall provide web interfaces for:

- Registration
- Login
- Student dashboard
- Recruiter dashboard
- Internship listings
- Internship details
- Profile management
- Resume upload
- Application management
- Applicant management
- Candidate ranking

#### Database Interface

The application shall communicate with a relational database for persistent storage of users, profiles, internships, applications, and resume-related information.

#### Resume Processing Interface

The application shall pass uploaded resume documents to the resume processing component for text extraction and analysis.

#### Ranking Interface

The resume processing component shall provide processed information to the matching and ranking component for calculating candidate match scores.



### 3.5 Constraints

The initial implementation shall use:

- Python for backend development.
- Flask as the web framework.
- SQLite as the development database.
- HTML, CSS, and JavaScript for the frontend.
- Git and GitHub for version control.

The initial version will be developed and tested in a local environment.



## 4. Acceptance Criteria

The InternMatch system shall satisfy the following acceptance criteria.

### 4.1 User Management

- A new user shall be able to register successfully.
- A registered user shall be able to log in and log out.
- Users shall only be able to access functionality permitted for their role.
- Students and recruiters shall be able to manage their respective profiles.

### 4.2 Internship Management

- Recruiters shall be able to create internship listings.
- Recruiters shall be able to update and delete their internship listings.
- Students shall be able to browse available internships.
- Students shall be able to search and filter internship listings.
- Students shall be able to view complete internship details.

### 4.3 Application Management

- Students shall be able to apply for active internships.
- The system shall prevent duplicate applications.
- Students shall be able to view their submitted applications.
- Students shall be able to view the current status of their applications.
- Recruiters shall be able to review applications for their internship listings.
- Recruiters shall be able to update application statuses.

### 4.4 Resume Management

- Students shall be able to upload supported resume files.
- The system shall validate uploaded resume files.
- Students shall be able to replace an existing resume.
- The system shall extract readable text from supported resumes.
- The system shall associate each resume with its corresponding student.

### 4.5 Resume Matching and Ranking

- The system shall process internship requirements.
- The system shall identify relevant skills or keywords from resumes.
- The system shall compare resume information with internship requirements.
- The system shall generate a match score.
- The system shall identify major matched skills.
- The system shall identify major missing skills where applicable.
- The system shall provide an understandable explanation of the matching result.
- Recruiters shall be able to view applicants ranked according to their match scores.

### 4.6 Administrative Functions

- Administrators shall be able to view registered users.
- Administrators shall be able to manage user accounts.
- Administrators shall be able to manage internship listings.
- Administrators shall be able to monitor application records.

### 4.7 Testing and Validation

The completed system shall be tested to verify that:

- Core functional requirements work as specified.
- Invalid user input is handled appropriately.
- Unauthorized operations are restricted.
- Duplicate applications are prevented.
- Resume uploads are validated.
- Resume matching produces consistent results for the same input.
- Major system errors are handled with appropriate messages.



## 5. Conclusion

This Software Requirements Specification establishes the requirements and expected behavior of the InternMatch system.

The requirements defined in this document will serve as the foundation for the system design, database design, implementation, testing, and final evaluation of the project.