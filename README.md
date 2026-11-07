# 🍳 Chef IA

Foto de ingredientes → receta → imagen del plato → paso a paso (Streamlit + NVIDIA build).

## Local
```bash
pip install -r requirements.txt
streamlit run app.py
```
Ingresa tu API key de https://build.nvidia.com/ en la barra lateral (o define `NVIDIA_API_KEY` en `.streamlit/secrets.toml`).

## Despliegue en streamlit.io
1. Sube el proyecto a GitHub (sin `secrets.toml`).
2. En share.streamlit.io: *New app* → repo, rama, archivo `app.py`.
3. (Opcional) *Settings > Secrets*: `NVIDIA_API_KEY = "nvapi-..."`.

## Modelos
Editables en config.py o en "Configuración avanzada". Confirma los IDs exactos en el catálogo de NVIDIA.
