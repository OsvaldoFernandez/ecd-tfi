# Propuesta de Trabajo Integrador Final — EVCS


## ¿Qué es EVCS?

EVCS es una empresa que provee un servicio de carga de vehículos eléctricos a través de una red de cargadores (también llamados *estaciones* o *EVSE*) instalados en distintas ubicaciones. Un usuario puede iniciar una carga de dos formas: pasando una tarjeta de crédito o débito directamente en el lector del propio cargador, o desde la aplicación móvil de EVCS.

Buena parte de los cargadores de la red no son operados directamente por EVCS, sino por otros operadores externos con los que EVCS se integra mediante un protocolo estándar de la industria (OCPI). Esto significa que una porción importante de la información que EVCS recibe sobre una carga —cuánta energía se entregó, cuánto duró, si se completó— viene reportada por un sistema de un tercero, a través de ese protocolo estándar (OCPI) y otra información adicional de cada operador... y no siempre llega completa.

Las cuatro ideas que siguen usan datos reales de la base de producción de EVCS (de solo lectura, sobre una réplica).

Esta propuesta incluye una carpeta adjunta (`sample_data`) con los últimos 1.000 registros de estas tablas grandes, para que se puedan revisar con más detalle que el head(10) que se muestra más abajo.

---

## Idea 1 — ¿Quién carga y cuándo?

### Dominio / problema
Hoy una parte importante de los usuarios carga su vehículo en los horarios de mayor demanda ("peak"). Eso vuelve a la red más cara de operar, más propensa a saturación y fallos, y menos amigable con el ambiente. EVCS ya ofrece planes con tarifa reducida en horario "Off-Peak" (10PM a 6AM), pero no existe hoy un análisis sistemático de qué usuarios aprovechan ese horario y cuáles no, ni de qué tan bien elegida está esa ventana horaria.

### Fenómeno (objeto de estudio)
El comportamiento del usuario respecto a su preferencia horaria de carga: en qué franja del día elige cargar, y qué tan consistente es ese hábito en el tiempo.

### Pregunta concreta
¿Quién carga y cuándo? ¿Qué usuarios son más proclives a cambiar su patrón horario de carga hacia el horario valle si se los incentiva?

### Meta
Hallar un modelo que determine, para cada usuario, su propensión a cargar en horario valle, y agrupar a los usuarios en segmentos de comportamiento horario claros para dirigirles campañas distintas.

### Impacto en el negocio
Con este modelo se pueden enviar campañas de marketing personalizadas y descuentos vía app para "re-educar" a los usuarios y maximizar el uso de los cargadores en horario valle, bajando el costo operativo y la saturación de la red en horario pico. Acción concreta: un *nudge* en tiempo real dentro de la app al iniciar la carga (ahorro simulado si se espera al valle), push notifications geolocalizadas/programadas a usuarios con patrón peak recurrente, y una campaña de email dirigida (usando el puntaje de propensión como score) ofreciendo upgrade a un plan Off-Peak.

### Tablas involucradas

**`charges`** — Total histórico: **2.073.650** filas &middot; Últimos 3 meses: **158.523**

Cada fila es una carga finalizada: quién la hizo, cuánta energía se entregó (`kwh`), cuánto duró (`duration`, en segundos) y cómo se pagó.

*Columnas con datos sensibles omitidas: `notes`, `rfid` y `cpo_last_4` se muestran como `(omitido)` cuando tienen valor: son texto libre o identificadores de tarjeta/credencial — no aportan al análisis y no corresponde exponerlos.*

| `id` | `user_id` | `completed_at` | `duration` | `created_at` | `updated_at` | `location_id` | `subscription_id` | `deleted_at` | `kwh` | `price` | `charger_type` | `connector` | `co2_saved` | `gas_saved` | `payment_method` | `session_id` | `payment_gateway` | `during_trial_period` | `station_id` | `charging_duration` | `price_per_kwh` | `session_fee` | `free_kwh` | `notes` | `user_car_id` | `created_from` | `trial_kwh` | `total_discount` | `rating` | `cpo_user_id` | `cpo_price` | `cpo_session_id` | `cpo_encoded_id` | `cpo_last_4` | `cpo_location_id` | `rfid` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2226790 | 103692 | 2026-10-25 11:50:01.727 | 3199 | 2026-10-25 11:50:04.84023 | 2026-10-25 11:50:05.112592 | 478 | 53021 | — | 42.9872 | 0.00 | dc50kw | CCS1 | 46074.169 | 5.184 | Roaming - 002 | 1776198 | — | f | 2646 | 3199 | 0.0000 | 0.00 | 42.9872 | — | 79181 | — | — | 30.65 | — | — | — | s22n-1307 | at3gY8Dom3OJ_oy7 | — | /cRYuSBy3rmoySTWuXxhX | — |
| 2226789 | — | 2026-10-25 11:46:05.119 | 0 | 2026-10-25 11:46:05.798724 | 2026-10-25 11:46:05.798724 | 84 | — | — | 0.0000 | 0.00 | dc50kw | — | 0.000 | 0.000 | Roaming - 002 | — | — | f | 3039 | 0 | 0.0000 | 0.99 | 0.0000 | — | — | — | — | 0.00 | — | — | — | 099-27364 | at3r_MDom3OJ1rKA | — | /YlexdtO476u4LG7ZfT0ehPi4Di4B | — |
| 2226788 | — | 2026-10-25 11:45:25.773 | 0 | 2026-10-25 11:45:26.741205 | 2026-10-25 11:45:26.741205 | 84 | — | — | 0.0000 | 0.00 | dc50kw | — | 0.000 | 0.000 | Roaming - 002 | — | — | f | 3039 | 0 | 0.0000 | 0.99 | 0.0000 | — | — | — | — | 0.00 | — | — | — | 099-27363 | at3rjsDom3OJztzJ | — | /YlexdtO476u4LG7ZfT0ehPi4Di4B | — |
| 2226787 | 140114 | 2026-10-25 11:43:06.807 | 4409 | 2026-10-25 11:43:09.788217 | 2026-10-25 11:43:16.600853 | 356 | — | — | 36.8877 | 22.75 | dc50kw | CCS1 | 39536.656 | 4.449 | Roaming - 002 | 1776195 | — | f | 1678 | 4409 | 0.5900 | 0.99 | 0.0000 | `(omitido)` | 113647 | — | — | 0.00 | -1 | — | — | 420-6559 | at3aEcDom3OJiEe6 | — | /6m54fBrXIjsSeoZ3imsR | — |
| 2226785 | 86613 | 2026-10-25 11:41:57.652 | 4679 | 2026-10-25 11:41:59.487534 | 2026-10-25 11:41:59.827235 | 50 | 50286 | — | 11.0990 | 0.00 | dc50kw | CCS1 | 11896.034 | 1.339 | Roaming - 002 | 1776194 | — | f | 1470 | 4679 | 0.0000 | 0.00 | 11.0990 | — | 62005 | — | — | 5.98 | — | — | — | 0e0-59193 | at3YvsDom3OJbrVk | — | /15Qmublyf7EHp7nxS9bLqYySBY4W8fEx1 | — |
| 2226784 | 20894 | 2026-10-25 11:41:23.516 | 1856 | 2026-10-25 11:41:25.020833 | 2026-10-25 11:41:25.31737 | 197 | 51927 | — | 22.8910 | 0.00 | dc50kw | Tesla | 24534.834 | 2.761 | Roaming - 002 | 1776202 | — | f | 2313 | 1856 | 0.0000 | 0.00 | 22.8910 | — | 5586 | 4 | — | 11.22 | — | — | — | 2b3-36569 | at3jnsDom3OJOvxJ | — | /SPBnwYm3Isvp74Egza2y | — |
| 2226783 | — | 2026-10-25 11:38:15.15 | 656 | 2026-10-25 11:38:17.382653 | 2026-10-25 11:38:17.382653 | 426 | — | — | 8.6520 | 0.00 | dc50kw | CCS1 | 9273.312 | 1.043 | Payter | 1776204 | payter | f | 2418 | 656 | 0.0000 | 0.99 | 0.0000 | — | — | — | — | 0.00 | — | — | 6.96 | s1v8-8120 | at3nl8Dom3OJhUOr | — | /La38eUBW2j7txBLpMx3O | — |
| 2226782 | — | 2026-10-25 11:27:31.978 | 2961 | 2026-10-25 11:27:38.607815 | 2026-10-25 11:27:38.607815 | 461 | — | — | 34.7630 | 0.00 | dc50kw | CCS1 | 37259.378 | 4.193 | Payter Cloud | 1776196 | payter | f | 2478 | 2961 | 0.0000 | 0.99 | 0.0000 | — | — | — | — | 0.00 | — | — | 18.02 | s1wd-1102 | at3cDMDom3OJrIIu | `(omitido)` | /UOGCm4aflcPA6Pa6LVYO | — |
| 2226781 | 85217 | 2026-10-25 11:25:36.508 | 5963 | 2026-10-25 11:25:37.890868 | 2026-10-25 11:25:38.446958 | 421 | 46606 | — | 12.9130 | 7.62 | dc50kw | CHAdeMO | 13840.300 | 1.557 | Roaming - 002 | 1776182 | — | f | 2514 | 5963 | 0.5900 | 0.00 | 0.0000 | `(omitido)` | 60583 | — | — | 0.99 | — | — | — | s1tr-6504 | at3P5MDom3OJybUN | — | /XVe7J0KoNWbxl00KLPio | — |
| 2226780 | 24886 | 2026-10-25 11:25:12.103 | 1568 | 2026-10-25 11:25:15.667183 | 2026-10-25 11:25:15.956817 | 196 | 34412 | — | 15.0175 | 0.00 | dc50kw | CCS1 | 16095.927 | 1.811 | Roaming - 002 | 1776199 | — | f | 1366 | 1568 | 0.0000 | 0.00 | 15.0175 | — | 8246 | 2 | — | 7.36 | — | — | — | 2b2-14417 | at3g9cDom3OJCWqj | — | /BQLxAzkihtjQb1uLVLAT | — |

