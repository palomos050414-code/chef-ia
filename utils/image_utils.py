"""Utilidades de imagen: validar, redimensionar, comprimir y codificar."""
import base64
import io

from PIL import Image, ImageOps


def validate_upload(name: str, size: int, allowed: set[str], max_mb: int) -> str | None:
    """Devuelve un mensaje de error si el archivo no es válido; None si está bien."""
    ext = name.rsplit(".", 1)[-1].lower() if "." in name else ""
    if ext not in allowed:
        return f"Formato no permitido (.{ext}). Usa: {', '.join(sorted(allowed))}."
    if size > max_mb * 1024 * 1024:
        return f"El archivo supera {max_mb} MB."
    return None


def prepare_image(data: bytes, max_side: int = 1024, quality: int = 85) -> bytes:
    """Corrige orientación, redimensiona (lado máx.) y comprime a JPEG."""
    img = Image.open(io.BytesIO(data))
    img = ImageOps.exif_transpose(img).convert("RGB")
    img.thumbnail((max_side, max_side))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=quality, optimize=True)
    return buf.getvalue()


def to_data_url(jpeg_bytes: bytes) -> str:
    """Codifica bytes JPEG como data URL base64."""
    return "data:image/jpeg;base64," + base64.b64encode(jpeg_bytes).decode()


def b64_to_bytes(b64: str) -> bytes:
    """Decodifica base64 (con o sin prefijo data:)."""
    if "," in b64[:100]:
        b64 = b64.split(",", 1)[1]
    return base64.b64decode(b64)


if __name__ == "__main__":
    demo = io.BytesIO()
    Image.new("RGB", (2000, 1000), "red").save(demo, format="PNG")
    out = prepare_image(demo.getvalue())
    print("OK", Image.open(io.BytesIO(out)).size, validate_upload("a.gif", 10, {"jpg"}, 8))
