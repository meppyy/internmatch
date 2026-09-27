from flask import render_template
from flask_login import current_user

from ..auth.decorators import role_required
from . import recruiter


@recruiter.route("/dashboard")
@role_required("recruiter")
def dashboard():
    return render_template(
        "recruiter/dashboard.html",
        recruiter_name=current_user.name
    )