**`sessions`** — Total histórico: **1.776.138** filas &middot; Últimos 3 meses: **133.990**

Cada fila es una sesión de carga. Es muy similar a la tabla anterior (su correspondencia es 1 a 1) con la única diferencia de que esta tiene información adicional producida por los cargadores eléctricos, que envían esto mediante protocolo OCPI: quién la inició, cuándo empezó/terminó, cuánta energía lleva entregada. `status`: 0 = en curso, 1 = completada. `end_date_time` vacío = todavía abierta en el momento de la consulta.

*Columnas con datos sensibles omitidas: `cdr_token`, `authorization_reference`, `pm_processor_id`, `widget_token` y `phone`.*

| `id` | `ocpi_id` | `start_date_time` | `end_date_time` | `kwh` | `total_cost_incl_vat` | `total_cost_excl_vat` | `cdr_token` | `authorization_reference` | `location_id` | `station_id` | `connector_id` | `status` | `created_at` | `updated_at` | `user_id` | `intent` | `coupon_codes` | `pm_processor_id` | `first_soc` | `last_soc` | `first_reading_at` | `last_reading_at` | `by_admin` | `code` | `phone` | `connection_id` | `cpo_id` | `price_per_kwh_discount` | `widget_token` | `ocpi_update_count` | `promo_id` | `emsp_id` | `power` | `max_power` | `current` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1776210 | 6addef2858b357affc7be42c | 2026-10-25 11:59:35.523 | — | 0.0110 | 1.00 | 1.00 | `(omitido)` | `(omitido)` | 367 | 2582 | 3275 | 0 | 2026-10-25 11:59:37.017456 | 2026-10-25 12:00:00.347095 | 38200 | — | {} | `(omitido)` | 24 | 24 | 2026-10-25 11:59:58.567 | 2026-10-25 11:59:58.567 | f | bb0c2d53 | — | — | 1 | 0 | `(omitido)` | 4 | — | — | 23.625 | 23.625 | 68.200 |
| 1776209 | 6addec41564cea48283f0da9 | 2026-10-25 11:47:12.449 | — | 9.1400 | 7.30 | 7.30 | `(omitido)` | `(omitido)` | 84 | 3039 | 3913 | 0 | 2026-10-25 11:47:13.733201 | 2026-10-25 11:59:13.787699 | 138033 | — | {} | `(omitido)` | 9 | 23 | 2026-10-25 11:48:12.614 | 2026-10-25 11:59:12.613 | f | 1133dd61 | — | — | 1 | 0 | `(omitido)` | 14 | — | — | 47.190 | 47.508 | 132.000 |
| 1776208 | 6addea6c807a88a4a7575d41 | 2026-10-25 11:39:23.429 | — | 16.6150 | 10.29 | 10.29 | `(omitido)` | `(omitido)` | 357 | 2565 | 3254 | 0 | 2026-10-25 11:39:24.910307 | 2026-10-25 11:59:56.166719 | 114077 | — | — | `(omitido)` | 36 | 65 | 2026-10-25 11:39:45.883 | 2026-10-25 11:59:54.158 | f | 51e2c88f | — | — | 1 | 0 | — | 156 | — | — | 49.621 | 49.621 | 130.000 |
| 1776207 | 6addea49a438dc2264abe677 | 2026-10-25 11:38:48.14 | — | 16.4640 | 12.35 | 12.35 | `(omitido)` | `(omitido)` | 174 | 3267 | 4183 | 0 | 2026-10-25 11:38:49.55403 | 2026-10-25 11:59:49.238436 | 105171 | — | — | `(omitido)` | 7 | 32 | 2026-10-25 11:39:12.044 | 2026-10-25 11:59:48.293 | f | 7701b147 | — | — | 1 | 0 | — | 69 | — | — | 48.084 | 48.093 | 133.900 |
| 1776206 | 6adde9b0807a88a4a7573e21 | 2026-10-25 11:36:13.547 | — | 2.5331 | — | — | `(omitido)` | — | 376 | 1967 | 2504 | 0 | 2026-10-25 11:36:16.315664 | 2026-10-25 12:00:01.881076 | — | — | {} | — | — | — | — | 2026-10-25 11:59:58.599 | f | 8aa74794 | — | 49118 | 1 | 0 | — | 99 | — | — | 6.493 | 6.522 | 31.630 |
| 1776205 | 6adde89e23490e74033fcabf | 2026-10-25 11:31:41.149 | — | 22.7200 | 16.67 | 16.67 | `(omitido)` | `(omitido)` | 84 | 3029 | 3908 | 0 | 2026-10-25 11:31:42.522537 | 2026-10-25 11:59:42.400102 | 81362 | — | {} | `(omitido)` | 13 | 44 | 2026-10-25 11:32:41.31 | 2026-10-25 11:59:41.31 | f | e2c99c80 | — | — | 1 | 0 | `(omitido)` | 33 | — | — | 49.848 | 49.848 | 131.700 |
| 1776204 | 6adde797807a88a4a756f026 | 2026-10-25 11:27:18.683 | 2026-10-25 11:38:15.15 | 8.6520 | 6.96 | 6.96 | `(omitido)` | — | 426 | 2418 | 3391 | 1 | 2026-10-25 11:27:19.969754 | 2026-10-25 11:38:17.31741 | — | — | {} | — | 12 | 23 | 2026-10-25 11:28:18.909 | 2026-10-25 11:38:15.15 | f | 5a499fdd | — | — | 1 | 0 | — | 15 | — | — | 0.000 | 49.843 | 0.000 |
| 1776203 | 6adde607807a88a4a756b271 | 2026-10-25 11:20:38 | — | 25.1580 | 18.35 | 18.35 | `(omitido)` | `(omitido)` | 484 | 2693 | 3411 | 0 | 2026-10-25 11:20:39.482359 | 2026-10-25 11:59:39.703731 | 139643 | pi_3UUPTcEWbleBd5sN0rMsNtJW | — | `(omitido)` | 13 | 44 | 2026-10-25 11:21:38 | 2026-10-25 11:59:38 | f | 0f66f957 | — | — | 1 | 0 | — | 41 | — | — | 40.000 | 40.000 | 100.000 |
| 1776202 | 6adde3a3564cea48283dbd1c | 2026-10-25 11:10:26.681 | 2026-10-25 11:41:23.516 | 22.8910 | 11.22 | 11.22 | `(omitido)` | `(omitido)` | 197 | 2313 | 2994 | 1 | 2026-10-25 11:10:27.905564 | 2026-10-25 11:41:24.970902 | 20894 | — | — | `(omitido)` | 59 | 97 | 2026-10-25 11:11:26.86 | 2026-10-25 11:41:23.516 | f | c26b22f5 | — | — | 1 | 0 | — | 38 | — | — | 0.000 | 49.811 | 0.100 |
| 1776201 | 6adde2dc58b357affc7aa65e | 2026-10-25 11:07:05.17 | — | 5.5689 | 3.72 | 3.72 | `(omitido)` | `(omitido)` | 353 | 1654 | 2105 | 0 | 2026-10-25 11:07:08.308768 | 2026-10-25 11:59:11.62425 | — | pi_3UUPGSEWbleBd5sN1CUqSojs | — | `(omitido)` | — | — | — | 2026-10-25 11:59:05.828 | f | a34479eb | `(omitido)` | — | 1 | 0 | — | 63 | — | — | 6.482 | 6.510 | 31.070 |

