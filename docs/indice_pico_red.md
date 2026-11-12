# Índice de pico de la red eléctrica de California por hora y día de la semana

*Versión: 2026-11-10. Período analizado: 1 de noviembre de 2025 a 31 de octubre de 2026. Todas las horas están en hora local de Los Ángeles (`America/Los_Angeles`, PST/PDT).*

---

## Resumen

Este documento define, para cada una de las 168 horas de la semana, qué tan "pico" es esa hora para la red eléctrica de California, combinando tres criterios: cuánto se exige a la red (demanda neta), cuánto cuesta la energía (precio mayorista) y cuánto contamina generarla (intensidad de CO2). Los tres criterios se combinan en un índice

> **Índice = a·X + b·Y + c·Z**

donde X, Y y Z son las tres matrices normalizadas a [0, 1] y los pesos surgen del primer componente principal de un análisis de componentes principales (ACP):

| Criterio | Matriz | Peso |
|---|---|---|
| Demanda neta de CAISO | X | **a = 0,351** |
| Precio mayorista day-ahead | Y | **b = 0,356** |
| Intensidad de CO2 de la generación | Z | **c = 0,293** |

El primer componente explica el **82,9%** de la variabilidad conjunta de las tres matrices. Las horas pico (cuartil superior del índice) son las de la noche de los días hábiles, desde las 18 h hasta la medianoche, y algunas horas de la madrugada siguiente. Las horas valle (cuartil inferior) son las del mediodía solar: entre las 10 y las 15 h en días hábiles, y desde las 8 h hasta las 16 o 17 h los fines de semana (sección 5.4).

## 1. Motivación

La forma habitual de definir el "horario pico" es una ventana comercial fija. Las tarifas por bloque horario de las distribuidoras de California, por ejemplo, ubican el pico entre las 16 y las 21 h; los planes "Off-Peak" de muchos operadores de carga usan la franja de 22 a 6 h. Estas ventanas tienen dos problemas:

1. **Son fijas y gruesas:** asignan el mismo valor a horas muy distintas y no distinguen días hábiles de fines de semana.
2. **No necesariamente coinciden con las emisiones:** un bloque barato no es necesariamente un bloque limpio. WattTime muestra que los bloques horarios de las tarifas no siempre se alinean con las emisiones de la red y que en CAISO las horas más limpias son las del día, con alta generación solar (Lewis et al., 2019).

Este trabajo reemplaza la ventana fija por un índice construido a partir de datos públicos de la red, con pesos determinados por los propios datos en lugar de por criterio del autor.

## 2. Datos

### 2.1 Fuentes

| Matriz | Qué mide | Fuente | Unidad |
|---|---|---|---|
| **X** | Demanda neta: demanda total menos generación solar y eólica | EIA-930, *Hourly and Daily Balancing Authority Operations Report*, área de balance CAISO (`CISO`), archivos semestrales de la *Hourly Electric Grid Monitor* | MW |
| **Y** | Precio marginal local (LMP) del mercado del día anterior, promedio de los hubs NP15 (norte) y SP15 (sur) | CAISO OASIS, consulta `PRC_LMP`, mercado `DAM`, nodos `TH_NP15_GEN-APND` y `TH_SP15_GEN-APND` | USD/MWh |
| **Z** | Intensidad de CO2 de la generación dentro de CAISO | EIA-930 (generación por combustible) × factores de emisión de EIA (sección 2.3) | gCO2/kWh |

### 2.2 Por qué demanda neta y no demanda total

La demanda neta es la demanda que tienen que cubrir las fuentes despachables (gas, hidroeléctrica, importaciones, baterías) una vez descontada la solar y la eólica. Es la variable que mejor describe la exigencia real sobre la red en California: su forma diaria es la conocida "curva del pato", con un valle al mediodía solar y una rampa pronunciada al atardecer.

### 2.3 Cálculo de la intensidad de CO2

EIA-930 informa la generación horaria por combustible, pero no publica las emisiones en los archivos semestrales. La intensidad se calculó como

> Z = Σ (generación del combustible × factor de emisión del combustible) / generación neta total

con factores de emisión por kWh generado obtenidos como el coeficiente de CO2 del combustible por el *heat rate* promedio de operación de 2025:

