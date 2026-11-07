"""prompt_imagen -> imagen del plato (FLUX.1-schnell u otro modelo de imagen)."""
from config import MAX_RETRIES, TIMEOUT_IMAGE
from services.nvidia_client import NvidiaError, request
from utils.image_utils import b64_to_bytes
from utils.json_utils import find_base64


def generate_dish_image(api_key: str, prompt: str, cfg: dict) -> bytes:
    """Devuelve bytes de la imagen. Soporta 'artifacts[0].base64', 'image' y 'b64_json'."""
    payload = {"prompt": prompt, "width": 1024, "height": 1024, "seed": 0, "steps": 4}
    resp = request("POST", cfg["image_url"], api_key, payload, TIMEOUT_IMAGE, MAX_RETRIES)
    b64 = find_base64(resp.json())
    if not b64:
        raise NvidiaError("La respuesta del generador no contiene imagen.")
    return b64_to_bytes(b64)


if __name__ == "__main__":
    print("Prueba manual: generate_dish_image(api_key, 'A bowl of pasta', DEFAULT_SETTINGS)")
