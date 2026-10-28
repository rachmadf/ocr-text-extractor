import os
from flask import Flask, redirect, url_for

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


def create_app():
    app = Flask(__name__, template_folder="template", static_folder="static")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-before-deployment")
    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB
    app.config["OUTPUT_FOLDER"] = os.path.join(BASE_DIR, "output")
    app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "static", "uploads")
    app.config["SOURCE_CODE_PATH"] = os.path.join(BASE_DIR, "static", "downloads", "ocr_text_extractor_source.zip")

    os.makedirs(app.config["OUTPUT_FOLDER"], exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    from routes.ocr import ocr
    app.register_blueprint(ocr)

    @app.route("/")
    def home():
        return redirect(url_for("ocr.index"))

    @app.errorhandler(413)
    def file_too_large(_error):
        from flask import render_template
        return render_template(
            "index.html",
            error="The uploaded image exceeds the 10 MB limit.",
            extracted_text="",
        ), 413

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1")
