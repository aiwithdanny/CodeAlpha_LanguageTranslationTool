"""Translation service layer.

Professional pattern: provider abstraction.
- Har translation provider (MyMemory, Google) ek hi interface follow karta hai.
- Kal ko naya provider (DeepL, Azure) add karna ho to sirf ek class likhni hai,
  baqi code ko haath nahi lagana parega (Open/Closed Principle).
- Primary provider fail ho to automatic fallback.
- Repeated translations memory me cache hoti hain (LRU).
"""

import logging
from abc import ABC, abstractmethod
from functools import lru_cache

from deep_translator import GoogleTranslator, MyMemoryTranslator

logger = logging.getLogger(__name__)

# Dropdown me dikhne wale languages: code -> display name
SUPPORTED_LANGUAGES = {
    "en-GB": "English",
    "ur-PK": "Urdu",
    "ps-PK": "Pashto",
    "pnb-PK": "Punjabi (Pakistan)",
    "hi-IN": "Hindi",
    "ar-SA": "Arabic",
    "fa-IR": "Persian",
    "tr-TR": "Turkish",
    "fr-FR": "French",
    "de-DE": "German",
    "es-ES": "Spanish",
    "it-IT": "Italian",
    "ru-RU": "Russian",
    "zh-CN": "Chinese (Simplified)",
    "ja-JP": "Japanese",
}


class TranslationError(Exception):
    """Koi bhi provider translate na kar sake to ye raise hoti hai."""


class BaseTranslator(ABC):
    """Har provider ko ye interface follow karna lazmi hai."""

    name: str = "base"

    @abstractmethod
    def translate(self, text: str, source: str, target: str) -> str:
        ...


class MyMemoryProvider(BaseTranslator):
    """Free API, key nahi chahiye. Daily limit: ~50k chars (anonymous)."""

    name = "mymemory"

    def translate(self, text: str, source: str, target: str) -> str:
        try:
            return MyMemoryTranslator(source=source, target=target).translate(text)
        except Exception as exc:
            logger.warning("MyMemory provider failed: %s", exc)
            raise TranslationError(f"MyMemory failed: {exc}") from exc


class GoogleProvider(BaseTranslator):
    """Google Translate (unofficial endpoint). Short codes: 'en-GB' -> 'en'."""

    name = "google"

    def translate(self, text: str, source: str, target: str) -> str:
        try:
            return GoogleTranslator(
                source=source.split("-")[0],
                target=target.split("-")[0],
            ).translate(text)
        except Exception as exc:
            logger.warning("Google provider failed: %s", exc)
            raise TranslationError(f"Google failed: {exc}") from exc


class TranslationService:
    """Public interface: validate -> cache check -> primary -> fallback."""

    def __init__(
        self,
        primary: str = "mymemory",
        fallback: str = "google",
        cache_size: int = 256,
    ):
        providers = {
            "mymemory": MyMemoryProvider(),
            "google": GoogleProvider(),
        }
        if primary not in providers or fallback not in providers:
            raise ValueError(f"Unknown provider. Choose from {list(providers)}")
        self._ordered = [providers[primary], providers[fallback]]
        # LRU cache: same text dobara aaye to API hit nahi hogi
        self._cached_translate = lru_cache(maxsize=cache_size)(self._translate_uncached)

    def _translate_uncached(self, text: str, source: str, target: str) -> str:
        errors = []
        for provider in self._ordered:
            try:
                return provider.translate(text, source, target)
            except TranslationError as exc:
                errors.append(f"{provider.name}: {exc}")
        raise TranslationError(" | ".join(errors))

    def translate(self, text: str, source: str, target: str) -> str:
        text = (text or "").strip()
        if not text:
            raise ValueError("Text khaali hai.")
        if source not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported source language: {source}")
        if target not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported target language: {target}")
        if source == target:
            return text  # same language: API call ki zaroorat nahi
        return self._cached_translate(text, source, target)
