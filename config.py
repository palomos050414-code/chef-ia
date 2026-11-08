"""Configuración central: URLs, IDs de modelos, timeouts y límites.

Los valores de DEFAULT_SETTINGS son editables desde la barra lateral
(expander "Configuración avanzada") porque el catálogo de NVIDIA puede cambiar.
"""

DEFAULT_SETTINGS: dict[str, str] = {
    "chat_url": "https://integrate.api.nvidia.com/v1/chat/completions",
    "vision_model": "nvidia/nemotron-3.5-super-vl-120b-a12b",  # confirmado en build.nvidia.com (multimodal, salida estructurada)
    "recipe_model": "deepseek-ai/deepseek-v4.1-flash",  # CONFIRMAR ID exacto en build.nvidia.com
    "image_url": "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.1-schnell",
    "video_url": "https://ai.api.nvidia.com/v1/cosmos/nvidia/cosmos3-nano",
    "status_url": "https://integrate.api.nvidia.com/v1/status/",
}

TIMEOUT_CHAT = 90          # segundos
TIMEOUT_IMAGE = 120
TIMEOUT_VIDEO_POLL = 240   # tiempo máximo total de espera del video
POLL_INTERVAL = 4
MAX_RETRIES = 3
TEMPERATURE_JSON = 0.3

MAX_IMAGE_SIDE = 1024
JPEG_QUALITY = 85
MAX_UPLOAD_MB = 8
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

DIETAS = ["ninguna", "vegetariana", "vegana", "sin gluten"]
DIFICULTADES = ["fácil", "media", "difícil"]

if __name__ == "__main__":
    print(DEFAULT_SETTINGS)
