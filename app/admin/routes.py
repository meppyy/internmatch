from flask import (
    render_template, flash, redirect, request, url_for, current_app
)
from flask_login import current_user
from . import admin
from ..auth.decorators import role_required
from ..services.storage import delete_resume_file
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

@admin.route("/internships")
@role_required("admin")
def internship_management():
    internships = Internship.query.order_by(
        Internship.created_at.desc()
    ).all()

    return render_template(
        "admin/internships.html",
        internships=internships
    )


@admin.route(
    "/internships/<int:internship_id>/status",
    methods=["POST"]
)
@role_required("admin")
def update_internship_status(internship_id):
    internship = Internship.query.get_or_404(internship_id)

    new_status = request.form.get("status", "").strip()

    if new_status not in {"Draft", "Active", "Closed"}:
        flash("Invalid internship status.", "error")
        return redirect(url_for("admin.internship_management"))

    internship.status = new_status
    db.session.commit()

    flash(
        "Internship status updated successfully.",
        "success"
    )

    return redirect(url_for("admin.internship_management"))


@admin.route(
    "/internships/<int:internship_id>/delete",
    methods=["POST"]
)
@role_required("admin")
def delete_internship(internship_id):
    internship = Internship.query.get_or_404(internship_id)

    # Preserve all application history.
    existing_application = Application.query.filter_by(
        internship_id=internship.internship_id
    ).first()

    if existing_application:
        flash(
            "This internship has application history and cannot be deleted.",
            "error"
        )
        return redirect(url_for("admin.internship_management"))

    db.session.delete(internship)
    db.session.commit()

    flash("Internship deleted successfully.", "success")

    return redirect(url_for("admin.internship_management"))

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

@admin.route(
    "/users/<int:user_id>/delete",
    methods=["POST"]
)
@role_required("admin")
def delete_user(user_id):
    user = User.query.get_or_404(user_id)

    # Administrators cannot delete their own accounts.
    if user.user_id == current_user.user_id:
        flash("You cannot delete your own account.", "error")
        return redirect(url_for("admin.user_management"))

    # Accounts must be disabled before permanent deletion.
    if user.is_active:
        flash(
            "Disable the account before deleting it.",
            "error"
        )
        return redirect(url_for("admin.user_management"))

    resume_file_paths = []

    if user.role == "student":
        profile = StudentProfile.query.filter_by(
            user_id=user.user_id
        ).first()

        if profile:
            # Preserve all application history.
            existing_application = Application.query.filter_by(
                student_id=profile.student_id
            ).first()

            if existing_application:
                flash(
                    "This student has application history and "
                    "cannot be deleted.",
                    "error"
                )
                return redirect(
                    url_for("admin.user_management")
                )

            if profile.resume and profile.resume.file_path:
                resume_file_paths.append(
                    profile.resume.file_path
                )

    elif user.role == "recruiter":
        profile = RecruiterProfile.query.filter_by(
            user_id=user.user_id
        ).first()

        if profile:
            # Preserve internship listings and their history.
            existing_internship = Internship.query.filter_by(
                recruiter_id=profile.recruiter_id
            ).first()

            if existing_internship:
                flash(
                    "This recruiter has internship listings and "
                    "cannot be deleted.",
                    "error"
                )
                return redirect(
                    url_for("admin.user_management")
                )

    elif user.role == "admin":
        # Never remove the last available administrator.
        active_admins = User.query.filter_by(
            role="admin",
            is_active=True
        ).count()

        if active_admins < 1:
            flash(
                "At least one active administrator must remain.",
                "error"
            )
            return redirect(
                url_for("admin.user_management")
            )

    else:
        flash(
            "This account type cannot be deleted.",
            "error"
        )
        return redirect(url_for("admin.user_management"))

    # Delete database records only after all safeguards pass.
    db.session.delete(user)
    db.session.commit()

    # Clean up external resume files after the database commit.
    # This avoids deleting a file while its database record
    # still exists if the database transaction fails.
    cleanup_failed = False

    for file_path in resume_file_paths:
        try:
            delete_resume_file(file_path)
        except Exception:
            cleanup_failed = True
            current_app.logger.exception(
                "Resume cleanup failed after deleting user %s.",
                user_id
            )

    if cleanup_failed:
        flash(
            "Account deleted, but its stored resume could not "
            "be removed. Manual storage cleanup is required.",
            "warning"
        )
    else:
        flash("Account deleted successfully.", "success")

    return redirect(url_for("admin.user_management"))