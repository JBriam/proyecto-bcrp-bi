# Medidas DAX para Dashboard Macro Perú

## Contexto
Estas medidas asumen una estructura de datos:
- Tabla `Fact_Valores` con columnas: `date`, `value`, `mom_pct`, `yoy_pct`, `series_code`, `series_name`, `unit`, `theme`.
- Tabla `Dim_Series` con: `series_code` (PK), `series_name`, `unit`, `theme`, `priority`.
- Tabla `Dim_Date` con: `date` (PK), `year`, `month`, `month_name`, `quarter`.

---

## MEDIDAS GLOBALES (reutilizables)

### Último valor disponible
```dax
Valor_Ultimo = 
CALCULATE(
    SUM(Fact_Valores[value]),
    LASTDATE(Dim_Date[date])
)
```

### Fecha del último valor
```dax
Fecha_Ultimo = 
MAX(Fact_Valores[date])
```

### Cantidad de observaciones cargadas
```dax
Obs_Count = 
COUNTA(Fact_Valores[date])
```

---

## MEDIDAS DE VARIACION

### Variación Mensual (%)
```dax
Variacion_MoM_pct = 
AVERAGE(Fact_Valores[mom_pct])
```

### Variación Interanual (%)
```dax
Variacion_YoY_pct = 
AVERAGE(Fact_Valores[yoy_pct])
```

### Variación vs Periodo Anterior (método alternativo)
```dax
Variacion_vs_Anterior = 
VAR FechaActual = MAX(Dim_Date[Date])
VAR FechaAnterior =
    CALCULATE(
        MAX(Dim_Date[Date]),
        FILTER(ALL(Dim_Date[Date]), Dim_Date[Date] < FechaActual)
    )
VAR ValorActual = [Valor_Ultimo]
VAR ValorAnterior = 
    CALCULATE(
        SUM(Fact_Valores[value]),
        KEEPFILTERS(Dim_Date[Date] = FechaAnterior)
    )
RETURN
    DIVIDE(ValorActual - ValorAnterior, ValorAnterior)
```

---

## MEDIDAS DE MEDIAS MOVILES

### Media Móvil 3 Meses (últimas 3 obs)
```dax
MA3M_Valor = 
AVERAGEX(
    TAIL(
        ALL(Dim_Date[date]),
        3
    ),
    CALCULATE(SUM(Fact_Valores[value]))
)
```

### Media Móvil 12 Meses (últimas 12 obs)
```dax
MA12M_Valor = 
AVERAGEX(
    TAIL(
        ALL(Dim_Date[date]),
        12
    ),
    CALCULATE(SUM(Fact_Valores[value]))
)
```

### Desviación vs MA12M
```dax
Delta_vs_MA12M = 
DIVIDE(
    [Valor_Ultimo] - [MA12M_Valor],
    [MA12M_Valor]
)
```

---

## MEDIDAS ESPECÍFICAS POR TEMA

### INFLACION

#### Inflación Interanual Principal
```dax
Inflacion_YoY = 
CALCULATE(
    [Variacion_YoY_pct],
    Dim_Series[series_code] = "PN01273PM"
)
```

#### Inflación Subyacente (Bienes)
```dax
Inflacion_Subyacente_Bienes = 
CALCULATE(
    [Variacion_YoY_pct],
    Dim_Series[series_code] = "PN01296PM"
)
```

#### Inflación No Subyacente (Alimentos)
```dax
Inflacion_NoSubyacente_Alimentos = 
CALCULATE(
    [Variacion_YoY_pct],
    Dim_Series[series_code] = "PN01308PM"
)
```

#### Bandera de Inflación (Semáforo)
```dax
Flag_Inflacion = 
VAR YoY = [Inflacion_YoY]
RETURN
    SWITCH(
        TRUE(),
        YoY > 0.035, "🔴 Alerta (>3.5%)",
        YoY > 0.025, "🟡 Atención (2.5%-3.5%)",
        "🟢 Normal (≤2.5%)"
    )
```

