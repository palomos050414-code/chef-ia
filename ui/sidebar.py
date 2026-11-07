"""Barra lateral: API key, preferencias, video opcional y configuración avanzada."""
import streamlit as st

from config import DEFAULT_SETTINGS, DIETAS, DIFICULTADES


def _secret_key() -> str:
    try:
        return st.secrets.get("NVIDIA_API_KEY", "")
    except Exception:
        return ""


def render_sidebar() -> dict:
    """Dibuja la barra lateral y devuelve los ajustes del usuario."""
    sb = st.sidebar
    sb.header("⚙️ Ajustes")
    typed = sb.text_input("API key de NVIDIA", type="password",
                          help="Genérala gratis en https://build.nvidia.com/")
    sb.caption("[Obtener API key](https://build.nvidia.com/)")
    api_key = typed.strip() or _secret_key()

    sb.subheader("Preferencias")
    dieta = sb.selectbox("Tipo de dieta", DIETAS)
    porciones = sb.number_input("Porciones", 1, 12, 2)
    dificultad = sb.selectbox("Dificultad", DIFICULTADES)
    video = sb.toggle("Generar video corto (opcional, lento)", value=False)

    cfg = dict(DEFAULT_SETTINGS)
    with sb.expander("Configuración avanzada"):
        labels = {"chat_url": "URL chat", "vision_model": "Modelo de visión",
                  "recipe_model": "Modelo de receta (DeepSeek)", "image_url": "URL imagen",
                  "video_url": "URL video", "status_url": "URL estado (polling)"}
        for k, label in labels.items():
            cfg[k] = st.text_input(label, value=cfg[k], key=f"cfg_{k}").strip()

    return {"api_key": api_key, "dieta": dieta, "porciones": int(porciones),
            "dificultad": dificultad, "video": video, "cfg": cfg}


if __name__ == "__main__":
    print("Ejecuta con: streamlit run app.py")
