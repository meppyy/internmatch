from flask import render_template

from . import student
from ..auth.decorators import role_required


@student.route("/dashboard")
@role_required("student")
def dashboard():
    return "Student Dashboard"