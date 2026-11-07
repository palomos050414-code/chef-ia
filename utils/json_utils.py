"""Extraer y validar JSON en respuestas de LLM."""
import json
import re
from typing import Any


def extract_json(text: str) -> Any:
    """Parsea JSON limpiando bloques ```json y texto alrededor. Lanza ValueError si falla."""
    t = re.sub(r"```(?:json)?", "", text or "").strip()
    try:
        return json.loads(t)
    except json.JSONDecodeError:
        pass
    pairs = sorted((t.find(o), c) for o, c in (("{", "}"), ("[", "]")) if t.find(o) != -1)
    for start, close in pairs:
        end = t.rfind(close)
        if end > start:
            try:
                return json.loads(t[start : end + 1])
            except json.JSONDecodeError:
                continue
    raise ValueError("La respuesta del modelo no contiene JSON válido.")


def require_keys(data: Any, keys: list[str]) -> dict:
    """Verifica que data sea un dict con las claves requeridas."""
    if not isinstance(data, dict):
        raise ValueError("Se esperaba un objeto JSON.")
    missing = [k for k in keys if k not in data]
    if missing:
        raise ValueError(f"Faltan campos en la respuesta: {', '.join(missing)}")
    return data


def find_base64(data: Any) -> str | None:
    """Busca recursivamente una cadena base64 larga (imagen/video) en una respuesta."""
    if isinstance(data, dict):
        for k in ("base64", "b64_json", "image", "video", "b64_video"):
            v = data.get(k)
            if isinstance(v, str) and len(v) > 100:
                return v
        data = list(data.values())
    if isinstance(data, list):
        for v in data:
            found = find_base64(v)
            if found:
                return found
    return None


if __name__ == "__main__":
    assert extract_json('Aquí: ```json\n{"a": 1}\n```') == {"a": 1}
    assert extract_json('[{"x": 2}]') == [{"x": 2}]
    assert find_base64({"artifacts": [{"base64": "A" * 200}]}) == "A" * 200
    print("OK")
