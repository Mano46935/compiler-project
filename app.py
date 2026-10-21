"""Local Flask demonstration UI; compiler logic lives in the text2web package."""

from pathlib import Path
import re
from uuid import uuid4

from flask import Flask, abort, render_template, request, send_from_directory
from werkzeug.utils import secure_filename

from text2web import compile_source
from text2web.codegen import write_output
from text2web.assets import IMAGE_EXTENSIONS, is_supported_image, local_asset_path

ROOT = Path(__file__).resolve().parent
MAX_SOURCE_BYTES = 128 * 1024


def _read_image_uploads():
    uploads = {}
    for upload in request.files.getlist("assets"):
        filename = secure_filename(upload.filename or "")
        if not filename:
            continue
        extension = Path(filename).suffix.lower()
        data = upload.read()
        if extension not in IMAGE_EXTENSIONS or not is_supported_image(data, extension):
            return None, f"{filename} is not a supported PNG, JPEG, GIF, or WebP image."
        if filename in uploads:
            return None, f"More than one uploaded file has the name {filename}."
        uploads[filename] = data
    return uploads, None


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(MAX_CONTENT_LENGTH=10 * 1024 * 1024, OUTPUT_ROOT=ROOT / "build" / "web")
    if test_config:
        app.config.update(test_config)

    @app.route("/", methods=["GET", "POST"])
    def index():
        sample_source = (ROOT / "examples" / "fest.sp").read_text(encoding="utf-8")
        source = sample_source
        result = None
        build_id = None
        file_error = None
        if request.method == "POST":
            source = request.form.get("source", "")
            if len(source.encode("utf-8")) > MAX_SOURCE_BYTES:
                result = None
                file_error = "Source instructions cannot exceed 128 KB."
            else:
                result = compile_source(source)
            if result and result.success:
                uploads, file_error = _read_image_uploads()
                if uploads is not None:
                    assets = {}
                    missing = []
                    for element in result.symbols:
                        if element.type != "image":
                            continue
                        asset_path = local_asset_path(element.properties["src"])
                        if asset_path is None:
                            continue
                        filename = secure_filename(asset_path.name)
                        if filename not in uploads:
                            missing.append(asset_path.name)
                        else:
                            assets[asset_path.as_posix()] = uploads[filename]
                    if missing:
                        file_error = "Upload the image file(s) referenced by your instructions: " + ", ".join(sorted(set(missing)))
                    else:
                        candidate = uuid4().hex
                        try:
                            write_output(
                                result, Path(app.config["OUTPUT_ROOT"]) / candidate,
                                assets=assets,
                            )
                            build_id = candidate
                        except OSError:
                            file_error = "Compilation succeeded, but output files could not be saved. Check folder permissions."
        return render_template(
            "index.html", source=source, sample_source=sample_source,
            result=result, build_id=build_id, file_error=file_error,
            debug=result.debug_data() if result else None,
        )

    @app.get("/build/<build_id>/<path:filename>")
    def output(build_id, filename):
        allowed = filename in {"index.html", "style.css"}
        image_file = Path(filename).suffix.lower() in IMAGE_EXTENSIONS
        if not re.fullmatch(r"[0-9a-f]{32}", build_id) or not (allowed or image_file):
            abort(404)
        response = send_from_directory(
            Path(app.config["OUTPUT_ROOT"]) / build_id, filename,
            as_attachment=request.args.get("download") == "1",
        )
        response.headers["Content-Security-Policy"] = "default-src 'none'; style-src 'self'; img-src 'self' http: https:; frame-ancestors 'self'"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