#### Gap vs Meta Inflación (meta = 2.0%)
```dax
Inflacion_Gap_vs_Meta = 
VAR Meta = 0.02
RETURN
    [Inflacion_YoY] - Meta
```

---

### POLITICA MONETARIA

#### Tasa de Referencia BCRP
```dax
Tasa_Referencia = 
CALCULATE(
    [Valor_Ultimo],
    Dim_Series[series_code] = "PD04722MM"
)
```

#### Cambio en Tasa Referencia (últimas 2 obs)
```dax
Delta_Tasa_Referencia = 
VAR FechaActual = MAX(Dim_Date[Date])
VAR FechaAnterior =
    CALCULATE(
        MAX(Dim_Date[Date]),
        FILTER(ALL(Dim_Date[Date]), Dim_Date[Date] < FechaActual)
    )
VAR TasaActual = [Tasa_Referencia]
VAR TasaAnterior = 
    CALCULATE(
        [Valor_Ultimo],
        KEEPFILTERS(Dim_Date[Date] = FechaAnterior),
        Dim_Series[series_code] = "PD04722MM"
    )
RETURN
    TasaActual - TasaAnterior
```

---

### TIPO DE CAMBIO

#### Tipo de Cambio Último Diario
```dax
TC_Diario_Ultimo = 
CALCULATE(
    [Valor_Ultimo],
    Dim_Series[series_code] = "PD04637PD"
)
```

#### Tipo de Cambio Promedio Mensual
```dax
TC_Promedio_Mensual = 
CALCULATE(
    [Valor_Ultimo],
    Dim_Series[series_code] = "PN01205PM"
)
```

#### Variación TC Últimos 3 Meses (%)
```dax
TC_Variacion_3M_pct = 
CALCULATE(
    [Delta_vs_MA12M],
    Dim_Series[series_code] = "PN01205PM"
) * 100
```

---

### ACTIVIDAD (PBI)

#### PBI Índice Últim Mes
```dax
PBI_Indice = 
CALCULATE(
    [Valor_Ultimo],
    Dim_Series[series_code] = "PN01770AM"
)
```

#### PBI Variación Interanual (%)
```dax
PBI_YoY_pct = 
CALCULATE(
    [Variacion_YoY_pct],
    Dim_Series[series_code] = "PN01728AM"
) * 100
```

#### PBI Variación Mensual Desestacionalizado (%)
```dax
PBI_MoM_Desestacionalizado = 
CALCULATE(
    [Variacion_YoY_pct],
    Dim_Series[series_code] = "PN01731AM"
) * 100
```

#### Bandera PBI Crecimiento
```dax
Flag_PBI = 
VAR PBI_YoY = [PBI_YoY_pct]
RETURN
    SWITCH(
        TRUE(),
        PBI_YoY < 0, "🔴 Contracción",
        PBI_YoY < 0.02, "🟡 Crecimiento Bajo",
        "🟢 Crecimiento Positivo"
    )
```

---

### EMPLEO

#### Tasa de Desempleo Lima (%)
```dax
Tasa_Desempleo = 
CALCULATE(
    [Valor_Ultimo],
    Dim_Series[series_code] = "PN38063GM"
)
```

#### PEA Lima (miles de personas)
```dax
PEA_Lima = 
CALCULATE(
    [Valor_Ultimo],
    Dim_Series[series_code] = "PN38050GM"
)
```

#### Puestos Formales (miles)
```dax
Puestos_Formales = 
CALCULATE(
    [Valor_Ultimo],
    Dim_Series[series_code] = "PN31879GM"
)
```

#### Puestos Formales Variación Interanual (%)
```dax
Puestos_Formales_YoY_pct = 
CALCULATE(
    [Variacion_YoY_pct],
    Dim_Series[series_code] = "PN31879GM"
) * 100
```

#### Ingreso Promedio Formal (S/)
```dax
Ingreso_Promedio_Formal = 
CALCULATE(
    [Valor_Ultimo],
    Dim_Series[series_code] = "PN31883GM"
)
```

---

### SECTOR EXTERNO

#### Exportaciones FOB (millones US$)
```dax
Exportaciones_USD = 
CALCULATE(
    [Valor_Ultimo],
    Dim_Series[series_code] = "PN38714BM"
)
```

