import json

from flask import Flask, render_template, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024  # Ограничение: 1 МБ


@app.route("/", methods=["GET", "POST"])
def index():
    source = ""
    result = ""
    error = ""

    if request.method == "POST":
        source = request.form.get("source", "")

        try:
            data = json.loads(source)
            result = json.dumps(data, ensure_ascii=False, indent=4)
        except json.JSONDecodeError as exc:
            error = (
                f"{exc.msg}. "
                f"Строка {exc.lineno}, столбец {exc.colno}."
            )

    return render_template(
        "index.html",
        source=source,
        result=result,
        error=error,
    )


@app.get("/health")
def health():
    return {"status": "ok"}
