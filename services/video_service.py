"""Opcional: video corto del plato con Cosmos text2video (soporta respuesta asíncrona 202)."""
import time

from config import MAX_RETRIES, POLL_INTERVAL, TIMEOUT_IMAGE, TIMEOUT_VIDEO_POLL
from services.nvidia_client import NvidiaError, request
from utils.image_utils import b64_to_bytes
from utils.json_utils import find_base64


def generate_video(api_key: str, prompt: str, cfg: dict) -> bytes:
    """Genera un video (bytes mp4). Hace polling con timeout si la API responde 202."""
    payload = {"model_mode": "text2video", "prompt": prompt, "resolution": "480_16_9",
               "num_frames": 25, "num_inference_steps": 35, "fps": 24, "seed": 42}
    resp = request("POST", cfg["video_url"], api_key, payload, TIMEOUT_IMAGE, MAX_RETRIES)
    deadline = time.time() + TIMEOUT_VIDEO_POLL
    req_id = resp.headers.get("NVCF-REQID")
    while resp.status_code == 202:
        if not req_id or time.time() > deadline:
            raise NvidiaError("Tiempo de espera agotado generando el video.")
        time.sleep(POLL_INTERVAL)
        resp = request("GET", cfg["status_url"] + req_id, api_key, None, 60, 2)
    b64 = find_base64(resp.json())
    if not b64:
        raise NvidiaError("La respuesta no contiene video.")
    return b64_to_bytes(b64)


if __name__ == "__main__":
    print("Prueba manual: generate_video(api_key, 'Pasta steaming on a plate', DEFAULT_SETTINGS)")
