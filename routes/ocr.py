import os
import uuid
from pathlib import Path

from flask import (
    Blueprint, current_app, render_template, request,
    send_from_directory, send_file
)
from werkzeug.utils import secure_filename

from services.ocr_service import OCRService

ocr = Blueprint("ocr", __name__, url_prefix="/ocr")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "bmp", "tif", "tiff", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@ocr.route("/about", methods=["GET"])
def about():
    """Display the project overview and product requirements."""
    return render_template("about.html")


@ocr.route("/download-source", methods=["GET"])
def download_source():
    """Download the project source-code archive."""
    source_path = current_app.config["SOURCE_CODE_PATH"]
    if not os.path.isfile(source_path):
        return "Source-code archive is not available.", 404
    return send_file(source_path, as_attachment=True, download_name="ocr_text_extractor_source.zip", mimetype="application/zip")


@ocr.route("/", methods=["GET"])
def index():
    return render_template("index.html", extracted_text="", error=None, result_filename=None)


@ocr.route("/extract", methods=["POST"])
def extract():
    image = request.files.get("image_file")
    if image is None or not image.filename:
        return render_template(
            "index.html", extracted_text="", error="Select an image file first.",
            result_filename=None
        ), 400

    original_name = secure_filename(image.filename)
    if not original_name or not allowed_file(original_name):
        return render_template(
            "index.html", extracted_text="", error="Unsupported file type. Upload PNG, JPG, JPEG, BMP, TIFF, or WEBP.",
            result_filename=None
        ), 400

    upload_dir = current_app.config["UPLOAD_FOLDER"]
    output_dir = current_app.config["OUTPUT_FOLDER"]
    os.makedirs(upload_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)

    token = uuid.uuid4().hex
    extension = Path(original_name).suffix.lower()
    upload_path = os.path.join(upload_dir, f"{token}{extension}")
    result_filename = f"ocr_result_{token}.txt"

    try:
        image.save(upload_path)
        extracted_text = OCRService.extract_text(upload_path)
        if not extracted_text.strip():
            extracted_text = "No text was detected in this image."

        output_path = os.path.join(output_dir, result_filename)
        with open(output_path, "w", encoding="utf-8") as result_file:
            result_file.write(extracted_text)

        return render_template(
            "index.html",
            extracted_text=extracted_text,
            error=None,
            result_filename=result_filename,
            original_filename=original_name,
        )
    except RuntimeError as exc:
        return render_template(
            "index.html", extracted_text="", error=str(exc), result_filename=None
        ), 500
    except Exception:
        current_app.logger.exception("OCR processing failed")
        return render_template(
            "index.html",
            extracted_text="",
            error="OCR processing failed. Check the server log and confirm the image is valid.",
            result_filename=None,
        ), 500
    finally:
        try:
            if os.path.exists(upload_path):
                os.remove(upload_path)
        except OSError:
            current_app.logger.warning("Could not remove temporary upload: %s", upload_path)


@ocr.route("/download/<path:filename>", methods=["GET"])
def download_txt(filename):
    # Only allow generated OCR result filenames; never accept arbitrary paths.
    if not filename.startswith("ocr_result_") or not filename.endswith(".txt") or os.path.basename(filename) != filename:
        return "Invalid result filename.", 400

    output_dir = current_app.config["OUTPUT_FOLDER"]
    file_path = os.path.join(output_dir, filename)
    if not os.path.isfile(file_path):
        return "The result file was not found. Run OCR again.", 404

    return send_from_directory(
        output_dir, filename, as_attachment=True,
        download_name="ocr_result.txt", mimetype="text/plain; charset=utf-8"
    )
