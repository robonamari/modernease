import datetime
import glob
import mimetypes
import os
from typing import Any, Union
from urllib.parse import quote

from dotenv import load_dotenv
from flask import Flask, Response, abort, redirect, render_template, request, send_file
from flask_compress import Compress
from waitress import serve

from utils.translation import load_translation

load_dotenv(".env")

app = Flask(__name__, static_folder="assets")
app.add_url_rule(
    "/favicon.ico",
    endpoint="favicon",
    redirect_to=os.getenv("favicon"),
)
Compress(app)


@app.route("/", methods=["GET"])
async def redirect_to_default_lang() -> Response:
    """
    Redirect to the default language '/en' preserving query string if any.

    Returns:
        Response: Redirect response (302) to '/en'.
    """
    url = "/en" + (request.full_path[1:] if "?" in request.full_path else "")
    return redirect(url, code=302)


@app.route("/<lang_code>", methods=["GET"])
async def index(lang_code: str) -> Union[str, Response]:
    """
    Render directory listing page for the given language.

    Validates the language, loads translation, lists directory contents, and renders page.

    Args:
        lang_code (str): Two-letter language code.

    Returns:
        Any: Rendered HTML or error response.
    """
    valid_languages = {
        f[:-4]
        for f in os.listdir("languages")
        if f.endswith(".yml") and len(f) == 6 and f[:-4].isalpha()
    }
    if lang_code not in valid_languages:
        return await download_file(lang_code)
    languages = await load_translation(lang_code)
    safe_root = os.path.join(os.path.dirname(__file__), "downloads")
    directory = os.path.normpath(os.path.join(safe_root, request.args.get("dir", "")))
    if not directory.startswith(safe_root) or not os.path.isdir(directory):
        return abort(404)
    file_list = []
    if directory != safe_root:
        parent_dir = os.path.dirname(directory)
        link = (
            f"/{lang_code}"
            if parent_dir == safe_root
            else f"/{lang_code}?dir={os.path.relpath(parent_dir, safe_root)}"
        )
        file_list.append(
            {
                "icon": "fas fa-level-up-alt",
                "name": languages["Parent_Directory"],
                "link": link,
            }
        )
    ignore_files = set(os.getenv("IGNORE_FILES", "").split(","))
    for name in sorted(
        f
        for f in os.listdir(directory)
        if not f.startswith(".") and f not in ignore_files
    ):
        file_path = os.path.join(directory, name)
        if os.path.isfile(file_path):
            mime_type, _ = mimetypes.guess_type(file_path)
            main_type = mime_type.split("/")[0] if mime_type else ""
            icon_map = {
                "video": "fas fa-video",
                "image": "fas fa-image",
                "audio": "fas fa-music",
                "application/pdf": "fas fa-file-pdf",
                "application/msword": "fas fa-file-word",
                "application/vnd.ms-excel": "fas fa-file-excel",
                "application/vnd.ms-powerpoint": "fas fa-file-powerpoint",
                "application/zip": "fas fa-file-archive",
                "application/x-rar-compressed": "fas fa-file-archive",
                "text/html": "fab fa-html5",
                "text/css": "fab fa-css3",
                "application/json": "fas fa-file-code",
                "application/javascript": "fab fa-js",
                "text/plain": "fas fa-file-alt",
            }
            icon = icon_map.get(mime_type, icon_map.get(main_type, "fas fa-file"))
            size_bytes = os.path.getsize(file_path)
            idx = min(4, max(0, (size_bytes.bit_length() - 1) // 10))
            size_units = ["B", "KB", "MB", "GB", "TB"]
            size = size_bytes / (1024**idx)
            file_list.append(
                {
                    "icon": icon,
                    "name": name,
                    "link": f"/{quote(os.path.relpath(file_path, safe_root))}",
                    "size": f"{size:.2f}{size_units[idx]}",
                    "date": datetime.datetime.fromtimestamp(
                        os.path.getmtime(file_path), tz=datetime.timezone.utc
                    ).strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                }
            )
        else:
            file_list.append(
                {
                    "icon": "fas fa-folder-open",
                    "name": name,
                    "link": f"/{lang_code}?dir={quote(os.path.relpath(file_path, safe_root))}",
                }
            )
    return render_template(
        "index.min.html",
        file_list=file_list,
        lang=lang_code,
        languages=languages,
        font_family=os.getenv("FONT_FAMILY"),
        favicon=os.getenv("FAVICON"),
        theme_color=os.getenv("THEME_COLOR"),
    )


@app.route("/LICENSE", methods=["GET"])
def show_license() -> Response:
    """
    Serve the LICENSE file as plain text.

    Returns:
        Response: Flask response containing the content of the LICENSE file with 'text/plain' MIME type.

    Raises:
        404: If the LICENSE file is not found.
    """
    return send_file("LICENSE", mimetype="text/plain")


@app.route("/<path:filename>", methods=["GET"])
async def download_file(filename: str) -> Union[Response, Any]:
    """
    Serve a file securely for download or inline display based on MIME type.

    Args:
        filename (str): Relative file path requested.

    Returns:
        Response: Flask response serving the file or aborts if access denied.
    """
    safe_root: str = os.path.join(os.path.dirname(__file__), "downloads")
    file_path: str = os.path.normpath(os.path.join(safe_root, filename))
    if not file_path.startswith(safe_root):
        return abort(403)
    ignore_files = set(os.getenv("ignore_files", "").split(","))
    for part in filename.split("/"):
        if part in ignore_files:
            return abort(403)
    if os.path.isfile(file_path):
        return send_file(file_path, as_attachment=True)
    return abort(404)


@app.errorhandler(Exception)
async def handle_error(error: Exception) -> Any:
    """
    Handle exceptions and redirect to a custom error page based on HTTP status code.

    Args:
        error (Exception): The raised exception.

    Returns:
        Response: Redirect response to a custom error page.
    """
    error_pages: dict[int, str] = {
        400: "400",
        401: "401",
        403: "403",
        404: "404",
        500: "500",
        503: "503",
    }
    error_code: int = getattr(error, "code", 500)
    error_page: str = error_pages.get(error_code, "500")
    return redirect(f"https://error.robonamari.com/{error_page}", code=302)


if __name__ == "__main__":
    mode = os.getenv("MODE")
    if mode == "development":
        app.run(
            host=os.getenv("HOST"),
            port=os.getenv("PORT"),
            debug=True,
            use_reloader=True,
            extra_files=glob.glob(
                os.path.join(os.path.dirname(__file__), "**", "*"), recursive=True
            ),
        )
    elif mode == "production":
        print(
            f"Starting server on {os.getenv('HOST')}:{os.getenv('PORT')} in production mode"
        )
        serve(app, host=os.getenv("HOST"), port=os.getenv("PORT"))
    else:
        raise RuntimeError(
            f"Invalid MODE '{mode}'. Must be 'development' or 'production'."
        )
