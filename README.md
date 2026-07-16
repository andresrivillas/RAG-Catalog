# Promotional Gifts AI

Asistente de inteligencia comercial para regalos empresariales. Construye
propuestas de regalos promocionales a partir de un catálogo, usando RAG
semántico (ChromaDB + embeddings locales) y un Business Engine determinístico.

## Arquitectura

Clean Architecture (domain / application / infrastructure / interfaces).
El RAG recupera conocimiento; el Business Engine decide; el lenguaje (Ollama,
futuro) solo redacta.

## Estado actual (Vertical Slices 1 a 9)

- **Slice 1**: lectura de Excel, limpieza, embeddings (`all-MiniLM-L6-v2`),
  indexación en ChromaDB y búsqueda semántica por consola.
- **Slice 2**: `CommercialIntent` + `IntentAnalyzer` (reglas/diccionarios),
  `BudgetOptimizer`, `ProductSelector`, `PricingEngine`, `ProposalBuilder`,
  `ProposalRanker` y `CommercialProposal`. Generación de propuestas
  estructuradas por consola.
- **Slice 3**: integración de Ollama (solo redacción). `LLMPort` + `OllamaLLM`,
  `PromptLoader`, `PromptContextBuilder`, `CommercialWriter` y el prompt
  `prompts/commercial/proposal_writer.txt`. El LLM solo redacta la
  `commercial_description`; el Business Engine sigue decidiendo todo.
- **Slice 4**: interfaz Streamlit (`interfaces/web/streamlit_app.py`) con
  manejo de errores (catálogo no indexado / Ollama caído).
- **Slice 5**: `KitBuilder`, `RoleClassifier`, `CompatibilityChecker`,
  `PerceivedValueEstimator` y `selection_reason`/`role` por producto.
- **Slice 6**: Knowledge Enrichment Pipeline (scraping + merge) y
  `MetadataBuilder` con `occasion`/`audience`/`commercial` tags.
- **Slice 7**: retrieval híbrido (`OccasionMatcher`, `CommercialScorer`,
  `NegativeFilter`), robustez de precios, `DecisionTrace` y módulo de
  evaluación objetiva (`scripts/evaluate.py`).
- **Slice 8**: refinamiento de propuestas (`RefinementAnalyzer`,
  `ProposalRefinementEngine`, `RefineProposalUseCase`) con versionado
  (`proposal_id`/`version`/`parent_version`) y bitácora.
- **Slice 9**: `ProposalEvaluationEngine` + `ProposalScoreCard` con 13
  criterios multicriterio ponderados y modo debug.

Requiere Ollama corriendo localmente con el modelo configurado
(por defecto `llama3.2`).

## Requisitos

- Python 3.9+
- Dependencias: `pandas`, `openpyxl`, `chromadb`, `sentence-transformers`,
  `pydantic-settings`

## Instalación

```bash
python3 -m pip install pandas openpyxl chromadb sentence-transformers pydantic-settings
```

## Uso

### 0. Servidor Ollama (Slice 3)

```bash
ollama pull llama3.2
ollama serve   # si no está activo
```

### 1. Indexar el catálogo

Coloca el Excel en `data/catalog/catalog.xlsx` y ejecuta:

```bash
PYTHONPATH=src:. python3 scripts/index_catalog.py
```

El flujo es: Excel → limpieza → enriquecimiento web (scraping de la URL de
cada producto, con fallback al Excel si la página falla) → metadata derivada →
embeddings → ChromaDB. El resultado enriquecido se guarda en
`data/enriched/enriched_catalog.json`. En ejecuciones siguientes, si ese archivo
existe, se carga directamente para evitar re-scraping.

### 2. Buscar productos (Slice 1)

```bash
PYTHONPATH=src:. python3 scripts/query_catalog.py
```

### 3. Generar propuestas por consola (Slices 2 y 3)

```bash
PYTHONPATH=src:. python3 scripts/generate_proposal.py
```

Ejemplo de solicitud:

```
Necesito 3800 regalos de cumpleaños con un presupuesto máximo de 25000 COP por unidad
```

### 4. Interfaz gráfica Streamlit (Slice 4)

```bash
python3 scripts/run_app.py
```

