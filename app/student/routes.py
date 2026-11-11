import mimetypes
from io import BytesIO

from ..services.storage import (
    save_resume_file,
    read_resume_file,
    delete_resume_file
)

from flask import render_template, request, redirect, url_for, current_app, send_file
from flask_login import current_user
from werkzeug.utils import secure_filename

from flask import flash
from sqlalchemy.exc import IntegrityError
from ..models.application import Application

from ..models.resume import Resume
from . import student
from ..auth.decorators import role_required
from ..models.student import StudentProfile
from ..extensions import db
from ..models.skill import Skill
from ..models.internship import Internship
from sqlalchemy import or_
from ..services import resume_parser, skill_extractor
from ..services.skill_matching import calculate_skill_match

@student.route("/dashboard")
@role_required("student")
def dashboard():
    student_profile = StudentProfile.query.filter_by(
        user_id=current_user.user_id
    ).first()

    return render_template(
        "student/dashboard.html",
        student=student_profile
    )

@student.route("/profile")
@role_required("student")
def profile():
    student_profile = StudentProfile.query.filter_by(
        user_id=current_user.user_id
    ).first()

    return render_template(
        "student/profile.html",
        student=student_profile
    )

@student.route("/profile/edit", methods=["GET", "POST"])
@role_required("student")
def edit_profile():
    student_profile = StudentProfile.query.filter_by(
        user_id=current_user.user_id
    ).first()

    if request.method == "POST":
        if "phone" in request.form:
            student_profile.phone = request.form.get("phone", "").strip()

        if "education" in request.form:
            student_profile.education = request.form.get("education", "").strip()

        if "profile_summary" in request.form:
            student_profile.profile_summary = request.form.get(
            "profile_summary", ""
        ).strip()

        if "experience" in request.form:
            student_profile.experience = request.form.get(
            "experience", ""
        ).strip()

        if "projects" in request.form:
            student_profile.projects = request.form.get(
            "projects", ""
        ).strip()

        if "certifications" in request.form:
            student_profile.certifications = request.form.get(
            "certifications", ""
        ).strip()

        db.session.commit()

        return redirect(url_for("student.profile"))

    return render_template(
        "student/edit_profile.html",
        student=student_profile
    )

@student.route("/skills", methods=["GET", "POST"])
@role_required("student")
def skills():
    student_profile = StudentProfile.query.filter_by(
        user_id=current_user.user_id
    ).first()

    if request.method == "POST":
        skill_name = request.form.get("skill_name", "").strip()

        if skill_name:
            skill = Skill.query.filter_by(
                skill_name=skill_name
            ).first()

            if not skill:
                skill = Skill(skill_name=skill_name)
                db.session.add(skill)
                db.session.flush()

            if skill not in student_profile.skills:
                student_profile.skills.append(skill)

            db.session.commit()

        return redirect(url_for("student.skills"))

    return render_template(
        "student/skills.html",
        student=student_profile
    )


@student.route("/skills/remove/<int:skill_id>", methods=["POST"])
@role_required("student")
def remove_skill(skill_id):
    student_profile = StudentProfile.query.filter_by(
        user_id=current_user.user_id
    ).first()

    skill = Skill.query.get_or_404(skill_id)

    if skill in student_profile.skills:
        student_profile.skills.remove(skill)
        db.session.commit()

    return redirect(url_for("student.skills"))

@student.route("/experience")
@role_required("student")
def experience():
    student_profile = StudentProfile.query.filter_by(
        user_id=current_user.user_id
    ).first()

    return render_template(
        "student/experience.html",
        student=student_profile
    )

@student.route("/resume/upload", methods=["GET", "POST"])
@role_required("student")
def upload_resume():
    student_profile = StudentProfile.query.filter_by(
        user_id=current_user.user_id
    ).first()

    if request.method == "POST":
        file = request.files.get("resume")

        if file and file.filename:
            filename = secure_filename(file.filename)

            extension = filename.rsplit(".", 1)[1].lower() if "." in filename else ""

            allowed_extensions = current_app.config[
                "ALLOWED_RESUME_EXTENSIONS"
            ]

            if not filename or extension not in allowed_extensions:
                return render_template(
                    "student/upload_resume.html",
                    student=student_profile,
                    error="Invalid file type. Please upload a PDF, DOC, or DOCX file."
                )

            resume = Resume.query.filter_by(
                student_id=student_profile.student_id
            ).first()

            old_file_path = resume.file_path if resume else None

            # Extract searchable text before saving the uploaded file.
            try:
                file_content = file.read()
                extracted_text = resume_parser.extract_resume_text(
                    file_content,
                    filename
                )
            except ValueError as error:
                current_app.logger.warning(
                    "Resume text extraction skipped for %s: %s",
                    filename,
                    error
                )
                extracted_text = None
            finally:
                # Storage must receive the complete original file.
                file.seek(0)

            # Save the new resume through the configured storage service.
            try:
                new_file_path = save_resume_file(
                    file,
                    student_profile.student_id,
                    filename
                )
            except ValueError as error:
                return render_template(
                    "student/upload_resume.html",
                    student=student_profile,
                    error=str(error)
                )

            # Update the database only after the file was saved.
            try:
                if resume:
                    resume.file_name = filename
                    resume.file_path = new_file_path
                    resume.extracted_text = extracted_text
                else:
                    resume = Resume(
                        student_id=student_profile.student_id,
                        file_name=filename,
                        file_path=new_file_path,
                        extracted_text=extracted_text
                    )
                    db.session.add(resume)

                # Add automatically detected skills without removing
                # skills the student has already entered manually.
                if extracted_text:
                    detected_skills = skill_extractor.extract_skills(
                        extracted_text
                    )

                    for skill_name in detected_skills:
                        skill = Skill.query.filter_by(
                            skill_name=skill_name
                        ).first()

                        if not skill:
                            skill = Skill(skill_name=skill_name)
                            db.session.add(skill)
                            db.session.flush()

                        if skill not in student_profile.skills:
                            student_profile.skills.append(skill)

                db.session.commit()

            except Exception:
                db.session.rollback()

                # Clean up the newly uploaded file if the DB update fails.
                try:
                    delete_resume_file(new_file_path)
                except Exception:
                    current_app.logger.exception(
                        "Could not clean up the uploaded resume."
                    )

                raise

            # Delete the previous resume only after the DB update succeeds.
            if old_file_path and old_file_path != new_file_path:
                try:
                    delete_resume_file(old_file_path)
                except Exception:
                    current_app.logger.exception(
                        "Could not delete the previous resume."
                    )

            return redirect(url_for("student.profile"))

    return render_template(
        "student/upload_resume.html",
        student=student_profile
    )


