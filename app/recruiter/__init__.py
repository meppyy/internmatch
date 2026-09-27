from flask import Blueprint

recruiter = Blueprint(
    "recruiter",
    __name__,
    url_prefix="/recruiter"
)

from . import routes