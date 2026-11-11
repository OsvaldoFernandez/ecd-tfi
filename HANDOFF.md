# Handoff — TFI (estado al 2026-11-10)

## ▶ Empezar por acá (próxima sesión)

**Pregunta del TFI (confirmada):** predecir, a partir de sus primeras cargas, qué usuarios nuevos de EVCS van a cargar en horas pico de la red, para prevenirlo mientras el hábito todavía se forma. **El argumento central es la prevención:** el 77% de los usuarios nuevos todavía no cargó nunca en pico; para ellos la regla de hábito da AUC 0,5 y el modelo 0,66-0,70, con 2,1 veces más aciertos que el azar en el top 10%.

**Documentos vigentes:**
- `docs/propuesta.md`: reescrita el 2026-11-10 con el enfoque de prevención. Pendiente que el usuario la revise.
- `docs/indice_pico_red.md`: definición de pico/valle (X demanda neta, Y LMP, Z CO2; pesos por ACP). Es para el TFI y para una posible publicación.

**Con qué seguimos (se trabaja con el usuario):**
1. **Revisar `docs/propuesta.md`** con el usuario y ajustar redacción y alcance. Verificar las páginas de Lally et al. (2010), 40(6), 998-1009: el DOI está confirmado, pero el volumen y las páginas no se leyeron de la fuente.
2. **Entrega 2** (`docs/entrega2_dataset_diccionario.md`): reescribirla como diccionario definitivo para esta pregunta, sobre el dataset maestro joineado (`charges` + `sessions` + `users` + `user_cars`/`cars` + `stations` + `connectors` + `locations` + `subscriptions`/`plans`). Cada columna lleva su tabla de origen y una marca (se usa / se descarta por ID externo, sensible o deprecada / derivada). Hay que confirmar con el usuario si prefiere ese formato o una sección por tabla. También hay que corregir las 4 referencias a `propuesta_TFI.md` y reemplazar los gráficos de la sección 3 por los de la pregunta actual (perfil horario en hora LA, franjas pico/valle).
3. Opcional: investigar de dónde sale la ventaja del gradient boosting (~0,79 contra ~0,74) para traducirla a variables que usen los modelos de la materia.

**Nada commiteado.** El usuario commitea por su cuenta.

---

## Historial de la sesión del 2026-11-10 (contexto; lo vigente está arriba)

## Decisiones tomadas

- **Idea elegida: Idea 1, "¿Quién carga y cuándo?"** (propensión a cargar en horario valle, 22 a 6 h hora LA).
  - Idea 2 (cargadores en riesgo): descartada. La etiqueta de "falla" tiene ruido (flapping, `outoforder` en 0,6 s) y no hay tickets de mantenimiento para validarla.
  - Idea 3 (intentos fallidos): descartada. La causa está del lado del CPMS; es más barato investigarla con el operador y un tester en sitio que modelarla.
  - Idea 4 (dónde instalar): queda como trabajo futuro. Sus arquetipos de ubicación entran como variable del clasificador de la Idea 1. No se combinan las dos como preguntas porque sería over-shooting.
- **Criterio del usuario:** la opción con menos dolores de cabeza para aprobar, y un AUC claramente mejor que el azar.
- **Alcance:** clasificación + segmentación como núcleo; IRT y grafo de proximidad son opcionales.

## Archivos

- `docs/preliminar/`: propuestas viejas (`propuesta_TFI.md` y `propuesta_tfi_raw.md`, esta última ignorada por git).
- `docs/propuesta.md`: propuesta nueva centrada en la Idea 1. **Las secciones 2, 4 y 7 están desactualizadas** (ver abajo).
- `notebooks/viabilidad/`: scripts del estudio de viabilidad.
  - `viab.py`: primer análisis. **Tiene leakage** (ver abajo); sus números no son válidos.
  - `cold.py`: chequeo con usuarios de 1 a 2 cargas previas. También tiene el leakage.
  - `clean.py`: **versión correcta**, sin la variable con leakage. Reutiliza la preparación de `viab.py`. Se corre así:
    `python3 -I -c "import sys; sys.argv=['x','data/charges_12m.csv','notebooks/viabilidad/viab.py']; exec(open('notebooks/viabilidad/clean.py').read())"`
- `data/charges_12m.csv` (ignorado por git, contiene `user_id`): extracción de la réplica del 2026-11-10, últimos 12 meses, solo cargas con `user_id`, 315.309 filas. La hora de inicio es `coalesce(sessions.start_date_time, completed_at - duration)`, convertida de UTC a `America/Los_Angeles`.
- Las 4 referencias a `propuesta_TFI.md` en `docs/entrega2_dataset_diccionario.md` siguen apuntando al nombre viejo; se corrigen al reescribir la Entrega 2.