| Combustible | Coeficiente de CO2 (lb/MMBtu) | Heat rate 2025 (Btu/kWh) | Factor (gCO2/kWh) |
|---|---|---|---|
| Gas natural | 116,65 | 7.781 | 412 |
| Carbón | 211,63 | 10.647 | 1.022 |
| Petróleo (destilados) | 163,45 | 10.969 | 813 |

Al resto de las fuentes (nuclear, hidroeléctrica, solar, eólica, geotérmica, baterías y otras) se les asignó un factor de 0.

Fuentes: coeficientes de CO2 de EIA (2024), basados en datos de 2022; *heat rates* de EIA, *Electric Power Annual*, tabla 8.1.

### 2.4 Procesamiento

- **Período:** 12 meses, de noviembre de 2025 a octubre de 2026, de modo que cada estación del año está representada exactamente una vez.
- **Zona horaria:** las tres fuentes informan los tiempos en UTC (EIA: *UTC Time at End of Hour*; OASIS: `INTERVALSTARTTIME_GMT`). Se convirtieron a `America/Los_Angeles` antes de asignar la hora y el día de la semana, para respetar los cambios de horario PST/PDT.
- **Convención horaria:** la columna *h* de cada matriz corresponde al intervalo de *h*:00 a *h*:59. Por ejemplo, la columna 14 es de 14:00 a 14:59.
- **Agregación:** cada celda de una matriz es el promedio de las observaciones horarias de ese día de la semana y esa hora a lo largo de los 12 meses (~52 observaciones por celda). EIA-930 aportó 8.760 horas y OASIS 8.757.

## 3. Las tres matrices

### 3.1 X — Demanda neta de CAISO (GW)

| | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Lun** | 21,1 | 20,2 | 19,8 | 19,6 | 19,7 | 20,5 | 21,1 | 18,7 | 15,1 | 13,5 | 12,8 | 12,5 | 12,2 | 12,3 | 12,5 | 13,5 | 16,2 | 20,1 | 24,5 | 27,2 | 27,1 | 26,3 | 24,6 | 22,9 |
| **Mar** | 21,9 | 20,9 | 20,3 | 20,1 | 20,1 | 20,9 | 21,5 | 19,1 | 15,5 | 14,1 | 13,4 | 13,0 | 12,7 | 12,6 | 12,9 | 13,9 | 16,6 | 20,5 | 24,8 | 27,4 | 27,4 | 26,5 | 24,9 | 23,1 |
| **Mié** | 22,2 | 21,2 | 20,6 | 20,3 | 20,3 | 21,1 | 21,6 | 18,9 | 15,5 | 14,0 | 13,3 | 12,9 | 12,6 | 12,6 | 12,9 | 14,0 | 16,4 | 20,3 | 24,6 | 27,3 | 27,2 | 26,4 | 24,8 | 23,0 |
| **Jue** | 22,1 | 21,1 | 20,5 | 20,2 | 20,2 | 21,0 | 21,5 | 18,8 | 15,4 | 14,0 | 13,2 | 12,9 | 12,7 | 12,6 | 12,8 | 14,0 | 16,6 | 20,4 | 24,4 | 27,1 | 27,1 | 26,4 | 24,8 | 23,1 |
| **Vie** | 22,2 | 21,2 | 20,5 | 20,3 | 20,3 | 21,0 | 21,5 | 18,6 | 15,0 | 13,4 | 12,5 | 12,2 | 12,1 | 12,1 | 12,5 | 13,2 | 15,8 | 19,7 | 24,1 | 26,8 | 26,6 | 26,0 | 24,7 | 23,1 |
| **Sáb** | 22,3 | 21,2 | 20,2 | 19,7 | 19,6 | 19,9 | 19,5 | 16,2 | 13,0 | 11,8 | 11,0 | 10,7 | 10,5 | 10,4 | 10,8 | 11,9 | 14,6 | 18,5 | 22,9 | 25,5 | 25,5 | 24,9 | 23,7 | 22,3 |
| **Dom** | 21,4 | 20,3 | 19,5 | 18,9 | 18,7 | 18,9 | 18,5 | 15,6 | 12,2 | 10,8 | 10,2 | 9,9 | 9,8 | 9,6 | 9,8 | 10,8 | 13,7 | 17,9 | 22,5 | 25,4 | 25,5 | 24,8 | 23,4 | 21,9 |

