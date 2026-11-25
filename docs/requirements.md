# InternMatch - Functional Requirements

## 1. Introduction

This document defines the functional requirements of the InternMatch system and records their current implementation status.

Functional requirements describe the operations and services that the system provides to its users.

The system has three primary user roles:

- Student
- Recruiter
- Administrator

### Implementation Status Definitions

Each functional requirement is assigned one of the following statuses:

- **Implemented:** The functionality is present in the application.
- **Partially Implemented:** Some aspects are implemented, but the complete stated requirement is not currently supported.
- **Planned:** The functionality has been identified as a requirement but has not yet been implemented.

Implementation statuses reflect the current application code and verified project behaviour. A partially implemented requirement must not be presented as fully supported.

## 2. User Registration

### FR-01 - User Registration

**Status: Implemented**

The system shall allow a new user to create an account.

The registration form shall collect:

- Full name
- Email address
- Password
- User role

The supported registration roles shall be:

- Student
- Recruiter

Administrator accounts shall be managed separately.

The system validates required registration fields, checks for existing email addresses, and creates the corresponding student or recruiter profile.

## 3. User Authentication

### FR-02 - User Login

**Status: Implemented**

The system shall allow registered users to log in using their email address and password.

Passwords shall be stored as password hashes rather than plaintext values.

### FR-03 - User Logout

**Status: Implemented**

The system shall allow authenticated users to securely log out of the system.

### FR-04 - Role-Based Access

**Status: Implemented**

The system shall provide different functionality based on the user's role.

- Students shall only be able to access student-specific functionality.
- Recruiters shall only be able to access recruiter-specific functionality.
- Administrative functionality shall only be accessible to administrators.

Protected routes shall enforce role-based access restrictions.

## 4. Student Profile Management

### FR-05 - Create Student Profile

**Status: Implemented**

The system shall create a student profile when a student successfully registers.

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

**Status: Implemented**

The system shall allow students to update their profile information.

### FR-07 - View Student Profile

**Status: Implemented**

The system shall allow students to view their profile information, including personal details, education, skills, experience, projects, certifications, and uploaded resume information.

## 5. Resume Management

### FR-08 - Resume Upload

**Status: Implemented**

The system shall allow students to upload a resume.

The system shall validate the uploaded file before storing it.

Supported file formats:

- PDF
- DOCX

The maximum upload size is 10 MB.

The system shall reject unsupported and invalid documents.

### FR-09 - Resume Replacement

**Status: Implemented**

The system shall allow students to replace their existing resume with an updated version.

The replacement process shall update the student's current resume record and remove the previous current-resume object after the database update succeeds, subject to successful storage cleanup.

Application-specific resume snapshots shall remain independent of this replacement.

### FR-10 - Resume Access

**Status: Implemented**

The system shall allow students to view or download their currently uploaded resume.

Resume retrieval shall use the configured storage backend.

Production resumes shall be retrieved from the private Supabase Storage bucket through the application.

### FR-11 - Resume Processing

**Status: Partially Implemented**

The system shall process uploaded PDF and DOCX resumes and extract readable textual information for use by the resume matching system.

The current implementation supports:

- PDF text extraction using pypdf.
- DOCX text extraction using python-docx.
- Text extraction from DOCX paragraphs and tables.
- Basic validation of document structure.
- Skill extraction from the extracted resume text.

The system does not currently provide comprehensive structured extraction of education, projects, employment history, or other resume sections.

Scanned PDF OCR is not implemented.

## 6. Internship Browsing

### FR-12 - View Internships

**Status: Implemented**

The system shall allow students to view available internship opportunities.

Internship listings shall display relevant information, including:

- Internship title
- Company name
- Internship description
- Location
- Work mode
- Duration
- Stipend
- Required skills
- Application deadline

Only active internship listings shall be displayed in the student browsing interface.

### FR-13 - Search Internships

**Status: Partially Implemented**

The system shall allow students to search for internships using available listing information.

The current implementation supports searching by:

- Internship title
- Company name
- Location
- Internship description

Dedicated searching by structured required skills is not currently implemented.

### FR-14 - Filter Internships

**Status: Partially Implemented**

The system shall allow students to filter internship listings using available attributes.

The current implementation provides:

- Work mode filtering.

Dedicated filters for location, skills, stipend, and duration are not currently implemented.

### FR-15 - View Internship Details

**Status: Implemented**

The system shall allow students to open an internship listing and view its details before applying.

The internship detail page also displays relevant skill-matching information and application availability.

