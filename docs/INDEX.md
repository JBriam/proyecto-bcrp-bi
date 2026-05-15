# Indice de documentacion

Este proyecto tiene una documentacion breve pero funcional para ejecutar el pipeline y construir el dashboard.

## Por donde empezar

1. [README.md](../README.md): instalacion, ejecucion del pipeline y uso general.
2. [powerbi_medidas_dax.md](powerbi_medidas_dax.md): medidas DAX y reglas de semaforos.
3. [umbrales_semaforos.md](umbrales_semaforos.md): bandas de alerta y formulas de semaforo.
4. [../config/boletin_prompt_template.md](../config/boletin_prompt_template.md): plantilla para generar boletines con IA.

## Estructura actual

- `config/`: catalogos, KPIs y plantilla de boletin.
- `data/`: datos crudos y procesados.
- `docs/`: guias tecnicas para Power BI y alertas.
- `src/bcrp_dashboard/`: pipeline principal de descarga y transformacion.

## Notas

- Los archivos en `docs/` estan pensados para usuarios que ya tienen Power BI instalado.
- Si solo quieres correr el pipeline, empieza por el README.