## Viabilidad: resultados

- 297.494 cargas con kWh > 0 de 23.892 usuarios; 7.563 usuarios tienen 5 cargas o más. El 14,3% de las cargas es en valle.
- Split temporal: entrenamiento antes del 2026-08-11, prueba después.
- **Leakage encontrado:** la variable `days_since_last` usaba la hora de inicio de la carga a predecir; combinada con la hora de la carga anterior, permitía reconstruir la hora actual. Por eso el gradient boosting daba un AUC falso de 0,93. Se sacó la variable.

AUC en prueba, versión sin leakage (`clean.py`):

| Cargas previas | n prueba | Baseline (hábito) | Logística | Naive Bayes | KNN |
|---|---|---|---|---|---|
| 1 a 2 | 4.094 | 0,734 | 0,813 | 0,814 | 0,813 |
| 3 a 9 | 6.703 | 0,839 | 0,873 | 0,870 | 0,871 |
| 10 a 29 | 11.327 | 0,868 | 0,878 | 0,869 | 0,874 |
| 30 o más | 45.432 | 0,898 | 0,901 | 0,887 | 0,896 |

El baseline es la proporción histórica de cargas en valle del usuario.

**Lectura:** con usuarios frecuentes, el modelo no le gana al hábito. Con usuarios con poco historial gana claramente (+0,08 de AUC con 1 a 2 cargas previas), y los tres clasificadores de la materia coinciden.

Otros hallazgos:
- La mitad de los usuarios con 5 cargas o más nunca cargó en valle; solo ~5% carga en valle más del 70% de las veces.
- AC no es más nocturno que DC: 10,8% contra 15,3% en valle.
- La tasa de valle de las ubicaciones frecuentadas no mejoró el AUC en su versión cruda.

## Traducción económica (`notebooks/viabilidad/lift.py`)

Usuarios de prueba con 1 a 2 cargas previas: 2.746, con 9,6% de tasa de valle. AUC a nivel usuario: modelo 0,802, baseline 0,713.

| Campaña al... | Aciertos modelo | Aciertos baseline | Azar |
|---|---|---|---|
| top 10% | 47,4% | 45,3% | 9,6% |
| top 20% | 30,8% | 25,7% | 9,6% |
| top 30% | 22,7% | 18,6% | 9,6% |

- En el top 5-10% el modelo empata con el baseline. La ganancia está en campañas más amplias: **+20% de aciertos con el mismo presupuesto** en el top 20%, porque el baseline no puede ordenar a la mayoría de usuarios con 0% previo en valle.
- Plan Off-Peak: USD 99,99/mes (1.073 suscripciones activas). Hay ~1.667 usuarios nuevos por mes (estimación aproximada, incluye reactivados).
- Valor estimado: ~USD 1.300 el primer año por cada punto de tasa de conversión. Es modesto en dólares; el argumento fuerte es la eficiencia relativa (+20% contra el baseline, 3,2x contra el azar). Faltan bootstrap de los intervalos y el costo real de la energía peak/off-peak (pedir a finanzas).

## Usuarios realmente nuevos (`notebooks/viabilidad/new_users.py`, `data/users_recent.csv`)

Altas con `users.created_at` dentro de la ventana: 15.309 usuarios con cargas, ~1.250 por mes.

| Cargas previas | n prueba | Baseline | Logística | NB | KNN | Diferencia logística − baseline (IC95, bootstrap por usuario) |
|---|---|---|---|---|---|---|
| 1 a 2 | 3.094 | 0,740 | 0,822 | 0,820 | 0,822 | [0,062; 0,099] |
| 3 a 9 | 4.762 | 0,845 | 0,874 | 0,869 | 0,868 | [0,021; 0,039] |

Campaña (1.995 usuarios, 11,4% de tasa de valle): en el top 20%, modelo 35,6% contra baseline 31,1% (+15%); en el top 30%, 27,9% contra 23,1% (+21%); en el top 10% empatan.

## Índice de pico de la red (2026-11-10, `notebooks/pico/`)

El usuario descartó la etiqueta 22-6. Pidió definir pico y valle por hora × día de la semana con 4 matrices (12 meses, nov 2025 a oct 2026, hora LA) y pesos obtenidos por ACP. También quiere compartirlo con colegas de EVCS como una página interactiva.

