"""App entry point. Factory pattern: create_app() se app banti hai.

Faida: testing me alag config ke saath app bana sakte hain,
aur code import karne pe server khud-ba-khud start nahi hota.
"""

import logging

from flask import Flask, render_template

from config import Config
from routes.api import api_bp
from services.translator import SUPPORTED_LANGUAGES, TranslationService


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Translator ek dafa banao, har request me reuse hoga (cache bhi shared)
    app.translator = TranslationService(
        primary=app.config["PRIMARY_PROVIDER"],
        cache_size=app.config["CACHE_SIZE"],
    )

    app.register_blueprint(api_bp)

    @app.route("/")
    def index():
        return render_template("index.html", languages=SUPPORTED_LANGUAGES)

    @app.route("/health", methods=["GET"])
    def health():
        """Monitoring ke liye: app zinda hai ya nahi."""
        return {"status": "ok"}

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=app.config["DEBUG"])