#### Importaciones FOB (millones US$)
```dax
Importaciones_USD = 
CALCULATE(
    [Valor_Ultimo],
    Dim_Series[series_code] = "PN38718BM"
)
```

#### Balanza Comercial FOB (millones US$)
```dax
Balanza_Comercial_USD = 
CALCULATE(
    [Valor_Ultimo],
    Dim_Series[series_code] = "PN38723BM"
)
```

#### Saldo Comercial como % de Importaciones
```dax
Saldo_pct_Importaciones = 
DIVIDE(
    [Balanza_Comercial_USD],
    [Importaciones_USD]
)
```

#### Términos de Intercambio Variación (%)
```dax
Terminos_Intercambio_Variacion = 
CALCULATE(
    [Variacion_YoY_pct],
    Dim_Series[series_code] = "PN38726BM"
) * 100
```

---

## MEDIDAS PARA TABLAS Y COMPARATIVAS

### Resumen por Serie (para tabla con valores y variaciones)
```dax
Resumen_Series = 
CONCATENATEX(
    VALUES(Dim_Series[series_name]),
    Dim_Series[series_name] & ": " & FORMAT([Valor_Ultimo], "0.00") & " (" & FORMAT([Variacion_YoY_pct], "0.0%") & " YoY)",
    ", "
)
```

### Ranking de Variación Interanual (top N series)
```dax
Top_Variaciones_YoY = 
RANKX(
    ALL(Dim_Series[series_code]),
    [Variacion_YoY_pct],,
    DESC
)
```

---

## MEDIDAS PARA NARRATIVA AUTOMATICA (IA)

### Texto de Tendencia (Resumen)
```dax
Texto_Tendencia = 
VAR YoY = [Variacion_YoY_pct]
VAR MoM = [Variacion_MoM_pct]
RETURN
    IF(
        YoY > 0,
        IF(MoM > 0, "Tendencia alcista confirmada", "Tendencia alcista pero desaceleración mensual"),
        IF(MoM > 0, "Tendencia bajista pero recuperación mensual", "Tendencia bajista confirmada")
    )
```

### JSON para API IA (versión simulada en texto)
```dax
JSON_Resumen = 
CONCATENATEX(
    VALUES(Dim_Series[series_code]),
    "{""code"": """ & Dim_Series[series_code] & """, ""value"": " & 
    TEXT([Valor_Ultimo], "0.00") & ", ""yoy_pct"": " & 
    TEXT([Variacion_YoY_pct], "0.00") & ", ""trend"": """ & 
    [Texto_Tendencia] & """}",
    ", "
)
```

---

## NOTAS DE IMPLEMENTACION

1. **Contexto de filtro:** Todas las medidas respetan los filtros activos (date, theme, series_code, etc.).
2. **Unidades:** Asegúrate de que el formato de número sea apropiado (%, decimales, moneda).
3. **Tooltips:** En cada visual, configura tooltips dinámicos que muestren `[Variacion_YoY_pct]`, `[MA3M_Valor]`, `Fecha_Ultimo`, etc.
4. **Actualización:** Estas medidas se recalculan automáticamente cuando actualizas `data/processed/bcrp_consolidado.csv` en tu modelo.
5. **Performance:** Si tienes >100k filas, considera agregar una columna calculada `YearMonth` en Dim_Date para optimizar medias móviles.

---

## CHECKLIST ANTES DE PUBLICAR

- [ ] Carga `data/processed/bcrp_consolidado.csv` en Power BI.
- [ ] Crea Dim_Date a partir de la columna `date` (usa Data > New Table > Calendar).
- [ ] Establece relación Fact_Valores → Dim_Date por `date`.
- [ ] Establece relación Fact_Valores → Dim_Series por `series_code`.
- [ ] Prueba cada medida en una tarjeta con filtros activos.
- [ ] Verifica que números y unidades se muestran correctamente.
- [ ] Habilita vista de datos para revisar valores crudos en tooltips.
- [ ] Publica y configura refresco automático (diario o semanal).
