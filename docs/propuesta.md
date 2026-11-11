# Propuesta de Trabajo Integrador Final — Anticipar la carga en horas pico

*Versión: 2026-11-10. Reemplaza a los documentos de `docs/preliminar/`, que exploraban cuatro ideas alternativas.*

---

## 1. Contexto

EVCS es una empresa que provee un servicio de carga de vehículos eléctricos a través de una red de cargadores (*estaciones* o *EVSE*) instalados en distintas ubicaciones, concentradas en la costa oeste de EE. UU. (California, Oregon y Washington). Un usuario puede iniciar una carga pasando una tarjeta por el lector del cargador o desde la aplicación móvil de EVCS.

Buena parte de los cargadores no son operados directamente por EVCS, sino por operadores externos (CPO) con los que EVCS se integra mediante el protocolo estándar de la industria OCPI. Por eso parte de la información de cada carga la reporta el sistema de un tercero.

## 2. Problema

### 2.1 Qué es una hora pico

La red eléctrica de California no tiene el mismo costo ni la misma huella de carbono a toda hora. Para este trabajo, las horas pico no se toman de una ventana comercial fija, sino de un índice construido con datos públicos de la red para cada una de las 168 horas de la semana (documentado en `docs/indice_pico_red.md`). El índice combina tres criterios con pesos obtenidos por análisis de componentes principales:

- **Demanda neta de CAISO** (demanda menos generación solar y eólica), peso 0,351.
- **Precio mayorista day-ahead**, peso 0,356.
- **Intensidad de CO2 de la generación**, peso 0,293.

Las horas pico (cuartil superior del índice) son las noches de los días hábiles, desde las 18 h hasta la medianoche, y algunas horas de la madrugada siguiente. Las horas valle son las del mediodía solar. Los fines de semana no tienen horas pico.

En promedio, una hora pico tiene un **precio mayorista 2,3 veces más alto** y una **intensidad de CO2 1,7 veces mayor** que una hora valle. Cada carga que se mueve fuera del pico reduce el costo de la energía y las emisiones asociadas, y alivia la red en el momento de mayor exigencia. Hoy, el 21% del tiempo de carga en EVCS ocurre en horas pico.

### 2.2 Prevenir en lugar de corregir

Cambiar un hábito ya formado es difícil. En cambio, la literatura sobre formación de hábitos muestra que hay una ventana de oportunidad cuando el contexto cambia:

- La hipótesis de discontinuidad del hábito sostiene que una intervención es más efectiva cuando se aplica durante un cambio de contexto. En un experimento de campo con 800 participantes, una intervención por comportamientos sustentables fue más efectiva en hogares que se acababan de mudar, con una ventana de unos tres meses (Verplanken y Roy, 2016).
- El automatismo de un hábito crece con las repeticiones hasta estabilizarse; en Lally et al. (2010) la mediana fue de 66 días, con gran variación entre personas.
- Una vez formado el hábito de carga, la señal de precio tiene poco efecto: en datos de telemetría de 2023, el 72% de las cargas domiciliarias empezó apenas se enchufó el vehículo, sin importar la tarifa horaria (Gupta et al., 2025).

Un usuario que empieza a usar EVCS está en ese cambio de contexto: cargadores, ubicaciones, precios y aplicación nuevos. Esto vale aunque el usuario ya tenga experiencia con vehículos eléctricos. El argumento no depende de que sea novato, sino de que el contexto es nuevo (sección 4.5).

Además, la mayoría de los usuarios nuevos **todavía no cargó nunca en hora pico**: entre los usuarios con una o dos cargas previas, el 77% no tiene ninguna en pico. Para ellos, la regla simple "cada usuario repite lo que hizo antes" no permite distinguir quién va a empezar a cargar en pico. Ahí es donde un modelo puede aportar.

### 2.3 Pregunta y meta

