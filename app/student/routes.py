from flask import render_template, request, redirect, url_for
from flask_login import current_user

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