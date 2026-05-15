# Umbrales y Semáforos - Dashboard Macro Perú

## TABLA DE REFERENCIA RÁPIDA

Usa esta tabla para configurar bandas de color, alertas y flags en Power BI.

| Indicador | Unidad | Normal (🟢) | Atención (🟡) | Alerta (🔴) | Fuente |
|-----------|--------|------------|---------------|------------|--------|
| **INFLACION** |
| IPC Lima YoY | % | ≤2.5% | 2.5%-3.5% | >3.5% | PN01273PM |
| IPC Subyacente | % | ≤2.0% | 2.0%-3.0% | >3.0% | PN01296PM |
| IPC Alimentos | % | ≤3.0% | 3.0%-4.0% | >4.0% | PN01308PM |
| **POLITICA MONETARIA** |
| Tasa Referencia | pp | -0.5 a +0.5 cambio | ±0.5-1.0 pp | >1.0 pp cambio | PD04722MM |
| Tasa vs Meta | pp | dentro meta | ±0.5 pp | >0.5 pp fuera | Calculada |
| **TIPO DE CAMBIO** |
| TC Promedio | S$/USD | 3.40-3.60 | 3.30-3.40 o 3.60-3.70 | <3.30 o >3.70 | PN01205PM |
| TC Variación 3M | % | ±3% | ±3-6% | >6% | Calculada |
| **ACTIVIDAD** |
| PBI YoY | % | 2.0%-3.5% | 0.5%-2.0% o 3.5%-5.0% | <0.5% o >5.0% | PN01728AM |
| PBI MoM Desest. | % | 0.5%-1.0% | 0-0.5% o 1.0%-1.5% | <0% o >1.5% | PN01731AM |
| PBI Índice | pts | >119 | 116-119 | <116 | PN01770AM |
| **EMPLEO** |
| Tasa Desempleo | % | 4.5%-5.5% | 5.5%-6.0% | >6.0% o <4.5% | PN38063GM |
| Puestos Formales YoY | % | >1.0% | -1.0% a 1.0% | <-1.0% | PN31879GM |
| Ingreso Real YoY | % | >0% | -1% a 0% | <-1.0% | PN37696PM |
| **SECTOR EXTERNO** |
| Saldo Comercial | MM US$ | >0 (superávit) | -200 a 0 | <-200 | PN38723BM |
| Balanza % Importac | % | >2% | 0%-2% | <0% (déficit) | Calculada |
| Términos Intercambio | var% | -2% a +2% | -5% a -2% o +2% a +5% | <-5% o >+5% | PN38726BM |

---

## SEMAFOROS POR PAGINA

### PÁGINA 1: Resumen Ejecutivo

#### Inflación
- **Rojo (🔴):** YoY > 3.5%
- **Naranja (🟡):** YoY 2.5-3.5%
- **Verde (🟢):** YoY ≤ 2.5%

**Fórmula DAX:**
```dax
Flag_Inflacion = 
SWITCH(TRUE(),
    [Inflacion_YoY] > 0.035, "🔴 Alerta",
    [Inflacion_YoY] > 0.025, "🟡 Atención",
    "🟢 Normal"
)
```

#### Tipo de Cambio
- **Rojo (🔴):** TC > 3.70 S/USD (depreciación alta)
- **Naranja (🟡):** 3.60-3.70 S/USD
- **Verde (🟢):** 3.40-3.60 S/USD (banda normal)

**Fórmula DAX:**
```dax
Flag_TC = 
SWITCH(TRUE(),
    [TC_Promedio_Mensual] > 3.70, "🔴 Depreciación",
    [TC_Promedio_Mensual] > 3.60, "🟡 Presión",
    [TC_Promedio_Mensual] < 3.40, "🟡 Apreciación",
    "🟢 Normal"
)
```

#### PBI
- **Rojo (🔴):** YoY < 0.5% (estancamiento)
- **Naranja (🟡):** YoY 0.5-2.0% (débil) o > 3.5% (muy fuerte)
- **Verde (🟢):** YoY 2.0-3.5%

**Fórmula DAX:**
```dax
Flag_PBI = 
SWITCH(TRUE(),
    [PBI_YoY_pct] < 0.005, "🔴 Contracción",
    [PBI_YoY_pct] < 0.020, "🟡 Débil",
    [PBI_YoY_pct] > 0.035, "🟡 Muy fuerte",
    "🟢 Normal"
)
```

#### Desempleo
- **Rojo (🔴):** > 6.0% (crisis) o < 4.5% (sobrecalentamiento)
- **Naranja (🟡):** 5.5-6.0% o 4.5-5.0%
- **Verde (🟢):** 5.0-5.5%

**Fórmula DAX:**
```dax
Flag_Desempleo = 
SWITCH(TRUE(),
    [Tasa_Desempleo] > 0.06, "🔴 Crisis",
    [Tasa_Desempleo] > 0.055, "🟡 Elevado",
    [Tasa_Desempleo] < 0.045, "🟡 Bajo",
    "🟢 Normal"
)
```

#### Balanza Comercial
- **Rojo (🔴):** Saldo < -200 MM USD (déficit severo)
- **Naranja (🟡):** -200 a 0 MM USD (déficit moderado)
- **Verde (🟢):** > 0 MM USD (superávit)

**Fórmula DAX:**
```dax
Flag_Balanza = 
SWITCH(TRUE(),
    [Balanza_Comercial_USD] < -200, "🔴 Déficit alto",
    [Balanza_Comercial_USD] < 0, "🟡 Déficit",
    "🟢 Superávit"
)
```