- **W:** sesiones activas simultáneas en EVCS. Sale de `data/charges_all_12m.csv` (617.676 cargas, todas, incluido roaming), filtrando kWh > 0 y duraciones entre 1 min y 12 h; quedan 454.283.
- **X:** demanda neta de CAISO = demanda − solar − eólica (EIA-930, archivos semestrales en `data/external/eia`).
- **Y:** precio LMP day-ahead de CAISO, promedio de NP15 y SP15 (OASIS, `data/external/caiso`). OASIS permite 31 días por request; los meses de 31 días se bajaron en dos mitades. Con Python falla el certificado, hay que usar `curl`.
- **Z:** gCO2/kWh de la generación dentro del estado (EIA-930 × coeficiente de EIA × heat rate de 2025: gas 412, carbón 1.022, petróleo 813). Es intensidad promedio, no marginal, y no incluye importaciones.
- Scripts: `matrices.py` (argumento `eia,lmp,evcs`) e `indice.py`. Las salidas quedan en `data/pico/` (CSV de cada matriz, índice, franjas y `matrices.json`).
- **Resultados:**
  - Correlaciones: W contra X −0,55, contra Y −0,55 y contra Z −0,83. X contra Y da 0,98 (son casi redundantes).
  - El CP1 explica el 77% y le da carga negativa a W, así que W queda con peso 0 y X, Y, Z con ~1/3 cada una.
  - Pico (top 25% del índice): de 18 a 24 h y la madrugada de días hábiles. Valle (bottom 25%): de 10 a 14 h en días hábiles y de 8 a 16 h los fines de semana.
  - **EVCS ya carga mayormente en el valle de la red:** el 36% del tiempo de carga cae en valle y el 20% en pico, con 25% de las horas en cada franja.
- **Pendiente de decisión del usuario:** qué hacer con W (opuesta a la red), y si la etiqueta del TFI pasa a ser "carga en pico de la red". Después hay que recalcular la viabilidad y armar la página para EVCS.

### Actualización: W descartada (decisión del usuario)

- El índice usa solo X, Y y Z. Pesos del ACP: X 0,351, Y 0,356, Z 0,293; el CP1 explica el 82,9%.
- La investigación completa quedó documentada en **`docs/indice_pico_red.md`**. Es para el usuario, como insumo del TFI y para una posible publicación; no se arma página para colegas por ahora.
- Etiquetas evaluadas con `notebooks/viabilidad/label_check.py` (usuarios nuevos, AUC de prueba):
  - "Pico de red": tasa 21,5%. Con 1 a 2 cargas previas, baseline 0,668 contra logística 0,723; con 3 a 9, 0,725 contra 0,754.
  - "Valle de red": tasa 34,8%. Con 1 a 2 cargas previas, baseline 0,662 contra logística 0,695.
  - Ambas tienen menos AUC que la etiqueta 22-6 (0,82), porque el hábito "nocturno" era muy persistente.
- **Pendiente:** que el usuario elija la etiqueta del TFI. Después hay que reescribir las secciones 2 a 4, 7 y 8 de `propuesta.md`; la sección 4.4 sin dinero de suscripciones, usando el contraste pico/valle de la sección 5.5 del documento del índice.

### Pregunta del TFI confirmada (2026-11-10)

> Predecir, a partir de sus primeras cargas, qué usuarios nuevos de EVCS van a cargar en las horas pico de la red eléctrica, para incentivarlos a cambiar mientras su hábito todavía se está formando.

Etiqueta confirmada: "carga en pico de red" (franjas de `docs/indice_pico_red.md`).

### Mejora de variables (`fe_pico*.py` en `notebooks/viabilidad/`)

- **Planteo recomendado: solo cargas de días hábiles** (los fines de semana no tienen pico). Agregar "es fin de semana" como variable sube el AUC a 0,85, pero es trivial.
  - Con 1 a 2 cargas previas en días hábiles (tasa de pico 32%): baseline 0,672 contra logística 0,736 y KNN 0,745. Diferencia de la logística, IC95 [0,050; 0,083].
  - Con 3 a 9 cargas previas: baseline 0,753 contra logística y KNN 0,79.