## 7. Internship Creation and Management

### FR-16 - Create Internship

**Status: Implemented**

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

Required fields and relevant input values shall be validated before the internship is stored.

### FR-17 - Update Internship

**Status: Implemented**

The system shall allow recruiters to modify their existing internship listings.

Recruiters shall only be able to modify internships belonging to their accounts.

### FR-18 - Delete Internship

**Status: Implemented**

The system shall allow recruiters to remove their internship listings.

However, deletion shall be restricted when an internship has existing applications, in order to preserve application history.

Recruiters shall be instructed to close such listings instead.

### FR-19 - Manage Internship Status

**Status: Implemented**

The system shall allow recruiters to manage internship statuses.

Supported statuses include:

- Draft
- Active
- Closed

Students shall only be able to submit applications to active internships.

## 8. Internship Applications

### FR-20 - Apply for Internship

**Status: Partially Implemented**

The system shall allow a registered student to apply for an active internship.

The application shall be associated with the student's profile and, when an uploaded resume exists, an independent copy of that resume shall be associated with the application.

The current implementation permits application submission even when the student does not have an uploaded resume. Mandatory resume enforcement is therefore not implemented.

### FR-21 - Application Validation

**Status: Implemented**

Before submitting an application, the system shall verify that:

- The student is authenticated.
- The internship is active.
- The application deadline has not passed.
- The student has not already applied for the same internship.

### FR-22 - Prevent Duplicate Applications

**Status: Implemented**

The system shall prevent a student from submitting more than one application for the same internship.

Duplicate applications are checked in the application workflow and protected by a database uniqueness constraint.

### FR-23 - Application Confirmation

**Status: Implemented**

After a successful application, the system shall provide confirmation to the student.

### FR-24 - View Submitted Applications

**Status: Partially Implemented**

The system shall allow students to view a list of internships for which they have applied.

The application history shall display:

- Internship title
- Company
- Application date
- Application status

Match scores are calculated for internship and recruiter-facing matching views, but are not currently displayed in the student application history.

### FR-25 - Application Status

**Status: Implemented**

The system shall maintain the status of each internship application.

Supported application statuses include:

- Applied
- Under Review
- Shortlisted
- Rejected
- Selected

### FR-26 - Application Status Updates

**Status: Implemented**

The system shall allow authorized recruiters to update application statuses for applications submitted to their internships.

The updated status shall be visible to the corresponding student through application history.

## 9. Applicant Management

### FR-27 - View Applicants

**Status: Implemented**

The system shall allow recruiters to view students who have applied to their internship listings.

For each applicant, the system provides information including:

- Student name
- Email address
- Profile information
- Skills
- Application date
- Application status
- Match score
- Matching information

### FR-28 - View Applicant Resume

**Status: Implemented**

The system shall allow recruiters to access the resume associated with an applicant's application.

The system shall prefer the independent application resume snapshot when one exists.

For older applications without a snapshot, the existing Application.resume relationship shall be used as a compatibility fallback.

Recruiters shall only be able to access resumes associated with applications belonging to their own internship listings.

### FR-29 - Review Applicant Profile

**Status: Implemented**

The system shall allow recruiters to view relevant student profile information when reviewing an application.

### FR-30 - Update Application Status

**Status: Implemented**

The system shall allow authorized recruiters to update an applicant's application status.

Only the recruiter responsible for the relevant internship shall be allowed to perform the update.

### FR-31 - Applicant Ranking

**Status: Implemented**

The system shall provide recruiters with a ranked list of applicants for an internship based on their calculated skill-match scores.

Applicants are ordered by match score, with higher scores appearing first by default.

### FR-32 - Sort Applicants

**Status: Partially Implemented**

The system shall allow recruiters to sort applicants using relevant attributes.

The current implementation supports:

- Match score, highest first.
- Match score, lowest first.
- Application date, newest first.
- Application date, oldest first.

Application status filtering is available, but dedicated sorting by application status is not implemented.

## 10. Resume Matching and Ranking

### FR-33 - Resume Text Extraction

**Status: Implemented**

The system shall extract readable text from supported uploaded resumes.

Extracted text shall be stored with the resume and used for skill extraction and further analysis.

Supported document formats are PDF and DOCX.

### FR-34 - Resume Preprocessing

**Status: Partially Implemented**

The system shall perform basic normalization during skill extraction and matching.

The current implementation supports:

- Case-insensitive skill identification.
- Flexible whitespace handling in recognized skill aliases.
- Removal of duplicate extracted skill entries.
- Case-insensitive comparison of student and internship skill names.

