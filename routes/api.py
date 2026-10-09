"""API routes (JSON endpoints).

Har response ka format consistent hai:
  success -> {"translation": "..."}
  error   -> {"error": "..."}  + sahi HTTP status code
"""

from flask import Blueprint, current_app, jsonify, request

from services.translator import SUPPORTED_LANGUAGES, TranslationError

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.route("/languages", methods=["GET"])
def list_languages():
    """Dropdown ke liye supported languages."""
    return jsonify({"languages": SUPPORTED_LANGUAGES})


@api_bp.route("/translate", methods=["POST"])
def translate():
    data = request.get_json(force=True, silent=True) or {}

    text = (data.get("text") or "").strip()
    source = data.get("source") or "en-GB"
    target = data.get("target") or "ur-PK"

    # --- input validation (pehle check, phir kaam) ---
    if not text:
        return jsonify({"error": "Text khaali hai. Kuch likhein."}), 400
    if len(text) > current_app.config["MAX_TEXT_LENGTH"]:
        return (
            jsonify(
                {
                    "error": f"Text bohat lamba hai "
                    f"(max {current_app.config['MAX_TEXT_LENGTH']} characters)."
                }
            ),
            400,
        )
    if source not in SUPPORTED_LANGUAGES or target not in SUPPORTED_LANGUAGES:
        return jsonify({"error": "Ghalat language select hui hai."}), 400

    try:
        result = current_app.translator.translate(text, source, target)
        return jsonify({"translation": result})
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except TranslationError as exc:
        current_app.logger.error("Translation failed: %s", exc)
        return (
            jsonify({"error": "Translation service abhi available nahi. Thori dair baad try karein."}),
            502,
        )
