# Promotional Gifts AI

Asistente de inteligencia comercial para regalos empresariales. Construye
propuestas de regalos promocionales a partir de un catálogo, usando RAG
semántico (ChromaDB + embeddings locales) y un Business Engine determinístico.

## Arquitectura

Clean Architecture (domain / application / infrastructure / interfaces).
El RAG recupera conocimiento; el Business Engine decide; el lenguaje (Ollama,
futuro) solo redacta.

## Estado actual (Vertical Slices 1 y 2)

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

No se usan aún: Streamlit, scraping ni multi-proveedor. Requiere Ollama
corriendo localmente con el modelo configurado (por defecto `llama3.2`).

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

### 2. Buscar productos (Slice 1)

```bash
PYTHONPATH=src:. python3 scripts/query_catalog.py
```

### 3. Generar propuestas (Slices 2 y 3)

```bash
PYTHONPATH=src:. python3 scripts/generate_proposal.py
```

Ejemplo de solicitud:

```
Necesito 3800 regalos de cumpleaños con un presupuesto máximo de 25000 COP por unidad
```

## Estructura

```
config/            # settings (rutas, modelo, top_k)
data/              # catalog.xlsx y persistencia ChromaDB
src/promotional_gifts/
  domain/          # entities, value_objects, ports, services (sin frameworks)
  application/     # intent_analyzer, use_cases
  knowledge/       # transform (cleaner, metadata, embedding) y store (indexer)
  infrastructure/  # adapters: excel, embeddings, chroma
  container.py     # Composition Root
scripts/           # index_catalog.py, query_catalog.py, generate_proposal.py
```
