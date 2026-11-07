"""Componentes de render: ingredientes, receta, pasos y descarga."""
import streamlit as st


def render_ingredient_editor(ingredients: list[dict]) -> list[str]:
    """Tabla editable (agregar/quitar filas). Devuelve nombres confirmados."""
    edited = st.data_editor(
        ingredients, num_rows="dynamic", use_container_width=True, key="ing_editor",
        column_config={"nombre": st.column_config.TextColumn("Ingrediente", required=True),
                       "cantidad": st.column_config.TextColumn("Cantidad")})
    rows = edited if isinstance(edited, list) else edited.to_dict("records")
    return [str(r.get("nombre") or "").strip() for r in rows if str(r.get("nombre") or "").strip()]


def recipe_to_markdown(r: dict) -> str:
    """Convierte la receta a Markdown para descargar."""
    lines = [f"# {r['nombre']}", "", r["descripcion"], "",
             f"**Tiempo:** {r['tiempo_total']} | **Dificultad:** {r['dificultad']} | **Porciones:** {r['porciones']}",
             "", "## Ingredientes"]
    for i in r["ingredientes"]:
        lines.append(f"- {i.get('cantidad', '')} {i.get('nombre', '')}" + (" (falta)" if i.get("falta") else ""))
    lines += ["", "## Preparación"]
    for n, p in enumerate(r["pasos"], 1):
        lines.append(f"{p.get('numero', n)}. {p.get('instruccion', '')} ({p.get('tiempo', '')})")
        if p.get("consejo"):
            lines.append(f"   - Consejo: {p['consejo']}")
    return "\n".join(lines)


def render_recipe(r: dict, image: bytes | None, video: bytes | None) -> None:
    """Muestra receta, imagen/placeholder, ingredientes, pasos y botón de descarga."""
    st.header(r["nombre"])
    col_img, col_info = st.columns([1, 1])
    with col_img:
        if image:
            st.image(image, use_container_width=True)
        else:
            st.info("🍽️ No se pudo generar la imagen del plato, pero la receta está lista.")
        if video:
            st.video(video)
    with col_info:
        st.write(r["descripcion"])
        st.markdown(f"⏱️ **{r['tiempo_total']}** · 🎯 **{r['dificultad']}** · 🍴 **{r['porciones']} porciones**")
        st.subheader("Ingredientes")
        for i in r["ingredientes"]:
            flag = " ⚠️ *falta*" if i.get("falta") else ""
            st.markdown(f"- {i.get('cantidad', '')} {i.get('nombre', '')}{flag}")

    st.subheader("Paso a paso")
    for n, p in enumerate(r["pasos"], 1):
        with st.expander(f"Paso {p.get('numero', n)} · {p.get('tiempo', '')}", expanded=(n == 1)):
            st.checkbox("Completado", key=f"paso_{n}")
            st.write(p.get("instruccion", ""))
            if p.get("consejo"):
                st.caption(f"💡 {p['consejo']}")
    st.download_button("⬇️ Descargar receta (.md)", recipe_to_markdown(r),
                       file_name="receta.md", mime="text/markdown")


if __name__ == "__main__":
    print(recipe_to_markdown({"nombre": "Test", "descripcion": "d", "tiempo_total": "5 min",
          "dificultad": "fácil", "porciones": 1, "ingredientes": [{"nombre": "huevo", "cantidad": "2"}],
          "pasos": [{"numero": 1, "instruccion": "Cocina.", "tiempo": "5 min", "consejo": ""}]}))
