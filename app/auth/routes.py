from flask import flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from .decorators import role_required
from ..extensions import db
from ..models.recruiter import RecruiterProfile
from ..models.student import StudentProfile
from ..models.user import User
from . import auth


@auth.route("/test")
def test():
    return "Auth blueprint is working!"


@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")
        role = request.form.get("role", "").strip().lower()
        company_name = request.form.get("company_name", "").strip()

        if not name:
            flash("Name is required.", "error")
            return redirect(url_for("auth.register"))

        if not email:
            flash("Email is required.", "error")
            return redirect(url_for("auth.register"))

        if not password:
            flash("Password is required.", "error")
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("auth.register"))

        if role not in {"student", "recruiter"}:
            flash("Invalid role selected.", "error")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "error")
            return redirect(url_for("auth.register"))

        if role == "recruiter" and not company_name:
            flash("Company name is required for recruiters.", "error")
            return redirect(url_for("auth.register"))

        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password),
            role=role
        )

        db.session.add(user)
        db.session.flush()

        if role == "student":
            profile = StudentProfile(user_id=user.user_id)
        else:
            profile = RecruiterProfile(
                user_id=user.user_id,
                company_name=company_name
            )

        db.session.add(profile)
        db.session.commit()

        flash("Registration successful.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")

@auth.route("/logout")
def logout():
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("home"))

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()

        if user is None or not check_password_hash(
            user.password_hash,
            password
        ):
            flash("Invalid email or password.", "error")
            return redirect(url_for("auth.login"))

        login_user(user)

        flash("Login successful.", "success")
        return redirect(url_for("home"))

    return render_template("auth/login.html")

@auth.route("/student-test")
@role_required("student")
def student_test():
    return "Student access granted!"


@auth.route("/recruiter-test")
@role_required("recruiter")
def recruiter_test():
    return "Recruiter access granted!"


@auth.route("/admin-test")
@role_required("admin")
def admin_test():
    return "Admin access granted!"