**`plans`** — Total histórico: **30** filas

Los planes que un usuario puede contratar. `start_hour`/`finish_hour` definen la ventana horaria “Off-Peak” (hoy 22h a 6h) con `price_per_kwh` más bajo que los planes regulares.

| `id` | `name` | `created_at` | `updated_at` | `monthly_price` | `yearly_price` | `icon_url` | `active` | `public` | `short_description` | `long_description` | `lockup_time` | `deleted_at` | `min_valid_charge_duration` | `start_hour` | `finish_hour` | `price_per_kwh` | `company_id` | `monthly_kwh` | `trial_days` | `weekly_price` | `weekly_kwh` | `trial_kwh` | `duration_days` | `display_banner` | `display_top_text` | `display_subtitle` | `display_under_subtitle` | `l2_price_per_kwh_discount` | `l3_price_per_kwh_discount` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 34 | Pioneer Market place | 2026-07-16 00:00:00 | 2026-09-04 20:32:59.066655 | 0.00 | 0.00 | — | t | f | — | — | 0 | — | 30 | — | — | 0.00 | — | 200.00 | — | — | — | — | — | — | — | — | — | 0 | 0 |
| 31 | Basic | 2025-01-29 12:45:40.3735 | 2025-02-10 19:17:06.464559 | 3.99 | 39.99 | — | t | t | Standard Pay As You Go $/kWh rates | — | 0 | — | 30 | — | — | — | — | 0.00 | — | — | — | — | — | — | — | — | — | — | — |
| 30 | Rideshare Premium | 2024-08-20 15:32:23.391323 | 2026-02-17 15:59:55.833897 | — | — | — | t | t | Effective rate ${{eff_rate}}/kWh /  / 10% Discount on Pay As You Go $/kWh rates after monthly allowance /  / No session fee | — | 0 | — | 30 | — | — | 0.35 | — | — | — | 45.00 | 165.00 | — | — | Rideshare Best Value | — | Weekly Energy Allowance | 578-644 miles range* | 10 | 10 |
| 29 | Rideshare At Night | 2024-08-20 15:31:09.439556 | 2026-02-17 16:00:29.625756 | — | — | — | t | t | Redeemable between {{start_hour}}-{{finish_hour}} /  / 10% Discount on Pay As You Go $/kWh rates after monthly allowance, or when charging between 6AM - 10PM /  / No session fee | — | 0 | — | 60 | 22 | 6 | 0.35 | — | — | — | 23.00 | 105.00 | — | — | — | — | Weekly Energy Allowance | 368 - 410 miles range* | 10 | 10 |
| 27 | Off-Peak | 2024-08-20 15:28:37.985416 | 2026-02-17 15:57:25.22768 | 99.99 | 1199.88 | — | t | t | Redeemable between {{start_hour}}-{{finish_hour}} /  / Effective rate ${{eff_rate}}/kWh /  / Standard Pay As You Go $/kWh rates after monthly allowance, or when charging between 6AM-10PM /  / No session fee | — | 0 | — | 30 | 22 | 6 | 0.39 | — | 400.00 | — | — | — | — | — | — | — | Monthly Energy Allowance | 1,400 - 1,560 miles range* | 0 | 0 |
| 26 | Premium | 2024-08-20 15:26:58.14698 | 2026-02-17 15:57:43.652755 | 199.99 | 2399.88 | — | t | t | Effective rate ${{eff_rate}}/kWh /  / Standard Pay As You Go $/kWh rates after monthly allowance /  / No session fee | — | 0 | — | 39 | — | — | 0.39 | — | 650.00 | — | — | — | — | — | Rideshare Best Value | — | Monthly Energy Allowance | 2,275 - 2,535 miles range* | 0 | 0 |
| 25 | Yuval Sites Free Charging | 2023-08-09 20:42:53.10678 | 2025-07-01 02:35:24.105691 | 0.00 | — | — | t | f | — | — | 0 | — | 60 | — | — | 0.00 | — | — | 0 | — | — | — | — | — | — | — | — | 100 | 100 |
| 24 | Trial Testing Plan | 2023-08-08 17:08:40.813077 | 2024-09-04 19:07:18.889725 | 49.99 | — | — | f | f | — | — | 0 | — | 60 | — | — | 0.33 | — | 200.00 | — | — | — | — | 7 | — | — | — | — | — | — |
| 23 | Essential Charge | 2023-06-28 15:48:28.182907 | 2023-07-06 17:38:24.707427 | — | — | https://admin.evcs.com/media/63ff73175da73_md.png | f | t | — | — | 0 | — | 30 | — | — | 0.39 | — | — | 0 | 11.00 | 30.00 | — | 7 | — | — | — | — | — | — |
| 22 | Complete Charge | 2023-06-28 15:47:37.666665 | 2023-07-06 17:38:29.507598 | — | — | https://admin.evcs.com/media/63ff73175da73_md.png | f | t | — | — | 0 | — | 30 | — | — | 0.39 | — | — | 0 | 25.00 | 80.00 | — | 7 | — | — | — | — | — | — |

### Plan de técnicas

