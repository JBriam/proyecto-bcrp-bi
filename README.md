# Dashboard Macroeconomico Peru - Base Python + BCRP

Este proyecto contiene una base para:

- Consumir series del API del BCRP.
- Limpiar y estandarizar datos con Pandas.
- Generar archivos consolidados para Power BI.
- Preparar insumos para un boletin economico con IA.

## 1) Estructura

- `config/series_bcrp.csv`: catalogo de series a descargar.
- `config/powerbi_kpis.csv`: definicion de KPI ejecutivos sugeridos.
- `config/boletin_prompt_template.md`: plantilla de prompt para generar boletines con IA.
- `data/raw/`: payloads crudos del API.
- `data/processed/`: tablas limpias y consolidadas.
- `src/bcrp_dashboard/`: codigo del pipeline.
- `docs/INDEX.md`: mapa rapido de la documentacion disponible.

## 2) Requisitos

- Python 3.10+
- Git

## 3) Clonar proyecto

```bash
git clone <URL_DEL_REPOSITORIO>
cd proyecto-bcrp-bi
```

## 4) Crear entorno e instalar dependencias

### Windows (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### macOS / Linux (bash/zsh)

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5) Configuracion

### Windows (PowerShell)

```powershell
Copy-Item .env.example .env
```

### macOS / Linux (bash/zsh)

```bash
cp .env.example .env
```

Si necesitas cambiar rutas o endpoint, edita `.env`.

## 6) Ejecutar pipeline

Ejecuta los comandos desde la carpeta raiz del proyecto.

```powershell
python src/bcrp_dashboard/main.py
```

Salida esperada:

- Un archivo de estado ETL en `data/processed/etl_status.csv`
- Un archivo por serie en `data/processed/*.parquet`
- Consolidado en:
  - `data/processed/bcrp_consolidado.parquet`
  - `data/processed/bcrp_consolidado.csv`

## 7) Generar insumo para boletin con IA

```powershell
python src/bcrp_dashboard/build_boletin_input.py
```

Salida esperada:

- `data/processed/boletin_input.json`

## 8) Uso en Power BI

1. Obtener datos -> Texto/CSV (o Parquet con conector).
2. Cargar `data/processed/bcrp_consolidado.csv`.
3. Crear visuales con `date`, `series_name`, `value`, `mom_pct`, `yoy_pct`, `theme`.
4. Crear tarjetas KPI usando `config/powerbi_kpis.csv` como referencia.

## 9) Generar Boletines Automáticos con IA

Una vez que tu dashboard esté en Power BI:

1. **Genera el insumo JSON:**
```powershell
python src/bcrp_dashboard/build_boletin_input.py
```

Salida: `data/processed/boletin_input.json` (resumen de todas las series con últimas variaciones)

2. **Usa el prompt template:**
   - Archivo: [config/boletin_prompt_template.md](config/boletin_prompt_template.md)
   - Alimenta un LLM (OpenAI, Azure OpenAI, Gemini, etc.)
   - Genera narrativa ejecutiva automática

3. **Integración recomendada:**
   - Power Automate: leer JSON y enviar a LLM
   - Exportar PDF del reporte + boletín en correo
   - Scheduler: ejecutar diariamente o semanalmente

## 10) ENTREGA FINAL

- 22 series macroeconómicas descargadas
- Datos consolidados y listos (CSV + Parquet)
- 30+ medidas DAX
- Umbrales y semáforos configurados

## 11) Próximos pasos sugeridos

- Incorporar series del INEI (desempleo regional, etc.) al mismo modelo.
- Agregar validaciones de calidad de datos (outliers, cambios bruscos).
- Automatizar ejecución diaria/semanal con Task Scheduler o GitHub Actions.
- Conectar refresco de datos en Power BI (cada 6-12 horas).
- Configurar alertas en Power Automate si indicadores cruzan umbrales críticos.
