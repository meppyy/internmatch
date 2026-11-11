from flask import render_template

from . import admin
from ..auth.decorators import role_required

from ..models.user import User
from ..models.student import StudentProfile
from ..models.recruiter import RecruiterProfile
from ..models.internship import Internship
from ..models.application import Application


@admin.route("/dashboard")
@role_required("admin")
def dashboard():
    total_users = User.query.count()

    total_students = StudentProfile.query.count()

    total_recruiters = RecruiterProfile.query.count()

    total_internships = Internship.query.count()

    active_internships = Internship.query.filter_by(
        status="Active"
    ).count()

    total_applications = Application.query.count()

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_students=total_students,
        total_recruiters=total_recruiters,
        total_internships=total_internships,
        active_internships=active_internships,
        total_applications=total_applications
    )


@admin.route("/users")
@role_required("admin")
def user_management():
    users = User.query.order_by(
        User.created_at.desc()
    ).all()

    return render_template(
        "admin/users.html",
        users=users
    )