"""TranslationService ke unit tests.

Network ko mock kiya gaya hai taake tests fast aur reliable hon —
provider fail/success scenarios control me test ho sakte hain.
"""

import pytest

from services.translator import (
    BaseTranslator,
    TranslationError,
    TranslationService,
)


class FakeProvider(BaseTranslator):
    """Test double: asli API ki jagah fixed jawab deta hai."""

    name = "fake"

    def __init__(self, result="TRANSLATED", fail=False):
        self.result = result
        self.fail = fail
        self.calls = 0

    def translate(self, text, source, target):
        self.calls += 1
        if self.fail:
            raise TranslationError("fake failure")
        return self.result


def make_service(primary_fail=False, fallback_fail=False):
    svc = TranslationService.__new__(TranslationService)
    # seedha providers inject karo, network touch nahi hoga
    from functools import lru_cache

    primary = FakeProvider(fail=primary_fail)
    fallback = FakeProvider(result="FALLBACK_OK", fail=fallback_fail)
    svc._ordered = [primary, fallback]
    svc._cached_translate = lru_cache(maxsize=32)(svc._translate_uncached)
    return svc, primary, fallback


def test_same_language_skips_api():
    svc, primary, fallback = make_service()
    assert svc.translate("hello", "en-GB", "en-GB") == "hello"
    assert primary.calls == 0 and fallback.calls == 0  # API hit hi nahi hui


def test_empty_text_rejected():
    svc, _, _ = make_service()
    with pytest.raises(ValueError):
        svc.translate("   ", "en-GB", "ur-PK")


def test_unsupported_language_rejected():
    svc, _, _ = make_service()
    with pytest.raises(ValueError):
        svc.translate("hello", "xx-YY", "ur-PK")


def test_primary_provider_used():
    svc, primary, fallback = make_service()
    assert svc.translate("hello", "en-GB", "ur-PK") == "TRANSLATED"
    assert primary.calls == 1 and fallback.calls == 0


def test_fallback_when_primary_fails():
    svc, primary, fallback = make_service(primary_fail=True)
    assert svc.translate("hello", "en-GB", "ur-PK") == "FALLBACK_OK"
    assert primary.calls == 1 and fallback.calls == 1


def test_error_when_all_providers_fail():
    svc, _, _ = make_service(primary_fail=True, fallback_fail=True)
    with pytest.raises(TranslationError):
        svc.translate("hello", "en-GB", "ur-PK")


def test_cache_avoids_repeat_calls():
    svc, primary, _ = make_service()
    svc.translate("hello", "en-GB", "ur-PK")
    svc.translate("hello", "en-GB", "ur-PK")  # dobara same text
    assert primary.calls == 1  # sirf ek dafa API lagi