| Técnica a aplicar | Resultado esperado (ideal) |
|---|---|
| Regresión logística / KNN / SVM / Naive Bayes sobre el historial y perfil del usuario (sin usar el horario de la sesión que se quiere predecir) | Un clasificador que estime, *antes* de que ocurra la próxima carga, la probabilidad de que esa sesión caiga en horario pico o valle — para poder intervenir con anticipación (ej. decidir a la mañana a qué usuarios mandarles el incentivo), no para redescubrir un dato que ya se tiene una vez que la carga ya pasó. |
| ACP sobre el perfil horario de 24 horas de cada usuario | Resumir el hábito de carga de cada usuario en 2 o 3 ejes interpretables (ej. “diurno” vs. “nocturno”). Cuidado: al ser cada fila una composición que suma 1, el ACP clásico puede mostrar correlaciones negativas artificiales — evaluar una transformación log-ratio (CLR) antes de interpretar los componentes. |
| Clustering (K-means) sobre esos ejes | Segmentos de usuarios claros y accionables (ej. “nocturnos”, “de mediodía”, “commuters”) para dirigirles campañas distintas. |
| Estimación de punto ideal (IRT bayesiano) sobre un puñado de preguntas binarias compartidas por sesión (¿franja valle?, ¿fin de semana?, ¿estación de alta demanda?, ¿incentivo activo?) | Un puntaje individual por usuario que mida qué tan “amigable al horario valle” es, útil para priorizar a quién conviene incentivar primero. |
| Grafo de proximidad sobre esos puntajes | Dado un usuario que ya cambió su hábito con éxito, encontrar a los usuarios más parecidos a él para ofrecerles la misma campaña. |

---

## Idea 2 — Cargadores en riesgo

### Dominio / problema
Cada cargador reporta continuamente su propio estado. Cuando uno queda en un estado inválido (`outoforder`, `inoperative`, `unknown`), hoy nadie lo detecta hasta que un usuario se queja, un técnico lo nota en una visita de rutina o personal de EVCS lo consulta explícitamente a través de su dashboard. 
La operación para identificar y reparar estos cargadores es lenta, y no existe una forma de priorizar qué ubicaciones atender primero —por ejemplo, las que tienen más cargadores o un uso más intensivo deberían priorizarse sobre las demás.

### Fenómeno (objeto de estudio)
El estado de un cargador a lo largo del tiempo, en particular sus transiciones hacia estados inválidos o no operativos (`outoforder`, `inoperative`, `unknown`).

### Pregunta concreta
¿Qué cargadores tienen mayor probabilidad de fallar pronto? ¿Qué ubicaciones deberían priorizarse para mantenimiento preventivo?

### Meta
Determinar un modelo que prediga, para cada cargador, su probabilidad de pasar a un estado inválido en el corto plazo, e identificar grupos de cargadores con patrones de falla similares para actuar sobre todo el grupo en lugar de uno por uno.

### Impacto en el negocio
Priorizar las visitas de mantenimiento según el riesgo real de cada cargador y ubicación, reduciendo el tiempo que un cargador pasa fuera de servicio y evitando que un usuario llegue a una estación que no funciona.
También es información muy valiosa para la toma de decisiones sobre la inversión en nuevos cargadores.

### Tablas involucradas

**`station_statuses`** — Total histórico: **44.388.424** filas &middot; Últimos 3 meses: **2.757.441 (estimado)**

Cada fila es un evento de estado de un cargador. `status`: 0 = available, 2 = charging, 3 = inoperative, 4 = outoforder, 8 = unknown. Es la tabla más grande de todo el sistema: no tiene `updated_at` ni duración explícita por estado, cada fila es un evento puntual.

| `id` | `station_id` | `status` | `created_at` |
|---|---|---|---|
| 44388378 | 4212 | 4 | 2026-10-25 11:58:52.929411 |
| 44388377 | 4212 | 0 | 2026-10-25 11:58:52.324411 |
| 44388376 | 3640 | 4 | 2026-10-25 11:58:49.649618 |
| 44388375 | 3642 | 4 | 2026-10-25 11:58:49.353643 |
| 44388374 | 3640 | 0 | 2026-10-25 11:58:48.526993 |
| 44388373 | 3642 | 0 | 2026-10-25 11:58:48.219416 |
| 44388372 | 2564 | 0 | 2026-10-25 11:58:45.239881 |
| 44388371 | 2563 | 0 | 2026-10-25 11:58:45.228104 |
| 44388370 | 1471 | 4 | 2026-10-25 11:58:44.623624 |
| 44388369 | 1471 | 0 | 2026-10-25 11:58:44.051164 |

**`stations`** — Total histórico: **3.623** filas

Cada fila es un cargador físico instalado. 

| `id` | `location_id` | `created_at` | `updated_at` | `name` | `available_status` | `kw` | `last_synched_at` | `deleted_at` | `ocpi_id` | `make` | `model` | `serial_number` | `emi3_id` | `tariff_id` | `custom_status` | `visible` | `conn_chademo_count` | `conn_tesla_count` | `conn_ccs1_count` | `conn_type1_count` | `plug_and_charge` | `alias` | `capabilities` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4274 | 537 | 2026-10-20 23:25:37.952654 | 2026-10-25 04:30:03.428701 | 115917901 | AVAILABLE | 50 | 2026-10-25 04:30:03.425639 | — | 6ad7f871d717e27888b4adf7 | — | — | — | US*NDO*Enev1159179*2 | 1750 | — | t | 0 | 0 | 1 | 0 | t | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4273 | 537 | 2026-10-20 23:25:37.754544 | 2026-10-25 04:30:03.287764 | 115917900 | AVAILABLE | 50 | 2026-10-25 04:30:03.283981 | — | 6ad7f871d717e27888b4adf1 | — | — | — | US*NDO*Enev1159179*1 | 1750 | — | t | 0 | 1 | 0 | 0 | t | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4272 | 537 | 2026-10-20 19:09:37.537995 | 2026-10-25 04:30:05.050276 | 115917501 | AVAILABLE | 50 | 2026-10-25 04:30:05.048471 | — | 6ad7bc50d717e27888aae0ff | — | — | — | US*NDO*Enev1159175*2 | 1750 | — | t | 0 | 0 | 1 | 0 | f | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4271 | 537 | 2026-10-20 19:09:04.737309 | 2026-10-25 04:29:46.853145 | 115917500 | AVAILABLE | 50 | 2026-10-25 04:29:46.849552 | — | 6ad7bc50d717e27888aae0f7 | — | — | — | US*NDO*Enev1159175*1 | 1750 | — | t | 0 | 1 | 0 | 0 | t | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4270 | 537 | 2026-10-20 19:08:43.981322 | 2026-10-25 03:53:11.592079 | 115917600 | AVAILABLE | 50 | 2026-10-25 03:53:11.589816 | — | 6ad7bc35d717e27888aad3dc | — | — | — | US*NDO*Enev1159176*1 | 1750 | — | t | 0 | 1 | 0 | 0 | t | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4269 | 537 | 2026-10-20 19:08:38.477655 | 2026-10-25 03:53:11.583926 | 115917601 | AVAILABLE | 50 | 2026-10-25 03:53:11.58173 | — | 6ad7bc35d717e27888aad3e3 | — | — | — | US*NDO*Enev1159176*2 | 1750 | — | t | 0 | 0 | 1 | 0 | f | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4268 | 537 | 2026-10-20 19:08:11.376204 | 2026-10-25 05:22:43.62113 | 115917701 | AVAILABLE | 50 | 2026-10-25 05:22:43.618813 | — | 6ad7bc1ad717e27888aac23c | — | — | — | US*NDO*Enev1159177*2 | 1750 | — | t | 0 | 0 | 1 | 0 | f | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4267 | 537 | 2026-10-20 19:08:11.14919 | 2026-10-25 05:22:43.617898 | 115917700 | AVAILABLE | 50 | 2026-10-25 05:22:43.616092 | — | 6ad7bc1ad717e27888aac232 | — | — | — | US*NDO*Enev1159177*1 | 1750 | — | t | 0 | 1 | 0 | 0 | t | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4266 | 537 | 2026-10-20 19:07:39.949534 | 2026-10-25 04:36:42.899456 | 115917801 | AVAILABLE | 50 | 2026-10-25 04:36:42.897678 | — | 6ad7bbf9d717e27888aaab2b | — | — | — | US*NDO*Enev1159178*2 | 1750 | — | t | 0 | 0 | 1 | 0 | f | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4265 | 537 | 2026-10-20 19:07:39.188044 | 2026-10-25 04:36:42.572096 | 115917800 | AVAILABLE | 50 | 2026-10-25 04:36:42.570281 | — | 6ad7bbf9d717e27888aaab21 | — | — | — | US*NDO*Enev1159178*1 | 1750 | — | t | 0 | 1 | 0 | 0 | t | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |

### Plan de técnicas

| Técnica a aplicar | Resultado esperado (ideal) |
|---|---|
| Regresión logística / SVM / Naive Bayes sobre el historial de estados de cada cargador | Un clasificador que prediga la probabilidad de que un cargador puntual pase a estado inválido en los próximos días. |
| Clustering sobre la “firma de fallas” de cada cargador | Grupos de cargadores con el mismo patrón de fallas (mismo modelo, misma zona) para actuar sobre el grupo entero en lugar de uno por uno. |
| ACP sobre las variables de estado agregadas por cargador (uptime %, cantidad de transiciones, tiempo medio entre fallas) | Simplificar decenas de métricas por cargador en pocos ejes que resuman su “salud”, antes de clusterizar o alimentar el clasificador. |

---

NOTA MUY IMPORTANTE: Muchas señales de "inválido" de un cargador no implican mayor tiempo de "downtime", voy a necesitar mucho trabajo de pre-procesamiento para traducir estos "cambio de estados puntuales" a la totalidad de tiempo en que un cargador no está operativo.
Por otra parte, muchas señales de "inválido" podrían indicar otro fenómeno indeseable llamado "station flapping" donde un cargador pasa repetidamente de estado válido a inválido y viceversa en un corto período de tiempo (lo que puede derivar en una mala experiencia de usuario y la contaminación de nuestros datos).

## Idea 3 — Intentos de carga que fallan

### Dominio / problema
Cuando un usuario intenta iniciar una carga —sea pasando su tarjeta en el cargador o desde la app—, a veces ese intento nunca se concreta como una carga real. El sistema igual recibe, de parte del operador del cargador, un aviso de "carga finalizada" pero con 0 kWh entregados: hubo un intento real en el mundo físico que falló antes de arrancar. Hoy este fenómeno se mezcla con el resto de las cargas y no hay un análisis sistemático de cuándo y por qué ocurre.

### Fenómeno (objeto de estudio)
Los intentos de carga que nunca llegan a iniciarse de verdad, reportados por el cargador o su operador externo sin energía entregada. En el sistema esto se ve como una request HTTP diseñada para que los operadores aporten información `POST mgmt/v1/charges` que llega con `kwh = 0` y sin `session_id` local (porque las requests HTTP del protocolo OCPI nunca existieron). 

### Pregunta concreta
¿Qué características —cargador, modelo, horario, forma de pago— predicen que un intento de carga vaya a fallar?

### Meta
Identificar los modelos de cargador, canales de pago y horarios con mayor tasa de intentos fallidos, y un modelo que prediga la probabilidad de que un intento de carga en curso vaya a fallar.

### Impacto en el negocio
Señalar a los fabricantes o modelos de cargador con fallas sistémicas de integración para reclamar reparación o reemplazo, mejorar la experiencia del usuario en el momento de iniciar la carga y reducir los reclamos por "la carga no funcionó".

### Tablas involucradas

**`charges`** — Total histórico: **2.073.650** filas &middot; Últimos 3 meses: **158.523**

Cada fila es una carga finalizada: quién la hizo, cuánta energía se entregó (`kwh`), cuánto duró (`duration`, en segundos) y cómo se pagó. `session_id`/`cpo_session_id` muestran si quedó sin vincular a una información OCPI.

*Columnas con datos sensibles omitidas: `notes`, `rfid` y `cpo_last_4` se muestran como `(omitido)` cuando tienen valor: son texto libre o identificadores de tarjeta/credencial — no aportan al análisis y no corresponde dejarlos en texto plano en un documento versionado.*