Abre la URL que muestra Streamlit (por defecto http://localhost:8501).
La barra lateral permite ajustar modelo Ollama, Top K y modo de generación.
Si el catálogo no está indexado u Ollama no está disponible, la app muestra
un mensaje claro con instrucciones (sin traceback).

### 5. Evaluación de calidad (Slice 7)

```bash
PYTHONPATH=src:. python3 scripts/evaluate.py
```

Ejecuta casos de prueba definidos en
`src/promotional_gifts/application/evaluation/proposal_evaluator.py` y mide
objetivamente la calidad de las propuestas (categorías esperadas, prohibidas,
presupuesto). No requiere Ollama. Requiere el catálogo indexado completo para
cubrir todas las categorías.

### 6. Refinamiento de propuestas (Slice 8)

El asistente actúa como asesor comercial: el usuario refina una propuesta
existente sin volver a generarla desde cero. En la app de Streamlit, bajo cada
propuesta aparece un cuadro de texto "Refinar propuesta" con un botón
"Aplicar refinamiento".

```bash
python3 scripts/run_app.py
```

Instrucciones soportadas (reglas determinísticas, sin LLM):

- `Cambia el mug por un termo` → reemplaza un producto.
- `Cambia el mug` → reemplaza por la mejor alternativa.
- `Agrega una agenda` / `Pon un termo` → agrega un producto.
- `Quítale la regla` → elimina un producto.
- `Hazla más premium` / `Hazla más elegante` → mejora el valor percibido.
- `Hazla más barata` → reduce el costo.
- `Hazla eco` → restringe a productos ecológicos.
- `No quiero plástico` → excluye un material.
- `Quiero que sea de madera` → prioriza un material.
- `Cambia el presupuesto a 18000` → ajusta el tope por unidad.
- `Renueva el empaque` → añade presentación/empaque.

Cada propuesta lleva `proposal_id`, `version` y `parent_version`. El motor
modifica solo lo necesario (recalcula costos, score y `decision_trace`) y Ollama
solo redacta la descripción explicando los cambios.

### 7. Proposal Evaluation Engine (Slice 9)

`ProposalRanker` ya no usa una fórmula única. Solicita un `ProposalScoreCard`
al `ProposalEvaluationEngine`, que evalúa cada propuesta en 13 dimensiones
independientes y combina sus aportes con pesos configurables.

```python
from promotional_gifts.domain.services.evaluation.proposal_evaluation_engine import (
    ProposalEvaluationEngine, EvaluationWeights,
)
engine = ProposalEvaluationEngine(weights=EvaluationWeights(settings.evaluation_weights))
card = engine.evaluate(proposal, intent, plan)
print(card.overall_score, card.observations)
```

Criterios (cada uno con puntuación y razonamiento determinista): Budget
Efficiency, Commercial Value, Kit Coherence, Product Diversity, Category
Diversity, Practical Utility, Brand Visibility, Premium Perception,
Sustainability, Personalization Potential, Occasion Fit, Audience Fit y
Proposal Balance.

Pesos en `config/settings.py` (`evaluation_weights`) y modo debug
(`evaluation_debug: true`) que registra el `ProposalScoreCard` completo vía
`logging`. El diseño deja una interfaz limpia para un futuro `AIJudge` (no
implementado en el MVP; solo reglas).

### 8. Proposal Workspace (Slice 10)

Las propuestas dejan de vivir solo en memoria y se persisten como documentos
JSON en `data/proposals/`. Cada propuesta generada se guarda automáticamente.

- `ProposalRepositoryPort` / `FileProposalRepository`: persistencia JSON.
- `ProposalDocument`: agregado serializable con `proposal_id`, `version`,
  `created_at`, `updated_at`, `original_query`, `client`, `intent`,
  `proposal`, `score_card`, `refinement_history`.
- `ProposalWorkspace`: guardar, abrir, actualizar, eliminar, duplicar, listar,
  y buscar por texto / cliente / ocasión / productos / fecha (búsqueda
  estructurada, sin embeddings).
- `VersionComparator`: compara versiones (productos agregados/eliminados,
  cambio de presupuesto, score y descripción); sin LLM.

En Streamlit, la barra lateral "Propuestas guardadas" lista las propuestas,
permite abrirlas (solo carga el JSON, sin Chroma ni Business Engine), navegar
entre versiones y compararlas. Al refinar, se guarda una nueva versión
(`v1 → v2 → v3`) sin sobrescribir.

El modelo `ProposalDocument` está diseñado para exportarse luego a PDF / Word /
Excel sin acoplarse a la lógica comercial.

## Estructura

```
config/            # settings (rutas, modelo, top_k, evaluation_weights, proposals_dir)
data/              # catalog.xlsx, persistencia ChromaDB y proposals/ (JSON)
src/promotional_gifts/
  domain/          # entities, value_objects, ports, services (sin frameworks)
    services/evaluation/  # proposal_evaluation_engine, criteria, proposal_score_card
    services/workspace/   # proposal_workspace, version_comparator, serializer
    entities/proposal_document.py  # ProposalDocument + RefinementRecord
    ports/proposal_repository_port.py
  application/     # intent_analyzer, use_cases
  knowledge/       # transform (cleaner, metadata, embedding) y store (indexer)
  infrastructure/  # adapters: excel, embeddings, chroma, persistence
  container.py     # Composition Root
 scripts/           # index_catalog.py, query_catalog.py, generate_proposal.py, run_app.py, evaluate.py
```
