from flask import render_template

from ..auth.decorators import role_required
from . import recruiter


@recruiter.route("/dashboard")
@role_required("recruiter")
def dashboard():
    return "Recruiter Dashboard"