- **Fenómeno (objeto de estudio):** la formación del hábito horario de carga en las primeras cargas de un usuario en EVCS.
- **Pregunta concreta:** a partir de sus primeras cargas, ¿qué usuarios nuevos de EVCS van a cargar en horas pico de la red?
- **Meta:** construir un clasificador que estime esa probabilidad y que:
  1. supere al azar y a la regla simple de hábito, y
  2. permita anticipar quiénes van a empezar a cargar en pico entre los usuarios que todavía no lo hicieron (prevención).
- **Impacto:** dirigir incentivos (beneficios por cargar en horas valle, recordatorios en la aplicación, notificaciones programadas) a los usuarios con mayor riesgo de adoptar un hábito de carga en pico, antes de que lo consoliden. Cada carga que se evita en pico se traduce en menor costo de energía, menores emisiones y menor exigencia para la red.

### 2.4 Por qué esta idea

De las cuatro ideas exploradas en la etapa preliminar, esta es la que reúne:

- **Una variable objetivo exacta:** si una carga empezó o no en hora pico se deriva de un *timestamp* y de una definición de pico documentada, sin ruido de instrumentación (a diferencia de los estados reportados por los cargadores, Idea 2).
- **Un volumen suficiente:** miles de usuarios nuevos y decenas de miles de cargas, con métricas de validación estables (a diferencia de las ~364 ubicaciones de la Idea 4).
- **Una pregunta que solo los datos pueden responder:** la causa de un intento de carga fallido (Idea 3) se diagnostica mejor con el operador y una prueba en sitio; la propensión horaria de un usuario, no.

## 3. Datos

### 3.1 Fuente

Base de datos de producción de EVCS (PostgreSQL), consultada sobre una réplica de solo lectura. Las tablas involucradas son:

| Tabla | Rol en el trabajo |
|---|---|
| `charges` | Tabla central: una fila por carga finalizada (usuario, energía, duración, medio de pago, cargador, ubicación). |
| `sessions` | Hora exacta de inicio de la carga (`start_date_time`) y datos reportados por el cargador vía OCPI. Relación 1 a 1 con `charges` cuando existe. |
| `users` | Fecha y canal de alta del usuario, para identificar a los usuarios nuevos. |
| `user_cars` / `cars` | Marca y año del vehículo, como aproximación a la experiencia previa del usuario (sección 4.5). |
| `stations` / `connectors` | Características del cargador: potencia, tipo de conector. |
| `locations` | Ubicación física que agrupa cargadores. |
| `subscriptions` / `plans` | Si el usuario tenía un plan activo al momento de la carga. |

La definición de hora pico proviene de fuentes externas (EIA-930 y CAISO OASIS) y se documenta en `docs/indice_pico_red.md`. El detalle de columnas se documenta en la Entrega 2.

### 3.2 Población y unidad de observación

- **Usuarios nuevos:** usuarios dados de alta (`users.created_at`) dentro de la ventana de estudio, de modo que se conoce su historial completo en EVCS.
- **Cargas de días hábiles:** como los fines de semana no tienen horas pico, se modelan solo las cargas de lunes a viernes. Incluir los fines de semana inflaría el AUC con una regla trivial ("fin de semana, entonces no es pico").
- **Unidad de observación:** cada carga de un usuario nuevo con entre 1 y 9 cargas previas. Todas las variables explicativas se calculan con esas cargas **previas**. El estrato principal es el de 1 a 2 cargas previas.
- **Subpoblación de prevención:** cargas de usuarios nuevos que todavía no tienen ninguna carga previa en pico.

### 3.3 Recorte

- **Ventana temporal:** los últimos 12 meses. Permite entrenar con 9 meses y validar con los 3 más recientes, y es la misma ventana con la que se construyó el índice de pico.
- **Solo usuarios identificados:** se excluyen las cargas sin `user_id`, que corresponden a *roaming* sin usuario EVCS identificable (~49% de las cargas del período). Es una exclusión estructural: el trabajo describe a los usuarios de la aplicación, no a toda la red.
- **Solo cargas reales:** se excluyen las cargas con 0 kWh y las borradas lógicamente (`deleted_at`).

### 3.4 Variable objetivo

`pico = 1` si la carga **empezó** en una hora pico según el índice de la red; `0` en caso contrario.

