from flask import render_template, request
from flask_login import current_user

from ..extensions import db
from ..auth.decorators import role_required
from . import recruiter
from ..models.recruiter import RecruiterProfile
from ..models.internship import Internship


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
        db.session.commit()

    return render_template(
        "recruiter/edit_profile.html",
        recruiter_profile=recruiter_profile
    )