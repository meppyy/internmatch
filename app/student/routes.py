from flask import render_template, request, redirect, url_for
from flask_login import current_user

from . import student
from ..auth.decorators import role_required
from ..models.student import StudentProfile
from ..extensions import db

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
        student_profile.phone = request.form.get("phone", "").strip()
        student_profile.education = request.form.get("education", "").strip()
        student_profile.profile_summary = request.form.get(
            "profile_summary", ""
        ).strip()
        student_profile.experience = request.form.get(
            "experience", ""
        ).strip()
        student_profile.projects = request.form.get(
            "projects", ""
        ).strip()
        student_profile.certifications = request.form.get(
            "certifications", ""
        ).strip()

        db.session.commit()

        return redirect(url_for("student.profile"))

    return render_template(
        "student/edit_profile.html",
        student=student_profile
    )