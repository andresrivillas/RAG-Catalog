# Promotional Gifts AI

Asistente de inteligencia comercial para regalos empresariales. Recibe la
necesidad de un cliente, analiza intención, presupuesto, industria y ocasión,
y genera varias propuestas de regalos promocionales a partir de un catálogo
local.

El sistema usa RAG semántico (ChromaDB + embeddings locales) para recuperar
productos, pero **las decisiones comerciales son 100% deterministas**: un
Business Engine basado en reglas selecciona, evalúa, diversifica y ajusta
propuestas. Ollama (u otro LLM compatible) solo se invoca **una vez por
generación** para redactar la descripción comercial de cada propuesta.

## Propósito

Automatizar el primer borrador de propuestas de regalos corporativos sin
depender de la experiencia individual del vendedor. El objetivo es reducir el
tiempo de preparación de una propuesta, mejorar el aprovechamiento del
presupuesto del cliente y aumentar la coherencia entre el mensaje de marca,
la industria y los productos recomendados.

## Funcionalidades principales

- **Análisis de intención comercial**: extrae cantidad, presupuesto (total o
  por unidad), ocasión, público objetivo, industria, preferencias de materiales,
  categorías y restricciones (eco, personalizable, sin plástico, etc.).
- **RAG semántico local**: recupera productos relevantes del catálogo usando
  ChromaDB y el modelo de embeddings `all-MiniLM-L6-v2`.
- **Motor comercial determinista**: evalúa afinidad por industria, ocasión,
  público, presupuesto, utilidad, coherencia de kit y valor percibido; no usa
  LLM para decidir.
- **Set global de propuestas**: cada solicitud genera un `ProposalSet` con
  varias propuestas deliberadamente diferentes (por ejemplo, tecnología,
  ejecutiva, eco). El LLM recibe todo el set en una sola llamada.
- **Persistencia de un solo JSON**: cada generación se guarda como un único
  documento JSON con la consulta original, el intent y el `ProposalSet`
  completo.
- **Refinamiento de propuestas**: permite modificar una propuesta existente
  (reemplazar, agregar, eliminar productos, cambiar presupuesto, hacerla más
  premium, eco, etc.) sin regenerar desde cero, guardando versiones.
- **Evaluación multicriterio**: cada propuesta recibe una `ProposalScoreCard`
  con múltiples criterios (presupuesto, coherencia, diversidad, valor comercial,
  ajuste a industria, ocasión, público, etc.) y observaciones explicativas.
- **Interfaz web con Streamlit**: generación, comparación, refinamiento,
  historial de propuestas guardadas y versionado desde el navegador.
- **Batería de aceptación**: casos representativos (software, arquitectura,
  clínica, eco, VIP, presupuesto bajo) que se ejecutan y se guardan en
  `tests/results/` para análisis de calidad.

## Arquitectura

Clean Architecture con cuatro capas:

- **domain**: entidades, value objects, puertos y servicios del Business Engine.
- **application**: casos de uso, análisis de intención, refinamiento, prompts y
  orquestación.
- **knowledge**: limpieza, enriquecimiento, metadata, embeddings e indexación.
- **infrastructure**: adapters concretos (Excel, ChromaDB, Ollama, archivos).
- **interfaces**: aplicación Streamlit y scripts de consola.

El Composition Root está en `src/promotional_gifts/container.py`.

## Flujo de generación

1. **Intención**: `IntentAnalyzer` interpreta la consulta en lenguaje natural.
2. **Recuperación**: ChromaDB busca productos candidatos usando el embedding
   generado a partir de campos comercialmente útiles (nombre, categoría,
   beneficios, materiales, tags, etc.).
3. **Selección**: `ProductSelector` puntúa cada candidato con afinidad de
   industria, ajuste a ocasión, valor comercial y aprovechamiento de
   presupuesto.
4. **Construcción del set**: `ProposalBuilder` crea propuestas con estrategias
   temáticas distintas, usando un pool de productos compartido y una blacklist
   dinámica.
5. **Diversidad**: `DiversityEngine` mide la similitud entre propuestas y, si
   es necesario, reconstruye la peor propuesta para garantizar variedad real.
6. **Evaluación**: `ProposalEvaluationEngine` califica cada propuesta y el set
   completo.
7. **Redacción**: `CommercialWriter` llama una sola vez al LLM con todo el set
   y distribuye la descripción comercial de cada propuesta.
