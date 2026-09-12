"""One-off live probe of the three AI4Bharat HF endpoints.

Verifies the actual request/response formats assumed by
app/services/language_service.py. Reads the token from the repo .env; never
prints it. Not part of the test suite — run manually:
    python3 probe_hf_live.py
"""
import sys
import base64
import pathlib

import httpx

TOKEN = ""
env = pathlib.Path(__file__).resolve().parents[1] / ".env"
for line in env.read_text().splitlines():
    if line.startswith("HUGGINGFACE_API_TOKEN="):
        TOKEN = line.split("=", 1)[1].strip()
if not TOKEN:
    sys.exit("No HUGGINGFACE_API_TOKEN in .env")

# Inference Providers router (api-inference.huggingface.co is retired).
BASE = "https://router.huggingface.co/hf-inference/models"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}


def show(label, resp, n=400):
    print(f"--- {label} ---")
    print("status:", resp.status_code)
    print("content-type:", resp.headers.get("content-type"))
    if "audio" in (resp.headers.get("content-type") or ""):
        print("body: <binary, len", len(resp.content), ">")
    else:
        print("body:", resp.text[:n])
    print()


with httpx.Client(timeout=120) as c:
    # 1. Translation: IndicTrans2
    r = c.post(
        f"{BASE}/ai4bharat/indictrans2-indic-indic-1B",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={
            "inputs": "নমস্কাৰ, আজি কেনে আছে?",
            "parameters": {"src_lang": "asm_Beng", "tgt_lang": "eng_Latn"},
        },
    )
    show("IndicTrans2 (asm->eng, params dict)", r)

    # If 4xx, try the alternate payload shape (inputs only).
    if r.status_code >= 400:
        r2 = c.post(
            f"{BASE}/ai4bharat/indictrans2-indic-indic-1B",
            headers={**HEADERS, "Content-Type": "application/json"},
            json={"inputs": "নমস্কাৰ, আজি কেনে আছে?"},
        )
        show("IndicTrans2 (inputs only)", r2)

    # 2. ASR: Indic Conformer (tiny WAV header as a shape probe)
    tiny_wav = base64.b64decode(
        "UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQAAAAA="
    )
    r = c.post(
        f"{BASE}/ai4bharat/indic-conformer-600m-multilingual",
        headers={**HEADERS, "Content-Type": "application/octet-stream"},
        content=tiny_wav,
    )
    show("Indic Conformer ASR (binary wav)", r)

    # 3. TTS: Indic Parler-TTS
    r = c.post(
        f"{BASE}/ai4bharat/indic-parler-tts",
        headers={**HEADERS, "Content-Type": "application/json"},
        json={
            "inputs": "নমস্কাৰ",
            "parameters": {"lang": "asm_Beng", "gender": "female"},
        },
    )
    show("Indic Parler-TTS (params lang/gender)", r)

    # If 4xx, try inputs-only format
    if r.status_code >= 400:
        r2 = c.post(
            f"{BASE}/ai4bharat/indic-parler-tts",
            headers={**HEADERS, "Content-Type": "application/json"},
            json={"inputs": "নমস্কাৰ"},
        )
        show("Indic Parler-TTS (inputs only)", r2)