Mínimo: 9,6 GW (domingo, 13 h). Máximo: 27,4 GW (martes, 19 h). La forma es la de la curva del pato: la demanda neta cae a menos de la mitad al mediodía por la generación solar y se dispara entre las 17 y las 21 h, cuando la solar desaparece y la demanda sigue alta.

### 3.2 Y — Precio mayorista day-ahead (USD/MWh)

| | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Lun** | 40 | 38 | 37 | 36 | 37 | 39 | 43 | 36 | 26 | 23 | 21 | 21 | 20 | 20 | 22 | 26 | 31 | 39 | 49 | 51 | 47 | 45 | 43 | 41 |
| **Mar** | 39 | 37 | 36 | 36 | 36 | 39 | 42 | 34 | 25 | 23 | 21 | 20 | 20 | 20 | 21 | 25 | 31 | 38 | 48 | 50 | 46 | 44 | 42 | 40 |
| **Mié** | 39 | 37 | 36 | 36 | 36 | 39 | 42 | 34 | 26 | 23 | 22 | 21 | 21 | 21 | 22 | 25 | 30 | 38 | 48 | 50 | 46 | 44 | 41 | 39 |
| **Jue** | 39 | 37 | 36 | 35 | 35 | 38 | 41 | 32 | 24 | 22 | 20 | 20 | 20 | 20 | 21 | 24 | 29 | 37 | 45 | 47 | 44 | 43 | 41 | 39 |
| **Vie** | 39 | 38 | 36 | 36 | 36 | 38 | 41 | 33 | 24 | 21 | 20 | 19 | 19 | 19 | 20 | 24 | 29 | 36 | 45 | 46 | 44 | 43 | 41 | 39 |
| **Sáb** | 38 | 37 | 36 | 35 | 35 | 35 | 36 | 27 | 18 | 15 | 14 | 14 | 13 | 13 | 15 | 18 | 25 | 32 | 41 | 42 | 41 | 40 | 39 | 38 |
| **Dom** | 37 | 37 | 36 | 35 | 34 | 34 | 33 | 24 | 16 | 14 | 13 | 12 | 12 | 12 | 13 | 18 | 25 | 32 | 42 | 43 | 41 | 40 | 39 | 38 |

Mínimo: 11,5 USD/MWh (domingo, 12 h). Máximo: 50,7 USD/MWh (lunes, 19 h). El precio sigue casi exactamente a la demanda neta: la energía más cara se despacha cuando hay que cubrir la rampa del atardecer con generación térmica.

### 3.3 Z — Intensidad de CO2 de la generación (gCO2/kWh)

| | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Lun** | 162 | 172 | 182 | 186 | 181 | 168 | 152 | 132 | 109 | 101 | 100 | 102 | 102 | 100 | 98 | 95 | 101 | 111 | 119 | 126 | 131 | 137 | 151 | 166 |
| **Mar** | 174 | 182 | 189 | 193 | 189 | 177 | 159 | 137 | 114 | 108 | 107 | 107 | 107 | 104 | 101 | 100 | 108 | 116 | 124 | 131 | 136 | 142 | 155 | 168 |
| **Mié** | 176 | 183 | 189 | 188 | 185 | 175 | 159 | 137 | 113 | 106 | 104 | 104 | 103 | 102 | 99 | 98 | 104 | 110 | 121 | 128 | 132 | 137 | 149 | 161 |
| **Jue** | 168 | 174 | 180 | 184 | 180 | 170 | 152 | 133 | 112 | 107 | 106 | 106 | 105 | 101 | 98 | 97 | 104 | 110 | 119 | 126 | 130 | 135 | 147 | 160 |
| **Vie** | 170 | 176 | 181 | 185 | 181 | 170 | 154 | 131 | 103 | 96 | 94 | 96 | 95 | 94 | 91 | 91 | 97 | 105 | 113 | 121 | 125 | 128 | 140 | 150 |
| **Sáb** | 148 | 155 | 157 | 159 | 157 | 152 | 136 | 105 | 78 | 74 | 74 | 76 | 75 | 74 | 72 | 71 | 77 | 86 | 94 | 100 | 104 | 108 | 118 | 131 |
| **Dom** | 150 | 161 | 160 | 165 | 165 | 160 | 147 | 119 | 85 | 81 | 82 | 85 | 82 | 81 | 77 | 75 | 82 | 92 | 99 | 105 | 110 | 117 | 131 | 148 |