- Los *timestamps* se almacenan en UTC y se convierten a `America/Los_Angeles` (respetando PST/PDT) antes de asignar hora y día de la semana.
- La hora de inicio se toma de `sessions.start_date_time` y, cuando la carga no tiene sesión asociada, se estima como `completed_at − duration`.

## 4. Estudio de viabilidad

Estudio preliminar sobre la réplica (extracción del 2026-11-10, últimos 12 meses).

### 4.1 Volumen

| Métrica | Valor |
|---|---|
| Cargas de usuarios identificados con kWh > 0 | 297.494 |
| Usuarios nuevos (dados de alta en la ventana) con al menos una carga | 15.309 (~1.250 por mes) |
| Proporción de cargas en pico (todas las cargas) | 21,5% |
| Proporción de cargas en pico (días hábiles, usuarios nuevos) | 32% |

### 4.2 Modelos y referencias

Split temporal: entrenamiento con cargas anteriores al 2026-08-11 y prueba con las posteriores. Variables, todas calculadas sobre las cargas **previas** del usuario: proporción de cargas en pico, si la última fue en pico, hora media de carga (codificada de forma circular), proporción de cargas en DC, cantidad de cargas, tasa de pico de las ubicaciones que frecuenta, medio de pago y si tiene un plan activo.

Se comparan tres clasificadores de la materia contra dos referencias:

- **Azar:** AUC 0,5.
- **Regla de hábito (baseline):** la proporción de cargas previas en pico del usuario, usada directamente como puntaje.

### 4.3 Resultados generales

AUC-ROC en el conjunto de prueba (usuarios nuevos, cargas de días hábiles):

| Cargas previas | n prueba | Baseline | Regresión logística | Naive Bayes | KNN |
|---|---|---|---|---|---|
| **1 a 2** | 2.070 | 0,672 | 0,736 | 0,733 | **0,745** |
| **3 a 9** | 3.437 | 0,749 | 0,791 | 0,785 | **0,794** |

Con 1 a 2 cargas previas, la mejora de la regresión logística sobre la regla de hábito tiene un intervalo de confianza del 95% de [0,050; 0,083] (*bootstrap* agrupado por usuario), por lo que no es atribuible al azar del muestreo.

### 4.4 Resultado principal: prevención

Entre los usuarios nuevos que todavía no tienen ninguna carga previa en pico (77% de los usuarios con 1 a 2 cargas previas), la regla de hábito asigna el mismo puntaje a todos y su AUC es 0,5. Los modelos sí logran ordenarlos:

| Subpoblación sin pico previo | n prueba | Positivos | Baseline | Logística | Naive Bayes | KNN |
|---|---|---|---|---|---|---|
| 1 a 2 cargas previas | 1.471 (1.113 usuarios) | 22,1% | 0,500 | 0,655 | 0,642 | **0,660** |
| 1 a 9 cargas previas | 2.852 (1.377 usuarios) | 17,8% | 0,500 | 0,664 | 0,654 | **0,695** |

En la práctica: si se dirige una acción preventiva al 10% de esos usuarios con mayor probabilidad estimada, el **47,7%** de ellos efectivamente carga en pico en su siguiente carga, contra el **23,2%** si se los eligiera al azar. Es decir, **2,1 veces más** usuarios en riesgo alcanzados con el mismo esfuerzo (1,6 veces al 20%, 1,5 veces al 30%).

### 4.5 Robustez: ¿nuevo en EVCS o nuevo en la carga?

Que un usuario sea nuevo en EVCS no implica que sea nuevo con los vehículos eléctricos. Como aproximación a la experiencia previa se usó la antigüedad del vehículo al momento del alta (año del alta menos año del modelo):

| Grupo (usuarios nuevos, 1 a 2 cargas previas, días hábiles) | n prueba | Baseline | Logística | Mejora |
|---|---|---|---|---|
| Vehículo del año o de 1 año | 533 | 0,706 | 0,750 | +0,043 |
| Vehículo de 3 años o más (probable experiencia previa) | 1.166 | 0,662 | 0,728 | +0,066 |

