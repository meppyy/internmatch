from datetime import datetime
from flask import render_template, request, flash
from flask_login import current_user

from ..extensions import db
from ..auth.decorators import role_required
from . import recruiter
from ..models.recruiter import RecruiterProfile
from ..models.internship import Internship
from ..models.skill import Skill
from app.models import internship


@recruiter.route("/dashboard")
@role_required("recruiter")
def dashboard():
    recruiter_profile = RecruiterProfile.query.filter_by(
        user_id=current_user.user_id
    ).first()

    total_internships = Internship.query.filter_by(
        recruiter_id=recruiter_profile.recruiter_id
    ).count()
    
    active_internships = Internship.query.filter_by(
        recruiter_id=recruiter_profile.recruiter_id,
        status="Active"
    ).count()

    closed_internships = Internship.query.filter_by(
        recruiter_id=recruiter_profile.recruiter_id,
        status="Closed"
    ).count()
    
    return render_template(
        "recruiter/dashboard.html",
        recruiter_name=current_user.name,
        company_name=recruiter_profile.company_name,
        total_internships=total_internships,
        active_internships=active_internships,
        closed_internships=closed_internships
    )

@recruiter.route("/profile")
@role_required("recruiter")
def profile():
    recruiter_profile = RecruiterProfile.query.filter_by(
        user_id=current_user.user_id
    ).first()

    return render_template(
        "recruiter/profile.html",
        recruiter_profile=recruiter_profile,
        recruiter_email=current_user.email
    )

@recruiter.route("/profile/edit", methods=["GET", "POST"])
@role_required("recruiter")
def edit_profile():
    recruiter_profile = RecruiterProfile.query.filter_by(
        user_id=current_user.user_id
    ).first()

    if request.method == "POST":
        recruiter_profile.company_name = request.form["company_name"]
        recruiter_profile.company_description = request.form["company_description"]
        recruiter_profile.contact_phone = request.form["contact_phone"]

        db.session.commit()

    return render_template(
        "recruiter/edit_profile.html",
        recruiter_profile=recruiter_profile
    )

@recruiter.route("/internships/create", methods=["GET", "POST"])
@role_required("recruiter")
def create_internship():

    if request.method == "POST":
        title = request.form["title"].strip()

        if not title:
            flash("Internship title is required.", "error")
            return render_template("recruiter/create_internship.html")

        description = request.form["description"].strip()

        if not description:
            flash("Internship description is required.", "error")
            return render_template("recruiter/create_internship.html")

        location = request.form["location"]
        work_mode = request.form["work_mode"]

        if work_mode not in ["Remote", "Hybrid", "On-site"]:
            flash("Invalid work mode.", "error")
            return render_template("recruiter/create_internship.html")

        duration = request.form["duration"]
        stipend = request.form["stipend"].strip()

        try:
            stipend_value = float(stipend)
        except ValueError:
            flash("Stipend must be a number.", "error")
            return render_template("recruiter/create_internship.html")

        if stipend_value < 0:
            flash("Stipend cannot be negative.", "error")
            return render_template("recruiter/create_internship.html")

        eligibility = request.form["eligibility"].strip()

        if not eligibility:
            flash("Eligibility requirements are required.", "error")
            return render_template("recruiter/create_internship.html")

        deadline = datetime.strptime(
            request.form["deadline"],
            "%Y-%m-%d"
        ).date()
        status = request.form["status"]

        required_skills = request.form["required_skills"]

        skill_names = [
            skill.strip()
            for skill in required_skills.split(",")
            if skill.strip()
        ]

        skills = []

        for skill_name in skill_names:
            skill = Skill.query.filter_by(skill_name=skill_name).first()

            if not skill:
                skill = Skill(skill_name=skill_name)
                db.session.add(skill)

            skills.append(skill)

        recruiter_profile = RecruiterProfile.query.filter_by(
            user_id=current_user.user_id
        ).first()

        internship = Internship(
            recruiter_id=recruiter_profile.recruiter_id,
            company_name=recruiter_profile.company_name,
            title=title,
            description=description,
            location=location,
            work_mode=work_mode,
            duration=duration,
            stipend=stipend,
            eligibility=eligibility,
            deadline=deadline,
            status=status
        )

        db.session.add(internship)

        for skill in skills:
            internship.skills.append(skill)

        db.session.commit()

        flash("Internship created successfully.", "success")

    return render_template("recruiter/create_internship.html")