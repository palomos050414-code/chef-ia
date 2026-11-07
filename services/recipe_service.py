"""Ingredientes + preferencias -> receta en JSON (DeepSeek, solo texto)."""
from config import TEMPERATURE_JSON, TIMEOUT_CHAT
from prompts import RECIPE_SYSTEM, RETRY_REMINDER, build_recipe_user
from services.nvidia_client import NvidiaError, chat
from utils.json_utils import extract_json, require_keys

REQUIRED = ["nombre", "descripcion", "tiempo_total", "dificultad", "porciones",
            "ingredientes", "pasos", "prompt_imagen"]


def generate_recipe(api_key: str, ingredientes: list[str], dieta: str, porciones: int,
                    dificultad: str, cfg: dict) -> dict:
    """Genera y valida la receta. Reintenta una vez si el JSON es malformado."""
    messages = [{"role": "system", "content": RECIPE_SYSTEM},
                {"role": "user", "content": build_recipe_user(ingredientes, dieta, porciones, dificultad)}]
    for attempt in range(2):
        text = chat(api_key, cfg["chat_url"], cfg["recipe_model"], messages,
                    TEMPERATURE_JSON, 3000, TIMEOUT_CHAT)
        try:
            data = require_keys(extract_json(text), REQUIRED)
            if not isinstance(data["pasos"], list) or not data["pasos"]:
                raise ValueError("La receta no trae pasos.")
            return data
        except ValueError as exc:
            if attempt == 1:
                raise NvidiaError(f"Receta inválida: {exc}") from exc
            messages.append({"role": "user", "content": RETRY_REMINDER})
    return {}


if __name__ == "__main__":
    print("Prueba manual: generate_recipe(api_key, ['huevo'], 'ninguna', 2, 'fácil', DEFAULT_SETTINGS)")