| `id` | `user_id` | `completed_at` | `duration` | `created_at` | `updated_at` | `location_id` | `subscription_id` | `deleted_at` | `kwh` | `price` | `charger_type` | `connector` | `co2_saved` | `gas_saved` | `payment_method` | `session_id` | `payment_gateway` | `during_trial_period` | `station_id` | `charging_duration` | `price_per_kwh` | `session_fee` | `free_kwh` | `notes` | `user_car_id` | `created_from` | `trial_kwh` | `total_discount` | `rating` | `cpo_user_id` | `cpo_price` | `cpo_session_id` | `cpo_encoded_id` | `cpo_last_4` | `cpo_location_id` | `rfid` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2226790 | 103692 | 2026-10-25 11:50:01.727 | 3199 | 2026-10-25 11:50:04.84023 | 2026-10-25 11:50:05.112592 | 478 | 53021 | — | 42.9872 | 0.00 | dc50kw | CCS1 | 46074.169 | 5.184 | Roaming - 002 | 1776198 | — | f | 2646 | 3199 | 0.0000 | 0.00 | 42.9872 | — | 79181 | — | — | 30.65 | — | — | — | s22n-1307 | at3gY8Dom3OJ_oy7 | — | /cRYuSBy3rmoySTWuXxhX | — |
| 2226789 | — | 2026-10-25 11:46:05.119 | 0 | 2026-10-25 11:46:05.798724 | 2026-10-25 11:46:05.798724 | 84 | — | — | 0.0000 | 0.00 | dc50kw | — | 0.000 | 0.000 | Roaming - 002 | — | — | f | 3039 | 0 | 0.0000 | 0.99 | 0.0000 | — | — | — | — | 0.00 | — | — | — | 099-27364 | at3r_MDom3OJ1rKA | — | /YlexdtO476u4LG7ZfT0ehPi4Di4B | — |
| 2226788 | — | 2026-10-25 11:45:25.773 | 0 | 2026-10-25 11:45:26.741205 | 2026-10-25 11:45:26.741205 | 84 | — | — | 0.0000 | 0.00 | dc50kw | — | 0.000 | 0.000 | Roaming - 002 | — | — | f | 3039 | 0 | 0.0000 | 0.99 | 0.0000 | — | — | — | — | 0.00 | — | — | — | 099-27363 | at3rjsDom3OJztzJ | — | /YlexdtO476u4LG7ZfT0ehPi4Di4B | — |
| 2226787 | 140114 | 2026-10-25 11:43:06.807 | 4409 | 2026-10-25 11:43:09.788217 | 2026-10-25 11:43:16.600853 | 356 | — | — | 36.8877 | 22.75 | dc50kw | CCS1 | 39536.656 | 4.449 | Roaming - 002 | 1776195 | — | f | 1678 | 4409 | 0.5900 | 0.99 | 0.0000 | `(omitido)` | 113647 | — | — | 0.00 | -1 | — | — | 420-6559 | at3aEcDom3OJiEe6 | — | /6m54fBrXIjsSeoZ3imsR | — |
| 2226785 | 86613 | 2026-10-25 11:41:57.652 | 4679 | 2026-10-25 11:41:59.487534 | 2026-10-25 11:41:59.827235 | 50 | 50286 | — | 11.0990 | 0.00 | dc50kw | CCS1 | 11896.034 | 1.339 | Roaming - 002 | 1776194 | — | f | 1470 | 4679 | 0.0000 | 0.00 | 11.0990 | — | 62005 | — | — | 5.98 | — | — | — | 0e0-59193 | at3YvsDom3OJbrVk | — | /15Qmublyf7EHp7nxS9bLqYySBY4W8fEx1 | — |
| 2226784 | 20894 | 2026-10-25 11:41:23.516 | 1856 | 2026-10-25 11:41:25.020833 | 2026-10-25 11:41:25.31737 | 197 | 51927 | — | 22.8910 | 0.00 | dc50kw | Tesla | 24534.834 | 2.761 | Roaming - 002 | 1776202 | — | f | 2313 | 1856 | 0.0000 | 0.00 | 22.8910 | — | 5586 | 4 | — | 11.22 | — | — | — | 2b3-36569 | at3jnsDom3OJOvxJ | — | /SPBnwYm3Isvp74Egza2y | — |
| 2226783 | — | 2026-10-25 11:38:15.15 | 656 | 2026-10-25 11:38:17.382653 | 2026-10-25 11:38:17.382653 | 426 | — | — | 8.6520 | 0.00 | dc50kw | CCS1 | 9273.312 | 1.043 | Payter | 1776204 | payter | f | 2418 | 656 | 0.0000 | 0.99 | 0.0000 | — | — | — | — | 0.00 | — | — | 6.96 | s1v8-8120 | at3nl8Dom3OJhUOr | — | /La38eUBW2j7txBLpMx3O | — |
| 2226782 | — | 2026-10-25 11:27:31.978 | 2961 | 2026-10-25 11:27:38.607815 | 2026-10-25 11:27:38.607815 | 461 | — | — | 34.7630 | 0.00 | dc50kw | CCS1 | 37259.378 | 4.193 | Payter Cloud | 1776196 | payter | f | 2478 | 2961 | 0.0000 | 0.99 | 0.0000 | — | — | — | — | 0.00 | — | — | 18.02 | s1wd-1102 | at3cDMDom3OJrIIu | `(omitido)` | /UOGCm4aflcPA6Pa6LVYO | — |
| 2226781 | 85217 | 2026-10-25 11:25:36.508 | 5963 | 2026-10-25 11:25:37.890868 | 2026-10-25 11:25:38.446958 | 421 | 46606 | — | 12.9130 | 7.62 | dc50kw | CHAdeMO | 13840.300 | 1.557 | Roaming - 002 | 1776182 | — | f | 2514 | 5963 | 0.5900 | 0.00 | 0.0000 | `(omitido)` | 60583 | — | — | 0.99 | — | — | — | s1tr-6504 | at3P5MDom3OJybUN | — | /XVe7J0KoNWbxl00KLPio | — |
| 2226780 | 24886 | 2026-10-25 11:25:12.103 | 1568 | 2026-10-25 11:25:15.667183 | 2026-10-25 11:25:15.956817 | 196 | 34412 | — | 15.0175 | 0.00 | dc50kw | CCS1 | 16095.927 | 1.811 | Roaming - 002 | 1776199 | — | f | 1366 | 1568 | 0.0000 | 0.00 | 15.0175 | — | 8246 | 2 | — | 7.36 | — | — | — | 2b2-14417 | at3g9cDom3OJCWqj | — | /BQLxAzkihtjQb1uLVLAT | — |

**`stations`** — Total histórico: **3.623** filas

Cada fila es un cargador físico instalado.

| `id` | `location_id` | `created_at` | `updated_at` | `name` | `available_status` | `kw` | `last_synched_at` | `deleted_at` | `ocpi_id` | `make` | `model` | `serial_number` | `emi3_id` | `tariff_id` | `custom_status` | `visible` | `conn_chademo_count` | `conn_tesla_count` | `conn_ccs1_count` | `conn_type1_count` | `plug_and_charge` | `alias` | `capabilities` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4274 | 537 | 2026-10-20 23:25:37.952654 | 2026-10-25 04:30:03.428701 | 115917901 | AVAILABLE | 50 | 2026-10-25 04:30:03.425639 | — | 6ad7f871d717e27888b4adf7 | — | — | — | US*NDO*Enev1159179*2 | 1750 | — | t | 0 | 0 | 1 | 0 | t | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4273 | 537 | 2026-10-20 23:25:37.754544 | 2026-10-25 04:30:03.287764 | 115917900 | AVAILABLE | 50 | 2026-10-25 04:30:03.283981 | — | 6ad7f871d717e27888b4adf1 | — | — | — | US*NDO*Enev1159179*1 | 1750 | — | t | 0 | 1 | 0 | 0 | t | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4272 | 537 | 2026-10-20 19:09:37.537995 | 2026-10-25 04:30:05.050276 | 115917501 | AVAILABLE | 50 | 2026-10-25 04:30:05.048471 | — | 6ad7bc50d717e27888aae0ff | — | — | — | US*NDO*Enev1159175*2 | 1750 | — | t | 0 | 0 | 1 | 0 | f | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4271 | 537 | 2026-10-20 19:09:04.737309 | 2026-10-25 04:29:46.853145 | 115917500 | AVAILABLE | 50 | 2026-10-25 04:29:46.849552 | — | 6ad7bc50d717e27888aae0f7 | — | — | — | US*NDO*Enev1159175*1 | 1750 | — | t | 0 | 1 | 0 | 0 | t | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4270 | 537 | 2026-10-20 19:08:43.981322 | 2026-10-25 03:53:11.592079 | 115917600 | AVAILABLE | 50 | 2026-10-25 03:53:11.589816 | — | 6ad7bc35d717e27888aad3dc | — | — | — | US*NDO*Enev1159176*1 | 1750 | — | t | 0 | 1 | 0 | 0 | t | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4269 | 537 | 2026-10-20 19:08:38.477655 | 2026-10-25 03:53:11.583926 | 115917601 | AVAILABLE | 50 | 2026-10-25 03:53:11.58173 | — | 6ad7bc35d717e27888aad3e3 | — | — | — | US*NDO*Enev1159176*2 | 1750 | — | t | 0 | 0 | 1 | 0 | f | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4268 | 537 | 2026-10-20 19:08:11.376204 | 2026-10-25 05:22:43.62113 | 115917701 | AVAILABLE | 50 | 2026-10-25 05:22:43.618813 | — | 6ad7bc1ad717e27888aac23c | — | — | — | US*NDO*Enev1159177*2 | 1750 | — | t | 0 | 0 | 1 | 0 | f | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4267 | 537 | 2026-10-20 19:08:11.14919 | 2026-10-25 05:22:43.617898 | 115917700 | AVAILABLE | 50 | 2026-10-25 05:22:43.616092 | — | 6ad7bc1ad717e27888aac232 | — | — | — | US*NDO*Enev1159177*1 | 1750 | — | t | 0 | 1 | 0 | 0 | t | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4266 | 537 | 2026-10-20 19:07:39.949534 | 2026-10-25 04:36:42.899456 | 115917801 | AVAILABLE | 50 | 2026-10-25 04:36:42.897678 | — | 6ad7bbf9d717e27888aaab2b | — | — | — | US*NDO*Enev1159178*2 | 1750 | — | t | 0 | 0 | 1 | 0 | f | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4265 | 537 | 2026-10-20 19:07:39.188044 | 2026-10-25 04:36:42.572096 | 115917800 | AVAILABLE | 50 | 2026-10-25 04:36:42.570281 | — | 6ad7bbf9d717e27888aaab21 | — | — | — | US*NDO*Enev1159178*1 | 1750 | — | t | 0 | 1 | 0 | 0 | t | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |

### Plan de técnicas

| Técnica a aplicar | Resultado esperado (ideal) |
|---|---|
| Regresión logística / SVM / Naive Bayes sobre el contexto de cada intento de carga | Un clasificador que prediga la probabilidad de que un intento de carga en curso vaya a fallar. |
| Clustering de cargadores/modelos según su tasa y tipo de fallas | Señalar un fabricante o modelo específico como responsable de la mayoría de los intentos fallidos — la concentración observada ya aparece a nivel de *modelo*, no de unidad aislada. |
| ACP sobre las variables agregadas por cargador/modelo | Simplificar las métricas de falla de cada cargador en pocos ejes interpretables antes de agruparlos. |

---

## Idea 4 — Dónde instalar el próximo cargador

### Dominio / problema
EVCS evalúa continuamente dónde instalar nuevos cargadores, pero hoy esa decisión se apoya sobre todo en criterios comerciales y cualitativos, sin un análisis sistemático de qué características hacen que una ubicación existente tenga alta utilización.

### Fenómeno (objeto de estudio)
La utilización y el rendimiento (ingreso, sesiones, kWh entregados) de las ubicaciones ya instaladas, en función de sus características (tipo de conectores, potencia, zona geográfica).

### Pregunta concreta
¿Qué características de una ubicación predicen que va a tener alta utilización? Dado un sitio candidato nuevo, ¿qué utilización se puede esperar?

### Meta
Encontrar arquetipos de ubicación según su comportamiento de uso, y un modelo que estime la utilización o el ingreso esperado de un sitio nuevo en base a ubicaciones comparables ya existentes.

### Impacto en el negocio
Priorizar la expansión de la red de cargadores hacia los sitios con mayor potencial de uso, mejorando el retorno de la inversión de cada instalación nueva.

### Tablas involucradas

**`locations`** — Total histórico: **364** filas

Cada fila es una ubicación física que agrupa uno o más cargadores. `ac_count`/`dc_count`: cantidad de cargadores lentos (AC) y rápidos (DC) en esa ubicación.

*Columnas con datos sensibles omitidas: `gatecode` se muestra como `(omitido)` cuando tiene valor: es el código de acceso físico a la ubicación.*

