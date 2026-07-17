# Quality Pass: Reporte ANTES vs DESPUÉS

Comparación de la batería de aceptación tras aplicar limpieza de datos, motor de afinidad por industria, modos de generación configurables y nuevos criterios de evaluación.

| Métrica | ANTES | DESPUÉS | Δ |
|---|---|---|---|
| Items por propuesta | 3.78 | 3.72 | -0.06 |
| Categorías limpias | 0.0% | 100.0% | +100.0% |
| Selection reasons limpias | 0.0% | 100.0% | +100.0% |
| Utilización presupuesto | 93.5% | 95.1% | +1.6% |
| Similitud máxima entre propuestas | 0.493 | 0.377 | -0.116 |
| Cobertura de categorías | 1.0 | 4.3 | 3.3 |
| Productos reutilizados | 6 | 6 | +0 |

## Detalle por caso

| Caso | Items/prop | Cat limpias | Razones limpias | Util % | Sim max | Modos |
|---|---|---|---|---|---|---|
| test_01_software | 4.0 | 100.0% | 100.0% | 96.8% | 0.518 | premium=1, eco=1, balanced=1 |
| test_02_arquitectura | 5.33 | 100.0% | 100.0% | 95.0% | 0.362 | premium=1, eco=1, balanced=1 |
| test_03_clinica | 4.67 | 100.0% | 100.0% | 91.4% | 0.490 | premium=1, balanced=1, eco=1 |
| test_04_eco | 3.0 | 100.0% | 100.0% | 97.8% | 0.313 | eco=1, balanced=1, premium=1 |
| test_05_vip | 3.33 | 100.0% | 100.0% | 96.0% | 0.310 | eco=1, premium=1, balanced=1 |
| test_06_presupuesto_bajo | 2.0 | 100.0% | 100.0% | 93.8% | 0.267 | balanced=1, premium=1, eco=1 |

## Observaciones

- ANTES = resultados del commit base `d41b1d8` (Vertical Slice 11 Global Generation).
- DESPUÉS = resultados tras el Quality Pass con catálogo re-indexado y sanitizado.
- 'Categorías limpias' mide que la categoría no contenga texto de menú de navegación, newsletter ni listas de categorías del sitio.
- 'Razones limpias' mide que `selection_reason` no contenga referencias, stock, logística ni textos largos.
- La reutilización controlada de productos entre propuestas del mismo set es aceptable cuando se justifica por diversidad de categorías y presupuesto.