Mínimo: 71 gCO2/kWh (sábado, 15 h). Máximo: 193 gCO2/kWh (martes, 3 h). La generación más limpia es la del mediodía solar. La más sucia, en términos de intensidad promedio, no es la del pico del atardecer sino la de la madrugada: sin solar y sin descarga de baterías, la generación dentro del estado depende casi por completo del gas natural. Al atardecer, la descarga de las baterías cargadas con energía solar reduce la intensidad promedio (ver limitaciones, sección 6).

## 4. Método

1. **Normalización:** cada matriz se lleva a [0, 1] con una transformación min-max sobre sus 168 celdas, para que criterios medidos en MW, USD/MWh y gCO2/kWh sean comparables.
2. **ACP:** se aplica un análisis de componentes principales sobre las tres matrices estandarizadas (168 observaciones, una por hora de la semana, y 3 variables).
3. **Pesos:** las cargas del primer componente, todas del mismo signo, se reescalan para que sumen 1. El primer componente es la combinación lineal de los tres criterios que captura la mayor parte de su variación común, es decir, la dirección "más pico" de la red según los propios datos.
4. **Índice:** para cada hora de la semana, índice = a·X + b·Y + c·Z con las matrices normalizadas. Va de 0 (la hora menos exigida, más barata y más limpia) a 1.
5. **Franjas:** pico = cuartil superior del índice (42 horas de 168, índice ≥ 0,714); valle = cuartil inferior (42 horas, índice ≤ 0,237); el resto, intermedio.

## 5. Resultados

### 5.1 Correlaciones entre criterios

| | X | Y | Z |
|---|---|---|---|
| **X** | 1 | 0,98 | 0,59 |
| **Y** | 0,98 | 1 | 0,64 |
| **Z** | 0,59 | 0,64 | 1 |

Demanda neta y precio son casi la misma información (0,98). La intensidad de CO2 está correlacionada con ambos, pero aporta una dimensión propia: su máximo está de madrugada y no al atardecer.

### 5.2 Análisis de componentes principales

| | CP1 | CP2 | CP3 |
|---|---|---|---|
| X | 0,606 | −0,398 | −0,689 |
| Y | 0,615 | −0,316 | 0,723 |
| Z | 0,505 | 0,861 | −0,054 |
| **Varianza explicada** | **82,9%** | 16,4% | 0,7% |

- **CP1 ("exigencia de la red"):** los tres criterios con el mismo signo y pesos parecidos. Resume el 83% de la variación.
- **CP2 ("emisiones de madrugada"):** opone la intensidad de CO2 a la demanda neta y el precio. Captura las horas en que la red está poco exigida pero la generación es sucia (la madrugada).
- **CP3:** la pequeña diferencia entre demanda neta y precio; es prácticamente ruido.

### 5.3 Pesos e índice

Pesos: **a = 0,351 (X), b = 0,356 (Y), c = 0,293 (Z).**

Índice por hora y día de la semana (0 = valle extremo, 1 = pico extremo):

| | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Lun** | 0,70 | 0,69 | 0,70 | 0,70 | 0,69 | 0,70 | 0,70 | 0,54 | 0,33 | 0,25 | 0,22 | 0,21 | 0,21 | 0,20 | 0,21 | 0,27 | 0,38 | 0,56 | 0,75 | 0,83 | 0,81 | 0,79 | 0,77 | 0,75 |
| **Mar** | 0,74 | 0,72 | 0,72 | 0,72 | 0,71 | 0,72 | 0,72 | 0,55 | 0,34 | 0,28 | 0,25 | 0,23 | 0,22 | 0,22 | 0,22 | 0,28 | 0,40 | 0,57 | 0,76 | 0,84 | 0,82 | 0,80 | 0,78 | 0,76 |
| **Mié** | 0,75 | 0,73 | 0,72 | 0,71 | 0,71 | 0,72 | 0,72 | 0,55 | 0,35 | 0,28 | 0,25 | 0,23 | 0,22 | 0,22 | 0,23 | 0,27 | 0,38 | 0,55 | 0,75 | 0,83 | 0,81 | 0,79 | 0,76 | 0,73 |
| **Jue** | 0,72 | 0,70 | 0,69 | 0,69 | 0,69 | 0,70 | 0,69 | 0,52 | 0,33 | 0,27 | 0,24 | 0,22 | 0,21 | 0,20 | 0,21 | 0,26 | 0,38 | 0,53 | 0,71 | 0,80 | 0,78 | 0,77 | 0,74 | 0,73 |
| **Vie** | 0,74 | 0,71 | 0,70 | 0,70 | 0,70 | 0,70 | 0,70 | 0,51 | 0,29 | 0,23 | 0,19 | 0,18 | 0,18 | 0,17 | 0,18 | 0,23 | 0,34 | 0,50 | 0,69 | 0,77 | 0,76 | 0,74 | 0,73 | 0,71 |
| **Sáb** | 0,68 | 0,66 | 0,64 | 0,62 | 0,62 | 0,61 | 0,57 | 0,35 | 0,14 | 0,08 | 0,06 | 0,05 | 0,04 | 0,04 | 0,05 | 0,11 | 0,24 | 0,40 | 0,58 | 0,66 | 0,66 | 0,65 | 0,64 | 0,63 |
| **Dom** | 0,65 | 0,66 | 0,63 | 0,62 | 0,61 | 0,60 | 0,56 | 0,35 | 0,12 | 0,07 | 0,05 | 0,05 | 0,03 | 0,03 | 0,04 | 0,09 | 0,23 | 0,40 | 0,60 | 0,68 | 0,68 | 0,67 | 0,67 | 0,66 |

### 5.4 Franjas pico y valle

**P** = pico (cuartil superior), v = valle (cuartil inferior), · = intermedio.

| | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **Lun** | · | · | · | · | · | · | · | · | · | · | v | v | v | v | v | · | · | · | **P** | **P** | **P** | **P** | **P** | **P** |
| **Mar** | **P** | **P** | **P** | **P** | · | **P** | **P** | · | · | · | · | v | v | v | v | · | · | · | **P** | **P** | **P** | **P** | **P** | **P** |
| **Mié** | **P** | **P** | **P** | · | · | **P** | **P** | · | · | · | · | v | v | v | v | · | · | · | **P** | **P** | **P** | **P** | **P** | **P** |
| **Jue** | **P** | · | · | · | · | · | · | · | · | · | v | v | v | v | v | · | · | · | **P** | **P** | **P** | **P** | **P** | **P** |
| **Vie** | **P** | **P** | · | · | · | · | · | · | · | v | v | v | v | v | v | v | · | · | · | **P** | **P** | **P** | **P** | · |
| **Sáb** | · | · | · | · | · | · | · | · | v | v | v | v | v | v | v | v | · | · | · | · | · | · | · | · |
| **Dom** | · | · | · | · | · | · | · | · | v | v | v | v | v | v | v | v | v | · | · | · | · | · | · | · |

- **Pico:** de lunes a jueves, de 18 a 24 h; el viernes, de 19 a 23 h. Se suma la madrugada que sigue a esas noches, sobre todo la de martes (0 a 4 h y 5 a 7 h) y la de miércoles (0 a 3 h y 5 a 7 h). Los fines de semana no tienen horas pico: la demanda neta y el precio son más bajos todo el día.
- **Valle:** el mediodía solar. En días hábiles va de 10 a 15 h (de 11 a 15 h martes y miércoles; de 9 a 16 h el viernes); los sábados, de 8 a 16 h, y los domingos, de 8 a 17 h.
- **Contraste con las ventanas comerciales:** de las 56 horas semanales de la franja 22-6, usada habitualmente como "Off-Peak", ninguna es valle: 21 son pico y 35 son intermedias. El valle de la red está al mediodía.

### 5.5 Contraste entre franjas

| Criterio | Promedio en pico | Promedio en valle | Pico / valle |
|---|---|---|---|
| Demanda neta (GW) | 24,2 | 12,0 | 2,0× |
| Precio (USD/MWh) | 42,5 | 18,2 | 2,3× |
| Intensidad de CO2 (gCO2/kWh) | 150 | 91 | 1,7× |

Una carga de energía que se mueve de una hora pico a una hora valle reduce, en promedio, a menos de la mitad el precio de la energía consumida y en un 40% su intensidad de CO2.

