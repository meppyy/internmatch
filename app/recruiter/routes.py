from flask import render_template
from flask_login import current_user

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

    return render_template(
        "recruiter/dashboard.html",
        recruiter_name=current_user.name,
        company_name=recruiter_profile.company_name,
        total_internships=total_internships
    )