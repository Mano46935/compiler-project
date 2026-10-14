"""Local Flask demonstration UI; compiler logic lives in the text2web package."""

from pathlib import Path
import re
from uuid import uuid4

from flask import Flask, abort, render_template, request, send_from_directory

from text2web import compile_source
from text2web.codegen import write_output

ROOT = Path(__file__).resolve().parent


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.update(MAX_CONTENT_LENGTH=128 * 1024, OUTPUT_ROOT=ROOT / "build" / "web")
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
            result = compile_source(source)
            if result.success:
                candidate = uuid4().hex
                try:
                    write_output(result, Path(app.config["OUTPUT_ROOT"]) / candidate)
                    build_id = candidate
                except OSError:
                    file_error = "Compilation succeeded, but output files could not be saved. Check folder permissions."
        return render_template(
            "index.html", source=source, sample_source=sample_source,
            result=result, build_id=build_id, file_error=file_error,
            debug=result.debug_data() if result else None,
        )

    @app.get("/build/<build_id>/<filename>")
    def output(build_id, filename):
        if not re.fullmatch(r"[0-9a-f]{32}", build_id) or filename not in {"index.html", "style.css"}:
            abort(404)
        response = send_from_directory(
            Path(app.config["OUTPUT_ROOT"]) / build_id, filename,
            as_attachment=request.args.get("download") == "1",
        )
        response.headers["Content-Security-Policy"] = "default-src 'none'; style-src 'self'; frame-ancestors 'self'"
        response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=5000, debug=False)
