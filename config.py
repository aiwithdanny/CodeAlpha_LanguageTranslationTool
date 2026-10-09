"""Application configuration.

Saari settings environment variables se aati hain taake code
change kiye baghair dev/prod me alag behavior ho sake.
"""

import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-secret-key")
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

    # Konsa translation provider pehle try ho ("mymemory" ya "google")
    PRIMARY_PROVIDER = os.environ.get("TRANSLATION_PROVIDER", "mymemory")

    # Ek request me max kitne characters translate ho sakte hain
    MAX_TEXT_LENGTH = int(os.environ.get("MAX_TEXT_LENGTH", "5000"))

    # Kitne recent translations memory me cache rakhein
    CACHE_SIZE = int(os.environ.get("TRANSLATION_CACHE_SIZE", "256"))

    # API rate safety: ek IP se per-minute max requests (basic guard)
    RATE_LIMIT_PER_MINUTE = int(os.environ.get("RATE_LIMIT_PER_MINUTE", "60"))
