from flask import Blueprint, current_app, send_from_directory

pwa = Blueprint("pwa", __name__)


@pwa.route("/manifest.json")
def manifest():
    response = send_from_directory(
        current_app.static_folder,
        "manifest.json",
        mimetype="application/manifest+json",
    )
    response.headers["Cache-Control"] = "no-cache"
    return response


@pwa.route("/service-worker.js")
def service_worker():
    response = send_from_directory(
        current_app.static_folder,
        "service-worker.js",
        mimetype="application/javascript",
    )
    response.headers["Cache-Control"] = "no-cache"
    return response