El modelo aporta también en el grupo con probable experiencia previa. Es consistente con la hipótesis de discontinuidad del hábito, según la cual lo determinante es el cambio de contexto (una red nueva de cargadores) y no la falta de experiencia. La antigüedad del vehículo es un *proxy* imperfecto (puede tratarse de un vehículo usado o recién comprado) y las muestras son chicas, por lo que se presenta como análisis de robustez y no como prueba.

### 4.6 Lo que no aportó y un error corregido

- **Variables que no mejoraron el AUC** (cambios menores a 0,005): un historial más detallado (índice de pico medio de las cargas previas, concentración horaria, hora de la última carga, duración y energía), perfiles horarios por bloques, y atributos del usuario (canal de alta, antigüedad y marca del vehículo).
- **Techo de referencia:** un modelo de *gradient boosting* (no incluido en la materia) alcanza ~0,79 con 1 a 2 cargas previas, lo que indica relaciones no lineales que los modelos lineales no capturan. Queda como referencia, no como parte del trabajo.
- **Un caso de *leakage* detectado y corregido:** una primera versión incluía "días desde la carga anterior", calculada con la hora de la carga a predecir; combinada con la hora de la carga anterior, permitía reconstruir la hora actual e inflaba el AUC. La variable se eliminó y la regla se incorporó al diseño (sección 5, punto 4).

## 5. Preparación de los datos

1. **Construcción del dataset maestro** a nivel carga, con las uniones de la sección 3.1 y los recortes de la sección 3.3.
2. **Conversión horaria** a `America/Los_Angeles` de todos los *timestamps*, antes de derivar hora y día de la semana.
3. **Asignación de la etiqueta** a partir de la matriz de franjas del índice de pico (`docs/indice_pico_red.md`).
4. **Variables de historial sin *leakage*:** cada variable se calcula únicamente con cargas anteriores del mismo usuario, y nunca con atributos de la carga que se predice (en particular, su hora de inicio). Las variables de ubicación se estiman solo con datos del período de entrenamiento.
5. **Normalización de texto libre** (`stations.make`, `locations.state`, `cars.make`) a categorías canónicas.
6. **Tratamiento de atípicos** en `kwh` y `duration` (sesiones que nunca se cerraron correctamente del lado del cargador) con un umbral explícito y documentado.

## 6. Plan de técnicas

### 6.1 Definición de la variable objetivo: ACP

El análisis de componentes principales se usa para combinar demanda neta, precio e intensidad de CO2 en un único índice de pico por hora de la semana, con pesos determinados por el primer componente (82,9% de la varianza explicada). Ya está realizado y documentado en `docs/indice_pico_red.md`.

### 6.2 Núcleo: clasificación de usuarios nuevos

| Técnica | Resultado esperado |
|---|---|
| Regresión logística | Modelo de referencia, interpretable: qué señales de las primeras cargas anticipan que un usuario va a cargar en pico. |
| KNN, Naive Bayes y SVM | Comparación de clasificadores sobre la misma población y el mismo split temporal. En la viabilidad, KNN obtuvo el mejor resultado en la subpoblación de prevención. |

La salida es una probabilidad por usuario, usable como puntaje para priorizar acciones preventivas.

### 6.3 Complemento: segmentación de usuarios con hábito consolidado

| Técnica | Resultado esperado |
|---|---|
| ACP sobre el perfil horario de 24 posiciones | Resumir el hábito de cada usuario consolidado (10 cargas o más) en 2 o 3 ejes interpretables. Como cada perfil es una composición que suma 1, se aplica una transformación log-ratio centrada (CLR) antes del ACP. |
| K-means sobre los componentes | Segmentos descriptivos (por ejemplo, "nocturnos de día hábil", "de mediodía", "de fin de semana") que muestren en qué hábitos desembocan los usuarios y cuántos terminan concentrados en el pico. |

### 6.4 Opcionales (si el núcleo está cerrado)

- **Estimación de punto ideal (IRT bayesiano):** un puntaje latente de "afinidad con el pico" por usuario, a partir de preguntas binarias evaluadas en cada carga.
- **Grafo de proximidad:** dado un usuario que dejó de cargar en pico, encontrar los usuarios más parecidos para dirigirles la misma acción.

