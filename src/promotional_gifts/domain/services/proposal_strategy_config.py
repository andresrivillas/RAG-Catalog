from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional

from ..entities.commercial_intent import CommercialIntent
from ..entities.product_knowledge import ProductKnowledge
from .generation_mode import GenerationMode
from .product_selector import ScoredProduct


@dataclass
class StrategySpec:
    """Estrategia deliberadamente distinta para construir una propuesta.

    Cada estrategia reordena el pool compartido priorizando un angulo
    tematico (categorias, tags, materiales) y manteniendo el score final
    como desempate.
    """

    strategy_id: str
    label: str
    generation_mode: GenerationMode
    # Reordena el pool compartido segun el foco de la estrategia.
    rerank: Callable[
        [List[ScoredProduct], CommercialIntent, "BudgetPlan"],
        List[ScoredProduct],
    ]
    category_boost: List[str] = field(default_factory=list)
    tag_boost: List[str] = field(default_factory=list)
    material_boost: List[str] = field(default_factory=list)


# Forward reference de BudgetPlan para la firma de rerank.
from .budget_plan import BudgetPlan  # noqa: E402


def _score(sp: ScoredProduct) -> float:
    return sp.trace.final_score if sp.trace else sp.score


def _make_thematic_rerank(
    category_boost: List[str], tag_boost: List[str], material_boost: List[str]
) -> Callable[[List[ScoredProduct], CommercialIntent, BudgetPlan], List[ScoredProduct]]:
    """Devuelve una funcion de reranqueo que prioriza productos de ciertas
    categorias, tags y materiales, manteniendo el score comercial como
    desempate. Asi cada propuesta del set representa una estrategia distinta.
    """
    categories = {c.lower() for c in category_boost}
    tags = {t.lower() for t in tag_boost}
    materials = {m.lower() for m in material_boost}

    def rerank(pool, intent, plan):
        def thematic_score(sp: ScoredProduct) -> float:
            product = sp.product
            score = 0.0
            if (product.category or "").lower() in categories:
                score += 3.0
            product_tags = {t.lower() for t in (product.commercial_tags or [])}
            product_tags |= {t.lower() for t in (product.audience_tags or [])}
            product_tags |= {t.lower() for t in (product.occasion_tags or [])}
            tag_hits = len(product_tags & tags)
            score += tag_hits * 1.5
            product_materials = {
                m.lower()
                for m in (product.materials or "").replace(",", " ").replace(";", " ").split()
            }
            material_hits = len(product_materials & materials)
            score += material_hits * 1.0
            return score

        return sorted(
            pool,
            key=lambda sp: (thematic_score(sp), _score(sp), sp.product.price.amount),
            reverse=True,
        )

    return rerank


# ---------------------------------------------------------------------------
# Estrategias base tematicas
# ---------------------------------------------------------------------------
_STRATEGY_TECHNOLOGY = StrategySpec(
    "technology",
    "Tecnología",
    GenerationMode.BALANCED,
    _make_thematic_rerank(
        category_boost=["tecnologia", "escritura", "oficina"],
        tag_boost=["usb", "cargador", "gadget", "wireless", "auricular", "power bank", "tecnicos", "tecnologia"],
        material_boost=["metal", "aluminio", "silicona", "plastico"],
    ),
    category_boost=["tecnologia", "escritura", "oficina"],
    tag_boost=["usb", "cargador", "gadget", "wireless", "auricular", "power bank", "tecnicos", "tecnologia"],
    material_boost=["metal", "aluminio", "silicona", "plastico"],
)

_STRATEGY_EXECUTIVE = StrategySpec(
    "executive",
    "Ejecutiva",
    GenerationMode.PREMIUM,
    _make_thematic_rerank(
        category_boost=["oficina", "viaje", "escritura", "bolsos"],
        tag_boost=["premium", "ejecutivo", "corporativo", "alta gama", "personalizable", "libreta", "agenda"],
        material_boost=["cuero", "metal", "madera", "aluminio"],
    ),
    category_boost=["oficina", "viaje", "escritura", "bolsos"],
    tag_boost=["premium", "ejecutivo", "corporativo", "alta gama", "personalizable", "libreta", "agenda"],
    material_boost=["cuero", "metal", "madera", "aluminio"],
)

_STRATEGY_ECO = StrategySpec(
    "eco",
    "Eco",
    GenerationMode.ECO,
    _make_thematic_rerank(
        category_boost=["hogar", "oficina", "otros"],
        tag_boost=["eco", "ecologico", "sostenible", "rpet", "reciclado", "bambu"],
        material_boost=["bambu", "madera", "rpet", "reciclado", "algodon"],
    ),
    category_boost=["hogar", "oficina", "otros"],
    tag_boost=["eco", "ecologico", "sostenible", "rpet", "reciclado", "bambu"],
    material_boost=["bambu", "madera", "rpet", "reciclado", "algodon"],
)