| `id` | `noodoe_id` | `name` | `subscriptions_enabled` | `deleted_at` | `created_at` | `updated_at` | `latitude` | `longitude` | `noodoe_image_urls` | `visible` | `ocpi_id` | `coming_soon` | `coming_soon_level_two` | `coming_soon_level_three` | `gatecode` | `directions` | `last_synched_at` | `private` | `image_url` | `cpo_site_id` | `street_address` | `city` | `state` | `zip_code` | `country` | `ac_count` | `dc_count` | `conn_chademo_count` | `conn_tesla_count` | `conn_ccs1_count` | `conn_type1_count` | `commissioned` | `code` | `third_party_integration_id` | `banner_title` | `banner_description` | `app_enabled` | `tou_enabled` | `promo_image_url` | `commissioned_at` | `decommissioned_at` | `ocpi_publish` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 538 | — | ARTEX Synthetic Site D1 4284 | t | — | 2026-10-22 02:05:14.488433 | 2026-10-25 07:15:56.79291 | 34.0522000 | -118.2437000 | {} | t | 6ad96f42d7ec1b75bdf13115 | f | — | — | — | — | 2026-10-25 07:15:56.792486 | f | — | s3d9 | 4284 Synthetic Test Ave | Los Angeles | CA | 90001 | US | 0 | 0 | 0 | 0 | 0 | 0 | f | c3470acc | 1 | — | — | t | f | — | — | — | t |
| 537 | — | Agua Caliente Palm Springs Fuel (AC Fuel PS) | t | — | 2026-10-20 19:00:01.96726 | 2026-10-25 07:47:40.593406 | 33.8088330 | -116.4843667 | {https://static-prod.noodoe.com/charger-photo/s3ck-img-1.jpg?v=1792701724510} | t | 6ad7ba2d79a4c155ca6eefc7 | f | — | — | — | — | 2026-10-25 07:15:56.6762 | f | https://admin.evcs.com/media/6ada756f4bf56.jpeg | s3ck | 999 Lawrence Crossley Road | Palm Springs | CA | 92264 | US | 0 | 16 | 0 | 8 | 8 | 0 | t | 504eefea | 1 | — | — | t | f | — | 2026-10-22 20:42:57.394621 | — | t |
| 536 | — | Mobility Development - South El Monte | t | — | 2026-09-28 18:44:20.871686 | 2026-10-25 07:15:56.624432 | 34.0462537 | -118.0463916 | {} | f | 6abab573a3981bc92960842a | f | — | — | — | — | 2026-10-25 07:15:56.624098 | t | — | s3bv | 1530 Central Avenue | South El Monte | CA | 91733-3304 | US | 6 | 0 | 0 | 0 | 0 | 6 | t | fa75f5ed | 1 | — | — | t | t | — | 2026-10-01 17:45:52.268397 | — | f |
| 535 | — | South El Monte Community Center | t | — | 2026-09-28 18:11:30.312733 | 2026-10-25 07:15:56.596471 | 34.0462124 | -118.0464079 | {https://static-prod.noodoe.com/charger-photo/s3bu-img-1.jpg?v=1790876860750} | t | 6abaadca5a6f92c5cc14ada1 | f | — | — | — | — | 2026-10-25 07:15:56.596114 | f | https://admin.evcs.com/media/6abe9cedd6a7f.jpeg | s3bu | 1530 Central Avenue | South El Monte | CA | 91733-3304 | US | 2 | 0 | 0 | 0 | 0 | 2 | t | 5fb8f4fa | 1 | — | — | t | f | — | 2026-10-01 17:45:36.150544 | — | f |
| 534 | — | Cowlitz Crossing - Fuel And Convenience Store | t | — | 2026-09-14 21:54:48.255472 | 2026-10-25 10:42:46.306372 | 45.8501849 | -122.7053043 | {https://static-prod.noodoe.com/charger-photo/s3b8-img-1.jpg?v=1789766222060} | t | 6aa86d178d76f3881ca33ed4 | f | — | — | — | — | 2026-10-25 07:15:56.52162 | f | — | s3b8 | 31801 Northwest 31st Avenue | Ridgefield | WA | 98642 | US | 0 | 8 | 0 | 4 | 4 | 0 | t | 7f8e3760 | 1 | — | — | t | f | — | 2026-09-18 21:18:20.908897 | — | f |
| 533 | — | Yelm Cinemas | t | — | 2026-09-09 01:16:38.280304 | 2026-10-25 07:15:56.456306 | 46.9400255 | -122.5997222 | {} | t | 6aa0b36c196b81ed1f42d9ee | f | — | — | — | — | 2026-10-25 07:15:56.455949 | f | https://admin.evcs.com/media/6aac44578c68e.jpg | s3aw | 201 Prairie Park Ln SE | Yelm | WA | 98597 | US | 0 | 8 | 1 | 0 | 7 | 0 | t | 78f4d676 | 1 | — | — | t | t | — | 2026-09-14 21:10:32.585424 | — | f |
| 532 | — | Greenbank Farm | t | — | 2026-07-31 20:12:58.405796 | 2026-10-25 09:17:45.841257 | 48.1054503 | -122.5730721 | {https://static-prod.noodoe.com/charger-photo/s375-img-1.jpg?v=1786408611531} | t | 6a6d01ca130f78a310e09a02 | f | — | — | — | — | 2026-10-25 07:15:56.344746 | f | — | s375 | 765 Wonn Road | Greenbank | WA | 98253 | US | 6 | 6 | 0 | 0 | 6 | 6 | t | 0587a46a | 1 | — | — | t | t | — | 2026-08-10 23:57:18.844951 | — | t |
| 531 | — | East County Thriftway Elma | t | — | 2026-07-31 17:02:46.503813 | 2026-10-25 07:15:56.282685 | 47.0010371 | -123.4092354 | {https://static-prod.noodoe.com/charger-photo/s374-img-1.jpg?v=1790089518050} | t | 6a6cd52c8fb37979e00bfc59 | f | — | — | — | — | 2026-10-25 07:15:56.282308 | f | — | s374 | 325 South 5th Street | Elma | WA | 98541 | US | 0 | 6 | 0 | 0 | 6 | 0 | t | 5d9b06e5 | 1 | — | — | t | f | — | 2026-08-11 00:48:14.792936 | — | t |
| 530 | — | LA Fitness - Tacoma Pacific | t | — | 2026-07-31 16:47:41.567382 | 2026-10-25 07:15:56.19941 | 47.1143794 | -122.4324124 | {https://static-prod.noodoe.com/charger-photo/s373-img-1.jpg?v=1786131360989} | t | 6a6cd1a320852c2754f5ff2f | f | — | — | — | — | 2026-10-25 07:15:56.199031 | f | — | s373 | 15707 Pacific Avenue South | Spanaway | WA | 98444 | US | 1 | 8 | 1 | 0 | 7 | 1 | t | 1db73d46 | 1 | — | — | t | f | — | 2026-08-07 21:01:53.253348 | — | t |
| 529 | — | Warm Springs-South Fremont BART Station | t | — | 2026-07-30 16:47:18.168679 | 2026-10-25 07:24:13.710274 | 37.5023342 | -121.9363369 | {https://static-prod.noodoe.com/charger-photo/s372-img-1.jpg?v=1787091707725} | t | 6a6b80083a7ef661b75fc1cc | f | — | — | — | Parking payment: Required Monday–Friday, 4:00 AM–3:00 PM. No payment required on weekends or BART parking holidays. Color-coded signs at each charging stall indicate which payment type applies to that specific space, and vehicles may park in EV parking for up to 24 hours. | 2026-10-25 07:15:55.895281 | f | — | s372 | 45193 Warm Springs Boulevard | Fremont | CA | 94539 | US | 40 | 0 | 0 | 0 | 0 | 40 | t | a9060deb | 1 | — | — | t | f | — | 2026-08-11 18:53:58.193398 | — | f |

**`stations`** — Total histórico: **3.623** filas

Cada fila es un cargador físico instalado. `make`/`model` vacíos en varias de las filas más recientes: son cargadores recién dados de alta a los que todavía no les llegó la sincronización de datos del fabricante.

| `id` | `location_id` | `created_at` | `updated_at` | `name` | `available_status` | `kw` | `last_synched_at` | `deleted_at` | `ocpi_id` | `make` | `model` | `serial_number` | `emi3_id` | `tariff_id` | `custom_status` | `visible` | `conn_chademo_count` | `conn_tesla_count` | `conn_ccs1_count` | `conn_type1_count` | `plug_and_charge` | `alias` | `capabilities` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 4274 | 537 | 2026-10-20 23:25:37.952654 | 2026-10-25 04:30:03.428701 | 115917901 | AVAILABLE | 50 | 2026-10-25 04:30:03.425639 | — | 6ad7f871d717e27888b4adf7 | — | — | — | US*NDO*Enev1159179*2 | 1750 | — | t | 0 | 0 | 1 | 0 | t | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4273 | 537 | 2026-10-20 23:25:37.754544 | 2026-10-25 04:30:03.287764 | 115917900 | AVAILABLE | 50 | 2026-10-25 04:30:03.283981 | — | 6ad7f871d717e27888b4adf1 | — | — | — | US*NDO*Enev1159179*1 | 1750 | — | t | 0 | 1 | 0 | 0 | t | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4272 | 537 | 2026-10-20 19:09:37.537995 | 2026-10-25 04:30:05.050276 | 115917501 | AVAILABLE | 50 | 2026-10-25 04:30:05.048471 | — | 6ad7bc50d717e27888aae0ff | — | — | — | US*NDO*Enev1159175*2 | 1750 | — | t | 0 | 0 | 1 | 0 | f | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4271 | 537 | 2026-10-20 19:09:04.737309 | 2026-10-25 04:29:46.853145 | 115917500 | AVAILABLE | 50 | 2026-10-25 04:29:46.849552 | — | 6ad7bc50d717e27888aae0f7 | — | — | — | US*NDO*Enev1159175*1 | 1750 | — | t | 0 | 1 | 0 | 0 | t | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4270 | 537 | 2026-10-20 19:08:43.981322 | 2026-10-25 03:53:11.592079 | 115917600 | AVAILABLE | 50 | 2026-10-25 03:53:11.589816 | — | 6ad7bc35d717e27888aad3dc | — | — | — | US*NDO*Enev1159176*1 | 1750 | — | t | 0 | 1 | 0 | 0 | t | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4269 | 537 | 2026-10-20 19:08:38.477655 | 2026-10-25 03:53:11.583926 | 115917601 | AVAILABLE | 50 | 2026-10-25 03:53:11.58173 | — | 6ad7bc35d717e27888aad3e3 | — | — | — | US*NDO*Enev1159176*2 | 1750 | — | t | 0 | 0 | 1 | 0 | f | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4268 | 537 | 2026-10-20 19:08:11.376204 | 2026-10-25 05:22:43.62113 | 115917701 | AVAILABLE | 50 | 2026-10-25 05:22:43.618813 | — | 6ad7bc1ad717e27888aac23c | — | — | — | US*NDO*Enev1159177*2 | 1750 | — | t | 0 | 0 | 1 | 0 | f | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4267 | 537 | 2026-10-20 19:08:11.14919 | 2026-10-25 05:22:43.617898 | 115917700 | AVAILABLE | 50 | 2026-10-25 05:22:43.616092 | — | 6ad7bc1ad717e27888aac232 | — | — | — | US*NDO*Enev1159177*1 | 1750 | — | t | 0 | 1 | 0 | 0 | t | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4266 | 537 | 2026-10-20 19:07:39.949534 | 2026-10-25 04:36:42.899456 | 115917801 | AVAILABLE | 50 | 2026-10-25 04:36:42.897678 | — | 6ad7bbf9d717e27888aaab2b | — | — | — | US*NDO*Enev1159178*2 | 1750 | — | t | 0 | 0 | 1 | 0 | f | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |
| 4265 | 537 | 2026-10-20 19:07:39.188044 | 2026-10-25 04:36:42.572096 | 115917800 | AVAILABLE | 50 | 2026-10-25 04:36:42.570281 | — | 6ad7bbf9d717e27888aaab21 | — | — | — | US*NDO*Enev1159178*1 | 1750 | — | t | 0 | 1 | 0 | 0 | t | — | {REMOTE_START_STOP_CAPABLE,RFID_READER} |

### Plan de técnicas

| Técnica a aplicar | Resultado esperado (ideal) |
|---|---|
| Clustering (K-means) sobre las ubicaciones existentes | Arquetipos claros de ubicación (ej. “urbano de alta rotación” vs. “ruta de baja frecuencia”) que sirvan de referencia para evaluar un sitio nuevo. |
| ACP previo al clustering | Resumir las características de cada ubicación (conectores, potencia, tráfico) en pocos ejes antes de agruparlas. |
| Regresión lineal múltiple | Una estimación numérica (uso esperado, ingreso esperado) para un sitio candidato nuevo, en base a ubicaciones comparables. |

---