@student.route("/resume")
@role_required("student")
def view_resume():
    student_profile = StudentProfile.query.filter_by(
        user_id=current_user.user_id
    ).first()

    if not student_profile or not student_profile.resume:
        return "Resume not found", 404

    resume = student_profile.resume

    try:
        file_content = read_resume_file(resume.file_path)
    except FileNotFoundError:
        return "Resume file not found", 404

    content_type, _ = mimetypes.guess_type(resume.file_name)

    return send_file(
        BytesIO(file_content),
        mimetype=content_type or "application/octet-stream",
        as_attachment=False,
        download_name=resume.file_name
    )

@student.route("/profile/completion")
@role_required("student")
def profile_completion():
    student_profile = StudentProfile.query.filter_by(
        user_id=current_user.user_id
    ).first()

    if not student_profile:
        return "Student profile not found", 404

    sections = {
        "Phone": bool(student_profile.phone),
        "Education": bool(student_profile.education),
        "Profile Summary": bool(student_profile.profile_summary),
        "Skills": bool(student_profile.skills),
        "Experience": bool(student_profile.experience),
        "Projects": bool(student_profile.projects),
        "Certifications": bool(student_profile.certifications),
        "Resume": bool(student_profile.resume),
    }

    completed = sum(sections.values())
    total = len(sections)

    percentage = int((completed / total) * 100)

    return render_template(
        "student/profile_completion.html",
        student=student_profile,
        sections=sections,
        percentage=percentage
    )


@student.route("/internships")
@role_required("student")
def browse_internships():
    search_query = request.args.get("q", "").strip()
    work_mode = request.args.get("work_mode", "").strip()

    internship_query = Internship.query.filter_by(
        status="Active"
    )

    if search_query:
        search_pattern = f"%{search_query}%"

        internship_query = internship_query.filter(
            or_(
                Internship.title.ilike(search_pattern),
                Internship.company_name.ilike(search_pattern),
                Internship.location.ilike(search_pattern),
                Internship.description.ilike(search_pattern)
            )
        )

    if work_mode:
        internship_query = internship_query.filter(
            Internship.work_mode == work_mode
        )

    # First retrieve the internships.
    internships = internship_query.order_by(
        Internship.created_at.desc()
    ).all()

    # Then retrieve the logged-in student's profile.
    student_profile = StudentProfile.query.filter_by(
        user_id=current_user.user_id
    ).first()

    # Finally calculate a match for each internship.
    skill_matches = {
        internship.internship_id: calculate_skill_match(
            student_profile,
            internship
        )
        for internship in internships
    }

    return render_template(
        "student/internships.html",
        internships=internships,
        query=search_query,
        work_mode=work_mode,
        skill_matches=skill_matches
    )



@student.route("/internships/<int:internship_id>")
@role_required("student")
def internship_details(internship_id):
    internship = Internship.query.filter_by(
        internship_id=internship_id,
        status="Active"
    ).first_or_404()

    student_profile = StudentProfile.query.filter_by(
        user_id=current_user.user_id
    ).first_or_404()

    existing_application = Application.query.filter_by(
        student_id=student_profile.student_id,
        internship_id=internship_id
    ).first()

    return render_template(
        "student/internship_details.html",
        internship=internship,
        has_applied=existing_application is not None
    )


@student.route(
    "/internships/<int:internship_id>/apply",
    methods=["POST"]
)
@role_required("student")
def apply_to_internship(internship_id):
    student_profile = StudentProfile.query.filter_by(
        user_id=current_user.user_id
    ).first_or_404()

    internship = Internship.query.filter_by(
        internship_id=internship_id,
        status="Active"
    ).first_or_404()

    existing_application = Application.query.filter_by(
        student_id=student_profile.student_id,
        internship_id=internship_id
    ).first()

    if existing_application:
        flash("You have already applied to this internship.", "error")
        return redirect(url_for(
            "student.internship_details",
            internship_id=internship_id
        ))

    resume = Resume.query.filter_by(
        student_id=student_profile.student_id
    ).first()

    application = Application(
        student_id=student_profile.student_id,
        internship_id=internship_id,
        resume_id=resume.resume_id if resume else None,
        status="Applied"
    )

    db.session.add(application)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        flash("You have already applied to this internship.", "error")
    else:
        flash("Your application was submitted successfully.", "success")

    return redirect(url_for(
        "student.internship_details",
        internship_id=internship_id
    ))

@student.route("/applications")
@role_required("student")
def application_history():
    student_profile = StudentProfile.query.filter_by(
        user_id=current_user.user_id
    ).first_or_404()

    applications = Application.query.filter_by(
        student_id=student_profile.student_id
    ).order_by(
        Application.application_date.desc()
    ).all()

    return render_template(
        "student/applications.html",
        applications=applications
    )