8. **Persistencia**: el `ProposalSet` se guarda como un único JSON.

## Requisitos

- Python 3.9+
- Dependencias: `pandas`, `openpyxl`, `chromadb`, `sentence-transformers`,
  `pydantic-settings`, `streamlit`, `requests`, `beautifulsoup4`

## Instalación

```bash
python3 -m pip install -r requirements.txt
```

## Uso

### 1. Servidor Ollama

```bash
ollama pull llama3.2
ollama serve   # si no está activo
```

### 2. Indexar el catálogo

Coloca el Excel en `data/catalog/catalog.xlsx` y ejecuta:

```bash
PYTHONPATH=src:. python3 scripts/index_catalog.py
```

El flujo es: Excel → limpieza → enriquecimiento web (scraping de cada URL de
producto, con fallback al Excel si la página falla) → metadata derivada →
embeddings → ChromaDB. El resultado enriquecido se guarda en
`data/enriched/enriched_catalog.json`. En ejecuciones siguientes, si ese
archivo existe, se carga directamente para evitar re-scraping.

### 3. Interfaz web Streamlit

```bash
python3 scripts/run_app.py
```

Abre la URL que muestra Streamlit (por defecto http://localhost:8501).
La barra lateral permite ajustar modelo Ollama, Top K y modo de generación.
Si el catálogo no está indexado u Ollama no está disponible, la app muestra
un mensaje claro con instrucciones (sin traceback).

### 4. Generar propuestas por consola

```bash
PYTHONPATH=src:. python3 scripts/generate_proposal.py
```

Ejemplo de solicitud:

```
Necesito 3800 regalos de cumpleaños con un presupuesto máximo de 25000 COP por unidad
```

### 5. Refinar propuestas

En la app de Streamlit, bajo cada propuesta aparece un cuadro de texto
"Refinar propuesta" con un botón "Aplicar refinamiento". Cada refinamiento
guarda una nueva versión (`v1 → v2 → v3`) sin sobrescribir la anterior.

Instrucciones soportadas (reglas deterministas, sin LLM):

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

### 6. Evaluar calidad objetiva

```bash
PYTHONPATH=src:. python3 scripts/evaluate.py
```

No requiere Ollama. Requiere el catálogo indexado completo.

### 7. Ejecutar la batería de aceptación

```bash
PYTHONPATH=src:. python3 tests/run_acceptance_battery.py
```

Genera un JSON por caso en `tests/results/` con la consulta original, la fecha
y el `ProposalSet` completo. Si un caso falla, guarda el error y el diagnóstico
en el mismo archivo.

### 8. Ejecutar tests unitarios

```bash
python3 tests/test_intent_analyzer.py
python3 tests/test_engine_improvements.py
python3 tests/test_industry_reasoning.py
python3 tests/test_global_generation.py
python3 tests/test_scraper_cleaning.py
```

## Estructura del proyecto

```
config/            # settings (rutas, modelo, top_k, evaluation_weights, proposals_dir)
data/              # catalog.xlsx, persistencia ChromaDB y proposals/ (JSON)
scripts/           # index_catalog.py, query_catalog.py, generate_proposal.py,
                   # run_app.py, evaluate.py
tests/             # tests unitarios y batería de aceptación (results/)
src/promotional_gifts/
  domain/          # entities, value_objects, ports, services (Business Engine)
  application/     # casos de uso, análisis de intención, refinamiento, prompts
  knowledge/       # transform (cleaner, metadata, embedding) y store (indexer)
  infrastructure/  # adapters: excel, embeddings, chroma, ollama, persistence
  container.py     # Composition Root
  interfaces/      # Streamlit y scripts de consola
```

## Principios del diseño

- **El LLM nunca decide**: solo redacta descripciones y explicaciones.
- **Inteligencia comercial en reglas**: industria, ocasión, público, presupuesto,
  utilidad y coherencia se puntúan de forma determinista.
- **Una sola llamada al LLM por generación**: todo el `ProposalSet` se envía en
  un único contexto y se devuelve un solo documento JSON.
- **Datos limpios**: el scraper descarta texto de UI, inventario, logística y
  HTML antes de llegar al motor.
- **Configurable por industria**: afinidad, categorías preferidas, materiales y
  blacklist comercial se definen en perfiles de industria.
- **Compatible y versionado**: refinamientos, workspace y Streamlit mantienen
  versiones sin romper el modelo de dominio.
