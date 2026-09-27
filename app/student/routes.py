import os

from flask import render_template, request, redirect, url_for, current_app, send_file
from flask_login import current_user
from werkzeug.utils import secure_filename

from ..models.resume import Resume
from . import student
from ..auth.decorators import role_required
from ..models.student import StudentProfile
from ..extensions import db
from ..models.skill import Skill

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

            if extension not in allowed_extensions:
                return render_template(
                    "student/upload_resume.html",
                     student=student_profile,
                    error="Invalid file type. Please upload a PDF, DOC, or DOCX file."
                )

            upload_folder = current_app.config["UPLOAD_FOLDER"]

            os.makedirs(upload_folder, exist_ok=True)

            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            resume = Resume.query.filter_by(
                student_id=student_profile.student_id
            ).first()

            if resume:
                old_file_path = resume.file_path

                if os.path.exists(old_file_path) and old_file_path != file_path:
                    os.remove(old_file_path)

                resume.file_name = filename
                resume.file_path = file_path
            else:
                resume = Resume(
                    student_id=student_profile.student_id,
                    file_name=filename,
                    file_path=file_path
                )
                db.session.add(resume)

            db.session.commit()

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

    if not os.path.exists(resume.file_path):
        return "Resume file not found", 404

    return send_file(
        resume.file_path,
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