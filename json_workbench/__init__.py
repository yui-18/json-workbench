import json

from flask import Flask, jsonify, render_template, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024


MESSAGES = {
    "Expecting value": "Здесь должно быть значение",
    "Expecting property name enclosed in double quotes":
        "Имя поля должно быть в двойных кавычках",
    "Expecting ':' delimiter": "После имени поля нужно двоеточие",
    "Expecting ',' delimiter": "Проверь запятые и закрывающие скобки",
    "Unterminated string starting at": "Добавь закрывающую кавычку",
    "Invalid \\escape": "Проверь символ после обратного слеша",
    "Extra data": "После конца JSON есть лишний текст",
}


def reject_constant(value):
    raise ValueError(f"В JSON нельзя использовать {value}")


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/format")
def format_json():
    payload = request.get_json(silent=True)

    if not isinstance(payload, dict):
        return jsonify(error="Не удалось прочитать запрос"), 400

    text = payload.get("text")
    mode = payload.get("mode")

    if not isinstance(text, str) or mode not in ("pretty", "compact"):
        return jsonify(error="Не удалось прочитать запрос"), 400

    try:
        data = json.loads(text, parse_constant=reject_constant)

        if mode == "pretty":
            output = json.dumps(data, ensure_ascii=False, indent=4)
        else:
            output = json.dumps(
                data, ensure_ascii=False, separators=(",", ":")
            )

        return jsonify(output=output)

    except json.JSONDecodeError as exc:
        message = MESSAGES.get(exc.msg, "Проверь JSON в этом месте")

        if exc.msg.startswith("Invalid control character"):
            message = "Внутри строки есть недопустимый символ"
        elif exc.msg.startswith("Invalid \\u"):
            message = "Проверь запись Unicode-символа"

        return jsonify(
            error=message,
            line=exc.lineno,
            column=exc.colno,
            position=exc.pos,
        ), 400

    except ValueError as exc:
        return jsonify(error=str(exc)), 400

    except RecursionError:
        return jsonify(error="Слишком много вложенных объектов"), 400


@app.errorhandler(413)
def too_large(_):
    return jsonify(error="Текст слишком большой. Лимит запроса — 1 МБ"), 413


@app.get("/health")
def health():
    return {"status": "ok"}
