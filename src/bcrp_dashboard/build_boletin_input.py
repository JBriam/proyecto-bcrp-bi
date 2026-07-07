from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
import resend
from groq import Groq

PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_FILE = PROJECT_ROOT / "data/processed/bcrp_consolidado.parquet"
OUTPUT_FILE = PROJECT_ROOT / "data/processed/boletin_input.json"

# Configurar clientes con sus respectivas API Keys desde las variables de entorno
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
resend.api_key = os.environ.get("RESEND_API_KEY")


def _trend_from_changes(mom: float | None, yoy: float | None) -> str:
    if pd.notna(yoy):
        if yoy > 0:
            return "al_alza"
        if yoy < 0:
            return "a_la_baja"
    if pd.notna(mom):
        if mom > 0:
            return "al_alza"
        if mom < 0:
            return "a_la_baja"
    return "estable"


def generar_boletin(payload: dict) -> str:
    system_prompt = """
Eres un analista macroeconómico de Perú.

Redacta un boletín ejecutivo estructurado en formato HTML limpio (sin etiquetas de bloque completas como <html> o <body>, solo etiquetas de contenido como <h1>, <h2>, <p>, <ul>, <li>, <table>, <tr>, <td>, <th>). Utiliza EXCLUSIVAMENTE los datos del JSON proporcionado.

Reglas obligatorias:
1. No inventar cifras.
2. Si falta un dato, indicar "dato no disponible".
3. Explicar cambios relevantes con lenguaje claro y profesional.
4. Mantener el boletín completamente en español.

Estructura de salida en HTML:
- <h1> Titular ejecutivo (1 línea)
- <h2> Resumen (máximo 80 palabras)
- <h2> Hallazgos clave (3 bullets)
- <h2> Riesgos y monitoreo (2 bullets)
- <h2> Anexo breve de cifras (tabla compacta)

No utilices información externa al JSON.
"""

    user_prompt = (
        "Datos para elaborar el boletín:\n\n"
        + json.dumps(payload, ensure_ascii=False, indent=2)
    )

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        temperature=0.3,
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_prompt,
            },
        ],
    )

    return response.choices[0].message.content


def enviar_correo_resend(html_content: str, destinatario: str) -> None:
    if not resend.api_key:
        print("Error: No se configuró la variable de entorno RESEND_API_KEY.")
        return

    # Estilos CSS básicos para mejorar la presentación del boletín en el gestor de correos
    html_styled = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333333; line-height: 1.6; max-width: 600px; margin: 0 auto; padding: 20px;">
        {html_content}
      </body>
    </html>
    """

    try:
        # En la capa gratuita sin dominio propio, el remitente obligatorio es 'onboarding@resend.dev'
        resend.Emails.send({
            "from": "onboarding@resend.dev",
            "to": destinatario,
            "subject": "Boletín Económico BCRP",
            "html": html_styled
        })
        print(f"Correo enviado exitosamente vía Resend a {destinatario}")
    except Exception as e:
        print(f"Error al enviar el correo con Resend: {e}")


def build_boletin_input(
    input_file: Path = INPUT_FILE,
    output_file: Path = OUTPUT_FILE,
) -> None:
    if not input_file.exists():
        raise FileNotFoundError(
            f"No se encontró {input_file}. Ejecuta primero el pipeline."
        )

    df = pd.read_parquet(input_file)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    summary_rows: list[dict[str, object]] = []

    for code, group in df.groupby("series_code", sort=True):
        group = group.sort_values("date")
        latest = group.iloc[-1]

        summary_rows.append(
            {
                "series_code": code,
                "series_name": latest.get("series_name", ""),
                "theme": latest.get("theme", ""),
                "unit": latest.get("unit", ""),
                "last_date": (
                    latest["date"].strftime("%Y-%m-%d")
                    if pd.notna(latest["date"])
                    else None
                ),
                "last_value": (
                    None
                    if pd.isna(latest.get("value"))
                    else float(latest["value"])
                ),
                "mom_pct": (
                    None
                    if pd.isna(latest.get("mom_pct"))
                    else float(latest["mom_pct"])
                ),
                "yoy_pct": (
                    None
                    if pd.isna(latest.get("yoy_pct"))
                    else float(latest["yoy_pct"])
                ),
                "trend": _trend_from_changes(
                    latest.get("mom_pct"),
                    latest.get("yoy_pct"),
                ),
            }
        )

    payload = {
        "source": "BCRP",
        "generated_at": pd.Timestamp.now(tz="UTC").strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "series_summary": summary_rows,
    }

    print("\nGenerando boletín con IA...\n")

    try:
        boletin_html = generar_boletin(payload)
        
        # Envío directo usando la API de Resend al destinatario solicitado
        enviar_correo_resend(boletin_html, "maryenaguilarzuniga@gmail.com")
        
    except Exception as e:
        print(f"Error al generar el boletín con Groq: {e}")

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"\nArchivo JSON generado: {output_file}")
    print(f"Total de series: {len(summary_rows)}")


if __name__ == "__main__":
    build_boletin_input()