---

### PÁGINA 2: Inflación y Política Monetaria

#### Estado General de Inflación
- **Crítico (🔴):** IPC YoY > 4.0% y alimentos > 4.5%
- **Preocupante (🟡):** IPC 3.0-4.0% o brecha vs meta > 0.5 pp
- **Controlado (🟢):** IPC ≤ 3.0% y dentro de banda meta

**Fórmula DAX:**
```dax
Estado_Inflacion = 
VAR IPC = [Inflacion_YoY]
VAR Alimentos = [Inflacion_NoSubyacente_Alimentos]
VAR Brecha = [Inflacion_Gap_vs_Meta]
RETURN
    SWITCH(TRUE(),
        IPC > 0.04, "🔴 Crítico",
        Brecha > 0.005, "🟡 Preocupante",
        "🟢 Controlado"
    )
```

---

### PÁGINA 3: Actividad y Empleo

#### Ciclo Económico (Actividad)
- **Contracción (🔴):** PBI YoY < 0%
- **Debilidad (🟡):** PBI YoY 0-1.5%
- **Expansión Normal (🟢):** PBI YoY 1.5-3.0%
- **Sobrecalentamiento (🔴):** PBI YoY > 4.0%

**Fórmula DAX:**
```dax
Ciclo_Economico = 
VAR PBI = [PBI_YoY_pct]
RETURN
    SWITCH(TRUE(),
        PBI < 0, "🔴 Contracción",
        PBI < 0.015, "🟡 Debilidad",
        PBI > 0.040, "🔴 Sobrecal.",
        "🟢 Expansión"
    )
```

#### Salud del Empleo
- **Malo (🔴):** Desempleo > 6% o Puestos Formales YoY < -1%
- **Tenso (🟡):** Desempleo 5.5-6% o Puestos -1% a 0%
- **Bueno (🟢):** Desempleo < 5.5% y Puestos YoY > 1%

**Fórmula DAX:**
```dax
Salud_Empleo = 
VAR Desemp = [Tasa_Desempleo]
VAR Formales_YoY = [Puestos_Formales_YoY_pct]
RETURN
    SWITCH(TRUE(),
        Desemp > 0.06, "🔴 Malo",
        Formales_YoY < -0.01, "🔴 Pérdidas",
        Desemp > 0.055, "🟡 Tenso",
        Formales_YoY < 0, "🟡 Débil",
        "🟢 Bueno"
    )
```

---

### PÁGINA 4: Sector Externo

#### Riesgo Externo (Compuesto)
- **Alto (🔴):** Saldo < -300 MM USD o TC > 3.70 y TdI cae >3%
- **Moderado (🟡):** Saldo -200 a 0 MM USD o TC 3.60-3.70
- **Bajo (🟢):** Saldo > 0 MM USD y TC < 3.60

**Fórmula DAX:**
```dax
Riesgo_Externo = 
VAR Saldo = [Balanza_Comercial_USD]
VAR TC = [TC_Promedio_Mensual]
VAR TdI = [Terminos_Intercambio_Variacion]
RETURN
    SWITCH(TRUE(),
        Saldo < -300, "🔴 Alto",
        TC > 3.70, "🔴 Presión",
        Saldo < 0, "🟡 Moderado",
        TC > 3.60, "🟡 Alerta",
        "🟢 Bajo"
    )
```

---

## CONFIGURACION EN POWER BI (Visual Formatting)

### Aplicar Colores por Condición

Para una tarjeta KPI con semáforo:

1. **Seleccionar visual (tarjeta)**
2. **Formato → Valores de datos**
3. **Color de fondo: Formato condicional**
4. **Regla:**
   - Si `[Flag_Inflacion]` contiene "🔴" → Rojo (#FF6B6B)
   - Si `[Flag_Inflacion]` contiene "🟡" → Naranja (#FFA500)
   - Si `[Flag_Inflacion]` contiene "🟢" → Verde (#52C41A)

### Bandas de Color en Gráficos

Para un gráfico de líneas (ej. Inflación):

1. **Seleccionar gráfico**
2. **Formato → Líneas de referencia**
3. **Añadir línea:**
   - Posición: 2.5% (naranja)
   - Color: Naranja
   - Estilo: Puntada

4. **Añadir línea:**
   - Posición: 3.5% (alerta)
   - Color: Rojo
   - Estilo: Línea sólida

---

## NOTAS IMPORTANTES

1. **Umbrales dinámicos:** Si los umbrales cambian (ej. meta de inflación), actualiza las constantes en las fórmulas DAX.

2. **Banda sombreada:** Para resaltar rango normal, usa:
   ```dax
   Area_Reference = 
   IF(
       AND([Valor_Ultimo] >= 4.5, [Valor_Ultimo] <= 5.5),
       [Valor_Ultimo],
       BLANK()
   )
   ```

3. **Histórico de alertas:** Guarda snapshots (bookmarks) de cuando cambió el semáforo para análisis post-evento.

4. **Umbrales por contexto:** Ajusta según normativa del BCRP/INEI y tu propia metodología interna.

---

## CHECKLIST

- [ ] Todas las fórmulas DAX sin errores.
- [ ] Colores consistentes con paleta de empresa.
- [ ] Leyendas claro explicado (ej. "🟢 = Dentro de rango normal").
- [ ] Tooltips muestran la fórmula de cálculo del semáforo.
- [ ] Documentación de umbrales junto a dashboard.
- [ ] Alertas configuradas en Power Automate para cambios críticos.