- **Lo que no aportó** (AUC ±0,005): historial ampliado (índice medio previo, concentración horaria, última hora, duración, kWh), bloques horarios y atributos del usuario (Lyft/Hertz, antigüedad del auto, Tesla).
- El gradient boosting llega a ~0,79, así que hay interacciones no lineales que los modelos de la materia no capturan. No se encontró de qué variable vienen.
- **Argumento más fuerte, la prevención:** el 77% de los usuarios nuevos todavía no cargó nunca en pico. Para ellos la regla simple da 0,5, mientras la logística da 0,655 y KNN 0,66-0,70. Una campaña al top 10% encuentra 2,1 veces más futuros cargadores en pico que al azar.
- **Nuevo en EVCS no es lo mismo que nuevo en la carga:** usando la antigüedad del auto al darse de alta como proxy de experiencia, la ganancia del modelo no es menor en usuarios con auto de 3 años o más (+0,066) que con auto del año (+0,043). Es consistente con la discontinuidad de contexto de Verplanken: lo que importa es el cambio de contexto, no la inexperiencia. La muestra es chica y no tiene IC.
- Pendiente: los puntos 3 y 4 (`propuesta.md` y Entrega 2) se trabajan con el usuario más tarde.

## Pendiente de decisión: ventana de la etiqueta (2026-11-10) — reemplazada por la sección anterior

- El usuario no quiere hablar de dinero ni de suscripciones en la sección 4.4. Prefiere justificarla con impacto ecológico y costo del kWh pico/base para EVCS.
- Hallazgo: en California, la franja 22-6 es más barata que el pico pero **no es la más limpia**. El pico de la red es 16-21 (más caro y más sucio); el mediodía 9-14 es el más barato y el más limpio.
  - Tarifa de referencia PG&E B-EV-2-S con recargos (WestLight Energy, sin fecha): pico 16-21 USD 0,267/kWh, off-peak 0,074, super off-peak 9-14 0,050.
  - WattTime 2019: los bloques TOU no siempre se alinean con las emisiones; en CAISO, cargar de día es lo más limpio.
- Reparto de las cargas de usuarios identificados: 28% en el pico 16-21, 29% en 9-14, 14% en 22-6.
- Opciones: mantener la etiqueta 22-6 (la ventana del plan) argumentando "fuera del pico", o redefinirla como "carga fuera del pico de la red (16-21)". Hay que preguntarle al usuario antes de reescribir las secciones 4.4 y 8.
- Fuentes de hábito verificadas: Verplanken & Roy 2016 (doi 10.1016/j.jenvp.2015.11.008, N=800, ventana de 3 meses); Lally et al. 2010 (doi 10.1002/ejsp.674, mediana de 66 días); Gupta et al. 2025 (arXiv 2503.03167, Rivian: 72% de las cargas arrancan al enchufar, sin importar la TOU).

## Reencuadre (aprobado 2026-11-10, ya volcado en `docs/propuesta.md`)

- **Pregunta:** ¿cuál va a ser el hábito horario de un usuario **nuevo**, a partir de sus primeras cargas?
- **Clasificación:** solo usuarios con pocas cargas previas (por ejemplo, menos de 10). Métrica central: AUC contra el azar y contra el baseline, con la tabla por estrato como resultado principal.
- **Usuarios frecuentes:** no van al clasificador; se describen con la segmentación (ACP con CLR sobre el perfil horario de 24 h, más K-means).
- **Argumento para el jurado:** el usuario sin hábito formado es el que más fácil se mueve con un incentivo, y es justo donde el modelo aporta.

## Próximos pasos

1. ~~Confirmar el reencuadre~~ y ~~reescribir `docs/propuesta.md`~~: hecho el 2026-11-10. La propuesta ya tiene los números sin leakage, la sección 4.4 con la traducción económica y la evaluación por estrato.
2. **Pendiente:** chequear en la réplica que "pocas cargas previas" corresponda a usuarios realmente nuevos. Hay que cruzar con `users.created_at` (bajar `id, created_at` de los últimos 14 meses a `data/users_recent.csv`), recalcular las tablas 4.3 y 4.4 solo con altas dentro de la ventana y ver cuánto se achica la muestra. El 2026-11-10 la réplica daba timeout de conexión (probablemente red o VPN).
3. Iterar la Entrega 2 junto con el usuario. El diccionario definitivo sería sobre el dataset maestro joineado (`charges` + `sessions` + `stations` + `connectors` + `locations` + `subscriptions`/`plans`, posiblemente `users`). Cada columna llevaría su tabla de origen y una marca: se usa, se descarta (ID externo, sensible o deprecada) o es derivada. Falta confirmar con el usuario si prefiere ese formato o una sección por tabla. `connectors` y `users` no están en el diccionario actual.

## Reglas de trabajo

- Las queries a la réplica (`psql "service=evcs_replica"`) llevan siempre WHERE/LIMIT en tablas grandes. `charges` no tiene índice por fecha: conviene una extracción y analizar en local.
- Todas las horas se trabajan en `America/Los_Angeles`, nunca en UTC.
- Toda variable de historial se calcula solo con cargas **anteriores**, y nunca con la hora de la carga que se predice.