## 7. Diseño de la evaluación

- **Split temporal, no aleatorio:** entrenamiento con los primeros 9 meses de la ventana y prueba con los últimos 3. Para elegir hiperparámetros se usa validación temporal dentro del período de entrenamiento.
- **Dos referencias obligatorias:** el azar (AUC 0,5) y la regla de hábito. El criterio de éxito es superar a la regla de hábito en usuarios nuevos; superar al azar es condición necesaria pero no suficiente.
- **Resultado principal, la prevención:** AUC en la subpoblación sin pico previo, donde la regla de hábito no discrimina, y proporción de aciertos al dirigir una acción al 10%, 20% y 30% de mayor riesgo frente a una selección al azar.
- **Resultados por estrato:** AUC por cantidad de cargas previas (1 a 2, 3 a 9), con intervalos de confianza por *bootstrap* agrupado por usuario.
- **Métricas complementarias:** PR-AUC por el desbalance de clases, y precisión/recall en el umbral de decisión elegido.
- **Robustez:** resultados por grupo de experiencia previa aproximada (antigüedad del vehículo).
- **Segmentación:** silueta, inercia en función de k y estabilidad de los segmentos entre períodos.

## 8. Limitaciones

- **Población parcial:** el trabajo describe solo a usuarios identificados de la aplicación; el ~49% de cargas de *roaming* sin usuario queda afuera por construcción.
- **Solo días hábiles:** el modelo no cubre los fines de semana, que no tienen horas pico según el índice.
- **Propensión no es efecto causal:** el modelo anticipa quién va a cargar en pico, no cuánto cambiaría su comportamiento ante un incentivo. Medir ese efecto requiere un experimento controlado (A/B), fuera del alcance.
- **La literatura de hábitos se aplica por analogía:** los estudios citados tratan sobre otros comportamientos (sustentabilidad en el hogar, hábitos de salud) o sobre carga domiciliaria; no se encontró evidencia específica sobre la formación del hábito de carga en una red pública nueva.
- **Experiencia previa aproximada:** la antigüedad del vehículo es un *proxy* imperfecto de la experiencia con vehículos eléctricos.
- **Definición de pico con supuestos propios:** el índice usa intensidad de CO2 promedio (no marginal), no incluye importaciones de energía, promedia las cuatro estaciones y usa precios mayoristas en lugar de tarifas finales. Sus limitaciones se detallan en `docs/indice_pico_red.md`.
- **Hora de inicio estimada** para las cargas sin sesión OCPI asociada (`completed_at − duration`).

## 9. Trabajo futuro

- **Experimento de incentivos:** usar el puntaje del modelo para un A/B que mida el efecto real de una acción preventiva sobre la carga en pico.
- **Índice de pico por estación del año y con emisiones marginales**, para afinar la definición de la variable objetivo.
- **Dónde instalar el próximo cargador:** estimar la utilización esperada de un sitio candidato a partir de arquetipos de ubicaciones existentes, incorporando datos externos (densidad de población, puntos de interés, tráfico).

## Referencias

- Gupta, Y., Vreeland, W., Peterman, A., Girouard, C. y Wang, B. (2025). *The Untapped Potential of Smart Charging: How EV Owners Can Save Money and Reduce Emissions Without Behavioral Change*. arXiv:2503.03167.
- Lally, P., van Jaarsveld, C. H. M., Potts, H. W. W. y Wardle, J. (2010). How are habits formed: Modelling habit formation in the real world. *European Journal of Social Psychology*, 40(6), 998-1009. https://doi.org/10.1002/ejsp.674
- Verplanken, B. y Roy, D. (2016). Empowering interventions to promote sustainable lifestyles: Testing the habit discontinuity hypothesis in a field experiment. *Journal of Environmental Psychology*, 45, 127-134. https://doi.org/10.1016/j.jenvp.2015.11.008
- Ver también las referencias de `docs/indice_pico_red.md` (EIA-930, CAISO OASIS, coeficientes de emisión de EIA, WattTime).
