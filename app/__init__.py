from flask import Flask


def create_app():
    app = Flask(__name__)

    @app.route("/")
    def home():
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>InternMatch</title>
        </head>
        <body>
            <h1>InternMatch</h1>
            <p>Internship Portal + Resume Ranking System</p>
            <p>Project is running successfully.</p>
        </body>
        </html>
        """

    return app