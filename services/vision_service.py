"""Imagen -> lista de ingredientes (modelo de visión)."""
from config import TEMPERATURE_JSON, TIMEOUT_CHAT
from prompts import RETRY_REMINDER, VISION_SYSTEM, VISION_USER
from services.nvidia_client import NvidiaError, chat
from utils.image_utils import to_data_url
from utils.json_utils import extract_json, require_keys


def detect_ingredients(api_key: str, jpeg_bytes: bytes, cfg: dict) -> list[dict]:
    """Devuelve [{'nombre': str, 'cantidad': str}, ...]. Reintenta una vez si el JSON es inválido."""
    messages = [
        {"role": "system", "content": VISION_SYSTEM},
        {"role": "user", "content": [
            {"type": "text", "text": VISION_USER},
            {"type": "image_url", "image_url": {"url": to_data_url(jpeg_bytes)}},
        ]},
    ]
    for attempt in range(2):
        text = chat(api_key, cfg["chat_url"], cfg["vision_model"], messages,
                    TEMPERATURE_JSON, 1024, TIMEOUT_CHAT)
        try:
            data = require_keys(extract_json(text), ["ingredientes"])
            items = [{"nombre": str(i.get("nombre", "")).strip(), "cantidad": str(i.get("cantidad", "")).strip()}
                     for i in data["ingredientes"] if isinstance(i, dict) and i.get("nombre")]
            if items:
                return items
            raise ValueError("No se detectaron ingredientes.")
        except ValueError as exc:
            if attempt == 1:
                raise NvidiaError(f"No se pudieron interpretar los ingredientes: {exc}") from exc
            messages.append({"role": "user", "content": RETRY_REMINDER})
    return []


if __name__ == "__main__":
    print("Prueba manual: detect_ingredients(api_key, jpeg_bytes, DEFAULT_SETTINGS)")
