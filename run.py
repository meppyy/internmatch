from app import create_app
from app.extensions import db

app = create_app()


if __name__ == "__main__":
    with app.app_context():
        print("FLASK DB:", db.engine.url)
        print("FLASK TABLES:", db.inspect(db.engine).get_table_names())

    app.run(debug=False)