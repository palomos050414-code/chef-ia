"""Chef IA - punto de entrada. Solo orquesta la UI; la lógica vive en services/."""
import hashlib

import streamlit as st

from config import ALLOWED_EXTENSIONS, JPEG_QUALITY, MAX_IMAGE_SIDE, MAX_UPLOAD_MB
from services.image_service import generate_dish_image
from services.nvidia_client import AuthError, NvidiaError
from services.recipe_service import generate_recipe
from services.video_service import generate_video
from services.vision_service import detect_ingredients
from ui.components import render_ingredient_editor, render_recipe
from ui.sidebar import render_sidebar
from utils.image_utils import prepare_image, validate_upload

st.set_page_config(page_title="Chef IA", page_icon="🍳", layout="wide")
st.markdown("""<style>
@media (max-width: 640px){ .block-container{padding:1rem .6rem;} h1{font-size:1.6rem;} }
</style>""", unsafe_allow_html=True)

S = st.session_state
for k, v in {"ingredients": None, "img_hash": None, "recipe": None, "dish_img": None, "video": None}.items():
    S.setdefault(k, v)


def fail(exc: Exception) -> None:
    st.error(f"❌ {exc}" if isinstance(exc, NvidiaError) else f"❌ Error inesperado: {type(exc).__name__}")


st.title("🍳 Chef IA")
st.caption("Fotografía tus ingredientes y obtén una receta, una imagen del plato y el paso a paso.")
opts = render_sidebar()
api_key, cfg = opts["api_key"], opts["cfg"]

if not api_key:
    st.info("🔑 Ingresa tu API key de NVIDIA en la barra lateral para comenzar "
            "(la obtienes en https://build.nvidia.com/).")
    st.stop()

if st.button("🔄 Empezar de nuevo"):
    for k in ("ingredients", "img_hash", "recipe", "dish_img", "video", "ing_editor"):
        S.pop(k, None)
    st.rerun()

# 1) Entrada de imagen
tab_cam, tab_up = st.tabs(["📷 Tomar foto", "🖼️ Subir imagen"])
with tab_cam:
    cam = st.camera_input("Fotografía tus ingredientes")
with tab_up:
    up = st.file_uploader("Sube una imagen", type=sorted(ALLOWED_EXTENSIONS))
source = cam or up

if source is not None:
    err = validate_upload(source.name or "foto.jpg", source.size, ALLOWED_EXTENSIONS, MAX_UPLOAD_MB)
    if err:
        st.error(err)
    else:
        raw = source.getvalue()
        h = hashlib.md5(raw).hexdigest()
        if S.img_hash != h and st.button("🔍 Identificar ingredientes", type="primary"):
            try:
                with st.spinner("Analizando la imagen..."):
                    S.ingredients = detect_ingredients(
                        api_key, prepare_image(raw, MAX_IMAGE_SIDE, JPEG_QUALITY), cfg)
                S.img_hash, S.recipe, S.dish_img, S.video = h, None, None, None
                S.pop("ing_editor", None)
            except AuthError as exc:
                st.error(f"🔒 {exc}")
            except Exception as exc:
                fail(exc)

# 2) Ingredientes editables -> receta
if S.ingredients:
    st.subheader("🥕 Ingredientes detectados (edítalos si es necesario)")
    confirmed = render_ingredient_editor(S.ingredients)
    if st.button("👨‍🍳 Generar receta", type="primary", disabled=not confirmed):
        try:
            with st.spinner("Creando la receta con DeepSeek..."):
                S.recipe = generate_recipe(api_key, confirmed, opts["dieta"], opts["porciones"],
                                           opts["dificultad"], cfg)
        except AuthError as exc:
            st.error(f"🔒 {exc}")
        except Exception as exc:
            fail(exc)
        if S.recipe:
            S.dish_img = S.video = None
            try:
                with st.spinner("Generando la imagen del plato..."):
                    S.dish_img = generate_dish_image(api_key, S.recipe["prompt_imagen"], cfg)
            except Exception as exc:
                fail(exc)
            if opts["video"]:
                try:
                    with st.spinner("Generando video (puede tardar varios minutos)..."):
                        S.video = generate_video(api_key, S.recipe["prompt_imagen"], cfg)
                except Exception as exc:
                    fail(exc)

# 3) Resultado
if S.recipe:
    st.divider()
    render_recipe(S.recipe, S.dish_img, S.video)