Comprehensive resume text preprocessing, including general stop-word removal and broader text normalization, is not currently implemented.

### FR-35 - Skill Extraction

**Status: Partially Implemented**

The system shall identify recognized skills from extracted resume text.

The current implementation uses a predefined skill-alias dictionary and regular-expression matching.

Recognized skills include programming languages, frameworks, libraries, databases, development tools, and other predefined technical skills.

The extracted skills are added to the student's skill profile without automatically removing manually maintained skills.

The implementation does not provide unrestricted extraction of arbitrary skills or general semantic keyword identification.

### FR-36 - Internship Requirement Processing

**Status: Implemented**

The system shall process skills and requirements specified by recruiters when creating or updating internship listings.

Required skills are maintained through structured skill relationships, with the existing required-skills text field available as a fallback.

### FR-37 - Resume-Internship Matching

**Status: Partially Implemented**

The system shall compare the skills associated with a student's profile against the requirements of an internship.

The current implementation uses the student's stored skill profile, which can contain automatically extracted and manually added skills.

It does not directly perform semantic comparison of the entire extracted resume text against an internship description.

### FR-38 - Match Score Generation

**Status: Implemented**

The system shall generate a numerical match score representing compatibility between the student's skills and the internship's required skills.

The score is presented as a percentage.

The current calculation is:

Match Percentage = (Number of Matched Required Skills / Total Required Skills) × 100

When no required skills are specified, the system does not generate an artificial percentage.

### FR-39 - Matched Skills

**Status: Implemented**

The system shall identify and display skills that are present in both the student's skill profile and the internship requirements.

### FR-40 - Missing Skills

**Status: Implemented**

The system shall identify internship requirements that are not currently present in the student's skill profile.

### FR-41 - Match Explanation

**Status: Partially Implemented**

The system shall provide information explaining the candidate's match score.

The current implementation generates explanations based on the number of matched skills, total required skills, and calculated percentage.

Matched and missing skills are also provided for recruiter evaluation.

Advanced explanations based on semantic relevance, experience, project quality, or other weighted factors are not currently implemented.

### FR-42 - Candidate Ranking

**Status: Implemented**

The system shall rank applicants for an internship using their calculated match scores.

Recruiters shall be provided with an ordered applicant list for evaluation.

### FR-43 - Ranking Update

**Status: Partially Implemented**

The system shall update applicant ranking information when relevant student skills or internship requirements change.

The current implementation calculates skill matches dynamically when internship and recruiter applicant pages are requested.

Persistent match-score recalculation and comprehensive synchronization of previously extracted skills after resume replacement are not fully implemented.

In particular, replacing a resume does not automatically remove previously extracted skills from the student's profile.

## 11. Administrator Functions

### FR-44 - View Users

**Status: Implemented**

The system shall allow administrators to view registered users.

### FR-45 - Manage Users

**Status: Implemented**

The system shall allow administrators to manage user accounts.

Administrative actions include:

- Viewing user information.
- Disabling user accounts.
- Enabling disabled user accounts.
- Removing eligible user accounts when necessary.

Account deletion is subject to safeguards intended to preserve application and internship history.

Administrators cannot disable or delete their own accounts through these operations, and restrictions protect the last active administrator.

### FR-46 - Manage Internship Listings

**Status: Implemented**

The system shall allow administrators to view and manage internship listings.

Administrative operations include:

- Viewing internship listings.
- Changing internship status.
- Removing eligible listings.

Listings with existing applications shall be protected from deletion to preserve application history.

### FR-47 - Monitor Applications

**Status: Implemented**

The system shall allow administrators to view and monitor application records within the system.

The administrative application monitor provides relevant student, recruiter, internship, and application information.

## 12. Notifications and System Messages

### FR-48 - Success Messages

**Status: Implemented**

The system shall provide appropriate confirmation messages after successful operations.

Examples include:

- Registration successful.
- Login successful.
- Resume uploaded successfully.
- Application submitted successfully.
- Internship created successfully.
- Application status updated successfully.

### FR-49 - Error Messages

**Status: Implemented**

The system shall display error messages when an operation cannot be completed.

Examples include:

- Invalid login credentials.
- Invalid file format.
- Missing required information.
- Duplicate application.
- Internship no longer available.
- Unauthorized resource access.

## 13. Data Validation

### FR-50 - Input Validation

**Status: Partially Implemented**

The system shall validate user-provided information before storing or processing it.