_STRATEGY_WELLNESS = StrategySpec(
    "wellness",
    "Bienestar",
    GenerationMode.BALANCED,
    _make_thematic_rerank(
        category_boost=["hogar", "viaje", "oficina"],
        tag_boost=["bienestar", "salud", "hidratacion", "termo", "botella", "higiene"],
        material_boost=["acero", "bambu", "aluminio", "vidrio"],
    ),
    category_boost=["hogar", "viaje", "oficina"],
    tag_boost=["bienestar", "salud", "hidratacion", "termo", "botella", "higiene"],
    material_boost=["acero", "bambu", "aluminio", "vidrio"],
)

_STRATEGY_EVENT = StrategySpec(
    "event",
    "Evento / Branding",
    GenerationMode.BALANCED,
    _make_thematic_rerank(
        category_boost=["otros", "bolsos", "oficina", "escritura"],
        tag_boost=["evento", "merchandising", "branding", "logo", "welcome", "bolsa"],
        material_boost=["plastico", "carton", "algodon", "metal"],
    ),
    category_boost=["otros", "bolsos", "oficina", "escritura"],
    tag_boost=["evento", "merchandising", "branding", "logo", "welcome", "bolsa"],
    material_boost=["plastico", "carton", "algodon", "metal"],
)

_STRATEGY_DESIGN = StrategySpec(
    "design",
    "Diseño",
    GenerationMode.BALANCED,
    _make_thematic_rerank(
        category_boost=["oficina", "escritura", "tecnologia"],
        tag_boost=["diseno", "diseño", "planos", "croquis", "maqueta", "personalizable", "madera", "bambu"],
        material_boost=["madera", "bambu", "metal", "carton"],
    ),
    category_boost=["oficina", "escritura", "tecnologia"],
    tag_boost=["diseno", "diseño", "planos", "croquis", "maqueta", "personalizable", "madera", "bambu"],
    material_boost=["madera", "bambu", "metal", "carton"],
)

_STRATEGY_SAFETY = StrategySpec(
    "safety",
    "Seguridad / Obra",
    GenerationMode.BALANCED,
    _make_thematic_rerank(
        category_boost=["oficina", "viaje", "tecnologia", "hogar"],
        tag_boost=["seguridad", "herramienta", "durabilidad", "utilidad", "casco", "obra"],
        material_boost=["metal", "aluminio", "acero", "plastico"],
    ),
    category_boost=["oficina", "viaje", "tecnologia", "hogar"],
    tag_boost=["seguridad", "herramienta", "durabilidad", "utilidad", "casco", "obra"],
    material_boost=["metal", "aluminio", "acero", "plastico"],
)

_STRATEGY_STATIONERY = StrategySpec(
    "stationery",
    "Escritura / Escolar",
    GenerationMode.BALANCED,
    _make_thematic_rerank(
        category_boost=["oficina", "escritura", "bolsos"],
        tag_boost=["cuaderno", "libreta", "estudiante", "escuela", "boligrafo", "lapices", "lápices"],
        material_boost=["papel", "carton", "plastico", "metal"],
    ),
    category_boost=["oficina", "escritura", "bolsos"],
    tag_boost=["cuaderno", "libreta", "estudiante", "escuela", "boligrafo", "lapices", "lápices"],
    material_boost=["papel", "carton", "plastico", "metal"],
)

_STRATEGY_MERCHANDISING = StrategySpec(
    "merchandising",
    "Merchandising",
    GenerationMode.BUDGET,
    _make_thematic_rerank(
        category_boost=["otros", "bolsos", "oficina"],
        tag_boost=["merchandising", "logo", "branding", "welcome", "bolsa", "mochila"],
        material_boost=["plastico", "carton", "algodon", "metal"],
    ),
    category_boost=["otros", "bolsos", "oficina"],
    tag_boost=["merchandising", "logo", "branding", "welcome", "bolsa", "mochila"],
    material_boost=["plastico", "carton", "algodon", "metal"],
)

_STRATEGY_WELCOME = StrategySpec(
    "welcome",
    "Bienvenida",
    GenerationMode.BALANCED,
    _make_thematic_rerank(
        category_boost=["hogar", "viaje", "otros"],
        tag_boost=["hotel", "bienvenida", "amenities", "kit", "viaje", "maleta"],
        material_boost=["algodon", "plastico", "vidrio", "metal"],
    ),
    category_boost=["hogar", "viaje", "otros"],
    tag_boost=["hotel", "bienvenida", "amenities", "kit", "viaje", "maleta"],
    material_boost=["algodon", "plastico", "vidrio", "metal"],
)


