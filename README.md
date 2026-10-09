# 🌍 CodeAlpha Task 1: Language Translation Tool

A production-style web app that translates text between 15 languages using free translation APIs.

## ✨ Features

- Translate text between **15 languages** (Urdu, Pashto, Punjabi, English, Arabic, French, …)
- **Provider abstraction** — MyMemory API primary, Google Translate automatic fallback
- **LRU caching** — repeated translations don't hit the API again
- Character counter, language **swap button**, loading spinner, error toasts
- 📋 **Copy** button, 🔊 **Text-to-Speech** (browser built-in)
- Input validation (empty text, max length, language whitelist) with proper HTTP status codes
- `/health` endpoint for monitoring
- **14 unit tests** (pytest, providers mocked — no network needed)

## 🛠 Tech Stack

Python 3 · Flask · deep-translator · HTML/CSS/JS · pytest

## 🚀 Setup

```bash
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

### Environment variables (optional)

| Variable | Default | Purpose |
|---|---|---|
| `TRANSLATION_PROVIDER` | `mymemory` | Primary provider (`mymemory` / `google`) |
| `MAX_TEXT_LENGTH` | `5000` | Max characters per request |
| `TRANSLATION_CACHE_SIZE` | `256` | Cached translations in memory |
| `FLASK_DEBUG` | `false` | Debug mode |

## 🧪 Tests

```bash
pytest tests/ -v
```

## 📁 Project Structure

```
├── app.py                  # App factory + entry point
├── config.py               # Environment-based config
├── services/
│   └── translator.py       # Provider abstraction, fallback, caching, validation
├── routes/
│   └── api.py              # /api/translate, /api/languages
├── templates/index.html    # UI
├── static/css/style.css
├── static/js/app.js
└── tests/                  # test_translator.py, test_api.py
```

## 🔌 API Reference

**POST /api/translate**
```json
{ "text": "Hello", "source": "en-GB", "target": "ur-PK" }
```
→ `200 {"translation": "ہیلو"}` · `400` validation error · `502` provider down

**GET /api/languages** → supported language list · **GET /health** → status

## 🔮 Future Improvements

- Auto language detection · translation history · Docker image · rate limiting per IP