The current implementation includes validation for:

- Required registration information.
- Duplicate email addresses.
- Password confirmation.
- User roles.
- Internship listing fields.
- Internship dates and stipend values.
- Required skills.
- Resume filenames and supported extensions.

Comprehensive validation across every profile field and every user input is not yet implemented.

### FR-51 - File Validation

**Status: Implemented**

The system shall validate uploaded resume files based on supported file formats and applicable size restrictions.

The system supports PDF and DOCX files up to 10 MB.

Invalid, corrupted, unsupported, and legacy DOC files shall be rejected.

Valid documents with no extractable text may be accepted with an appropriate warning.

### FR-52 - Required Fields

**Status: Partially Implemented**

The system shall ensure that required fields are completed before allowing important operations such as registration and internship creation.

The current implementation validates the principal registration and internship creation fields.

Application submission validates authentication, internship availability, application deadline, and duplicate applications.

However, application submission does not enforce the presence of an uploaded resume or complete student profile information.

## 14. Search and Data Retrieval

### FR-53 - Internship Search Results

**Status: Implemented**

The system shall display internship search results that satisfy the student's supported search and filtering criteria.

The current implementation supports text searching across internship titles, company names, locations, and descriptions, together with work-mode filtering.

### FR-54 - Applicant Retrieval

**Status: Implemented**

The system shall retrieve and display applicants associated with a recruiter's internship listing.

The system shall verify internship ownership before returning applicant information.

### FR-55 - Application Retrieval

**Status: Implemented**

The system shall allow students and authorized recruiters to retrieve relevant application information according to their roles.

Administrators shall also be able to access the administrative application monitor.

Access to application-specific resumes shall enforce recruiter ownership.

## 15. Application Resume Snapshot Management

### FR-56 - Application Resume Snapshot Preservation

**Status: Implemented**

The system shall create an independent copy of the student's current resume when an application is submitted, provided a resume is available.

The snapshot shall be associated with the corresponding application and shall preserve the resume submitted at the time of application.

The system shall ensure that:

- Each application can have one associated resume snapshot.
- The snapshot stores its own filename and storage path.
- Replacing the student's current resume does not overwrite existing application snapshots.
- Recruiters retrieve the original application snapshot when one is available.
- New applications may use the student's updated current resume.
- Legacy applications without snapshots retain compatibility through the existing Application.resume relationship.

The production implementation stores resume files through the configured storage abstraction. In the production environment, this uses a private Supabase Storage bucket.

The snapshot mechanism has been verified through the production Resume A to Resume B replacement workflow.

---

## 16. Implementation Status Summary

The functional requirements document distinguishes functionality that is implemented from functionality that has remaining limitations.

### Implemented Functionality

The following major areas have been implemented:

- User registration and authentication.
- Role-based access control.
- Student and recruiter profile management.
- Resume uploading, validation, and replacement.
- Resume text extraction and predefined skill extraction.
- Internship creation, browsing, and management.
- Student applications and application tracking.
- Recruiter applicant management.
- Application resume snapshot creation and retrieval.
- Rule-based skill matching and applicant ranking.
- Administrative user and internship management.
- Application monitoring.
- PostgreSQL production database integration.
- Private Supabase resume storage.

### Partially Implemented Functionality

The following requirements have known limitations:

- Comprehensive resume information extraction.
- Dedicated skill-based internship searching.
- Additional internship filters.
- Display of match scores in student application history.
- Application submission without mandatory resume enforcement.
- Advanced resume preprocessing.
- Generalized skill and keyword extraction.
- Direct semantic resume-internship comparison.
- Advanced match explanations.
- Comprehensive ranking synchronization after resume replacement.
- Application-status sorting.
- Comprehensive validation across every user input.
- Complete enforcement of profile and resume requirements before application submission.

### Planned Improvements

Potential future improvements include:

- Additional internship filters for location, stipend, duration, and skills.
- Improved skill extraction and normalization.
- More comprehensive resume information extraction.
- Advanced match explanations and weighted skill evaluation.
- Improved synchronization of extracted skills after resume replacement.
- Additional applicant sorting options.
- Expanded profile and application validation.

These improvements are not represented as completed functionality.

---

## 17. Document Maintenance

This document should be updated whenever a functional requirement is introduced, modified, implemented, or verified.

Implementation status should reflect the actual application behaviour rather than the intended future system design.

Manual production verification and automated test results should be recorded separately.

A requirement should only be marked as fully implemented when the corresponding functionality is present and its expected behaviour has been verified.