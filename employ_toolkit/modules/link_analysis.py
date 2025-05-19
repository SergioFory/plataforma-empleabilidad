import uuid
from pathlib import Path
from datetime import date

import requests

OUTPUT_DIR = Path("workspace")
OUTPUT_DIR.mkdir(exist_ok=True)


class DownloadError(Exception):
    """Se lanza cuando la descarga del informe falla."""


def _make_filename(client_name: str) -> Path:
    return OUTPUT_DIR / f"{client_name}_{uuid.uuid4().hex[:6]}_linkedin.pdf"


def download_report(url: str, client_name: str) -> Path:
    """
    Llama a la API pública de reepl.io. Devuelve Path al PDF.
    Lanza DownloadError si algo falla.
    """
    endpoint = "https://reepl.io/free-tools/linkedin-profile-analysis"
    try:
        resp = requests.post(endpoint, json={"url": url}, timeout=30)
        resp.raise_for_status()
        if "application/pdf" not in resp.headers.get("Content-Type", ""):
            raise DownloadError("La API no devolvió un PDF.")
    except Exception as e:
        raise DownloadError(str(e)) from e

    filename = _make_filename(client_name)
    filename.write_bytes(resp.content)
    return filename
