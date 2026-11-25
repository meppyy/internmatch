from flask import (
    render_template, flash, redirect, request, url_for
)
from flask_login import current_user
from . import admin
from ..auth.decorators import role_required

from ..extensions import db
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

@admin.route(
    "/users/<int:user_id>/status",
    methods=["POST"]
)
@role_required("admin")
def update_user_status(user_id):
    user = User.query.get_or_404(user_id)

    action = request.form.get("action", "").strip().lower()

    if action not in {"disable", "enable"}:
        flash("Invalid account action.", "error")

    elif action == "disable":

        # Administrators cannot disable their own accounts.
        if user.user_id == current_user.user_id:
            flash(
                "You cannot disable your own account.",
                "error"
            )

        elif not user.is_active:
            flash("Account is already disabled.", "warning")

        else:
            # Never disable the final active administrator.
            if user.role == "admin":
                active_admins = User.query.filter_by(
                    role="admin",
                    is_active=True
                ).count()

                if active_admins <= 1:
                    flash(
                        "You cannot disable the last active "
                        "administrator account.",
                        "error"
                    )
                    return redirect(
                        url_for("admin.user_management")
                    )

            user.is_active = False
            user.session_version += 1

            db.session.commit()

            flash("Account disabled successfully.", "success")

    else:
        if user.is_active:
            flash("Account is already enabled.", "warning")
        else:
            user.is_active = True
            db.session.commit()

            flash("Account enabled successfully.", "success")

    return redirect(url_for("admin.user_management"))