## 6. Limitaciones

- **Intensidad promedio, no marginal.** Z mide la intensidad promedio de toda la generación de esa hora. El efecto de sumar un kWh de consumo depende de la planta que se enciende para cubrirlo (intensidad marginal), que en el atardecer suele ser una planta de gas de punta. Con intensidad marginal, las horas del atardecer probablemente resultarían más sucias que la madrugada. Datos marginales como los de WattTime requieren una cuenta.
- **No incluye importaciones.** CAISO importa una parte importante de su energía, sobre todo de noche. Z considera solo la generación dentro del área de balance; la intensidad de lo consumido (incluidas las importaciones) puede diferir.
- **Promedio anual.** Cada celda promedia las cuatro estaciones. La curva del pato es más marcada en primavera y verano; un índice por estación podría mostrar franjas distintas.
- **Dos de los tres criterios son casi redundantes.** La correlación de 0,98 entre X e Y hace que la combinación "demanda/precio" pese ~70% en el índice y las emisiones ~30%. Es una consecuencia de los datos, no una elección; si se quisiera dar más peso a las emisiones, habría que fijar los pesos por criterio y no por ACP.
- **Precio mayorista, no precio final.** Y es el precio del mercado mayorista; el costo final para un consumidor comercial incluye cargos de distribución, transmisión y potencia que siguen otra estructura (por ejemplo, la tarifa B-EV-2 de PG&E, con un pico fijo de 16 a 21 h).
- **Umbrales por cuartiles.** El corte en el 25% superior e inferior es una convención. El índice continuo puede usarse directamente si un uso particular requiere otro umbral.
- **Normalización min-max.** Es sensible a valores extremos de cada matriz. Al trabajar con promedios de ~52 observaciones por celda, el efecto es acotado.

## 7. Nota sobre un criterio descartado

Se evaluó incluir como cuarto criterio la ocupación simultánea de los cargadores de EVCS (sesiones activas por hora). Ese criterio resultó negativamente correlacionado con los otros tres (−0,55 con demanda neta y precio, −0,83 con intensidad de CO2): la red de EVCS se usa más al mediodía, justamente cuando la red eléctrica está menos exigida. En el ACP quedaba con carga opuesta a la de los criterios de red, por lo que combinarlo en un único índice cancelaba información. Se lo descartó del índice y queda como dato de contexto: con las franjas de la sección 5.4, el 36% del tiempo de carga en EVCS cae en horas valle y el 21% en horas pico.

## 8. Reproducibilidad

- Scripts en `notebooks/pico/`:
  - `download_lmp.sh` y `download_lmp_halves.sh`: descarga de precios de CAISO OASIS. La API admite consultas de hasta 31 días, por lo que los meses de 31 días se descargan en dos mitades.
  - `matrices.py`: construcción de las matrices (argumentos `eia`, `lmp`).
  - `indice.py`: correlaciones, ACP, pesos, índice y franjas.
- Datos de entrada (no versionados): archivos semestrales de EIA-930 en `data/external/eia/` y zips de OASIS en `data/external/caiso/`.
- Salidas en `data/pico/`: una matriz CSV por criterio, `indice_pico.csv`, `franja_pico_valle.csv` y `matrices.json`.

## Referencias

- California ISO. *OASIS Frequently Asked Questions* y API de OASIS. https://www.caiso.com/Documents/OASIS-Frequently-Asked-Questions.pdf
- U.S. Energy Information Administration. *About the EIA-930 data*. https://www.eia.gov/electricity/930-content/about.html
- U.S. Energy Information Administration (2024). *Carbon Dioxide Emissions Coefficients*. https://www.eia.gov/environment/emissions/co2_vol_mass.php
- U.S. Energy Information Administration. *Electric Power Annual*, tabla 8.1: *Average Operating Heat Rate for Selected Energy Sources, 2015 through 2025*. https://www.eia.gov/electricity/annual/html/epa_08_01.html
- Lewis, C., Bronski, P., McCormick, G. y Amuchastegui, N. (2019). *How Emissions-Optimized EV Charging Enables Cleaner Electric Vehicles*. WattTime. https://www.watttime.org/news/report-201909-emissions-optimized-electric-vehicle-charging/