def _rerank_completeness(pool, intent, plan):
    # Estrategia generica de respaldo: maximiza score comercial por peso,
    # favoreciendo productos que dejan espacio para completar el kit.
    def value(sp: ScoredProduct) -> float:
        price = sp.product.price.amount or 1.0
        room = max(0.0, (plan.per_unit_ceiling or price) - price)
        return (_score(sp) * 1.0) / price + room / 10000.0

    return sorted(pool, key=value, reverse=True)


_STRATEGY_COMPLETENESS = StrategySpec(
    "completeness",
    "Completitud de kit",
    GenerationMode.BALANCED,
    _rerank_completeness,
)


BASE_STRATEGIES: List[StrategySpec] = [
    _STRATEGY_EXECUTIVE,
    _STRATEGY_TECHNOLOGY,
    _STRATEGY_ECO,
]


# ---------------------------------------------------------------------------
# Mapeo por industria a tres estrategias distintas.
# ---------------------------------------------------------------------------
INDUSTRY_STRATEGIES: Dict[str, List[StrategySpec]] = {
    "software": [_STRATEGY_TECHNOLOGY, _STRATEGY_EXECUTIVE, _STRATEGY_ECO],
    "tecnologia": [_STRATEGY_TECHNOLOGY, _STRATEGY_EXECUTIVE, _STRATEGY_ECO],
    "arquitectura": [_STRATEGY_ECO, _STRATEGY_EXECUTIVE, _STRATEGY_DESIGN],
    "construccion": [_STRATEGY_SAFETY, _STRATEGY_EXECUTIVE, _STRATEGY_ECO],
    "ingenieria": [_STRATEGY_TECHNOLOGY, _STRATEGY_EXECUTIVE, _STRATEGY_ECO],
    "salud": [_STRATEGY_WELLNESS, _STRATEGY_EXECUTIVE, _STRATEGY_ECO],
    "hospital": [_STRATEGY_WELLNESS, _STRATEGY_EXECUTIVE, _STRATEGY_ECO],
    "clinica": [_STRATEGY_WELLNESS, _STRATEGY_EXECUTIVE, _STRATEGY_ECO],
    "educacion": [_STRATEGY_STATIONERY, _STRATEGY_MERCHANDISING, _STRATEGY_EXECUTIVE],
    "universidad": [_STRATEGY_STATIONERY, _STRATEGY_MERCHANDISING, _STRATEGY_EXECUTIVE],
    "colegio": [_STRATEGY_STATIONERY, _STRATEGY_MERCHANDISING, _STRATEGY_EXECUTIVE],
    "finanzas": [_STRATEGY_EXECUTIVE, _STRATEGY_TECHNOLOGY, _STRATEGY_ECO],
    "financiera": [_STRATEGY_EXECUTIVE, _STRATEGY_TECHNOLOGY, _STRATEGY_ECO],
    "hoteleria": [_STRATEGY_WELCOME, _STRATEGY_EXECUTIVE, _STRATEGY_ECO],
    "vip": [_STRATEGY_EXECUTIVE, _STRATEGY_TECHNOLOGY, _STRATEGY_ECO],
    "eventos": [_STRATEGY_EVENT, _STRATEGY_EXECUTIVE, _STRATEGY_ECO],
}


def strategies_for(
    industry: Optional[str],
    num_proposals: int = 3,
    mode: Optional[GenerationMode] = None,
) -> List[StrategySpec]:
    """Devuelve hasta `num_proposals` estrategias distintas para la industria.

    Si no hay mapeo especifico, selecciona un set de respaldo segun el modo.
    """
    if industry:
        specs = INDUSTRY_STRATEGIES.get(industry.lower())
        if specs:
            return specs[:num_proposals]

    mode = mode or GenerationMode.BALANCED
    if mode == GenerationMode.ECO:
        fallback = [_STRATEGY_ECO, _STRATEGY_EXECUTIVE, _STRATEGY_TECHNOLOGY]
    elif mode == GenerationMode.PREMIUM:
        fallback = [_STRATEGY_EXECUTIVE, _STRATEGY_TECHNOLOGY, _STRATEGY_ECO]
    elif mode == GenerationMode.BUDGET:
        fallback = [_STRATEGY_TECHNOLOGY, _STRATEGY_ECO, _STRATEGY_EXECUTIVE]
    else:
        fallback = BASE_STRATEGIES

    return fallback[:num_proposals]
