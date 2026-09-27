from flask import render_template
from flask_login import current_user

from . import student
from ..auth.decorators import role_required
from ..models.student import StudentProfile


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