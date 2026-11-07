"""Cliente HTTP genérico para NVIDIA: headers, reintentos y manejo de errores.
Nunca registra ni incluye la API key en los mensajes."""
import time

import requests


class NvidiaError(Exception):
    """Error genérico de la API."""


class AuthError(NvidiaError):
    """API key inválida o sin permisos."""


def _headers(api_key: str) -> dict:
    return {"Authorization": f"Bearer {api_key}", "Accept": "application/json",
            "Content-Type": "application/json"}


def _check(resp: requests.Response) -> None:
    if resp.status_code in (401, 403):
        raise AuthError(f"API key inválida o sin permisos (HTTP {resp.status_code}).")
    if resp.status_code >= 400:
        raise NvidiaError(f"Error HTTP {resp.status_code}: {resp.text[:200]}")


def request(method: str, url: str, api_key: str, payload: dict | None = None,
            timeout: int = 60, retries: int = 3) -> requests.Response:
    """Petición con reintentos y backoff exponencial ante 429/5xx y fallos de red."""
    last: Exception | None = None
    for attempt in range(retries):
        try:
            resp = requests.request(method, url, headers=_headers(api_key), json=payload, timeout=timeout)
            if resp.status_code == 429 or resp.status_code >= 500:
                last = NvidiaError(f"Servicio no disponible o límite alcanzado (HTTP {resp.status_code}).")
            else:
                _check(resp)
                return resp
        except requests.RequestException as exc:
            last = NvidiaError(f"Error de red: {type(exc).__name__}")
        time.sleep(2 ** attempt)
    raise last or NvidiaError("Fallo desconocido.")


def chat(api_key: str, url: str, model: str, messages: list[dict],
         temperature: float = 0.3, max_tokens: int = 2048, timeout: int = 90) -> str:
    """Chat completions compatible con OpenAI; devuelve el texto de la respuesta."""
    payload = {"model": model, "messages": messages, "temperature": temperature,
               "max_tokens": max_tokens, "stream": False}
    data = request("POST", url, api_key, payload, timeout).json()
    try:
        return data["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError) as exc:
        raise NvidiaError("Respuesta inesperada del modelo de chat.") from exc


if __name__ == "__main__":
    print("Módulo cliente listo (requiere API key real para pruebas).")
