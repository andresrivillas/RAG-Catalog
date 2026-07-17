import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import streamlit as st

from config.settings import settings
from smart_catalog.presentation.smart_catalog_page import render_smart_catalog
from promotional_gifts.container import (
    build_generate_proposal_use_case,
    build_refine_proposal_use_case,
    build_proposal_workspace,
    is_catalog_indexed,
    is_ollama_available,
)
from promotional_gifts.application.intent_analyzer import IntentAnalyzer
from promotional_gifts.domain.services.workspace.version_comparator import (
    VersionComparator,
)
from promotional_gifts.domain.entities.commercial_intent import CommercialIntent

MODES = ["balanced", "premium", "budget", "eco"]

PRIMARY = "#4F46E5"
SUCCESS = "#059669"
WARNING = "#D97706"
DANGER = "#DC2626"
NEUTRAL = "#6B7280"


def inject_styles():
    st.markdown(
        """
<style>
html, body, .stApp, [data-testid="stAppViewContainer"],
[data-testid="stHeader"], [data-testid="stToolbar"],
section[data-testid="stSidebar"] .stSidebarContent {
    font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
    background: #F3F4F6;
}
section[data-testid="stSidebar"] .stSidebarContent {
    background: #FFFFFF;
}
.main > div {
    background: #F3F4F6;
}

/* Card */
.pg-card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    border: 1px solid #F3F4F6;
}

/* Product card */
.pg-product {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    transition: box-shadow 0.15s ease;
}
.pg-product:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

/* Product image placeholder */
.pg-img-placeholder {
    width: 100px; height: 100px;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #9CA3AF;
    font-size: 11px;
    background: #F9FAFB;
}

/* Product name */
.pg-name {
    font-weight: 600;
    font-size: 15px;
    color: #111827;
    line-height: 1.3;
    text-decoration: none;
}
.pg-name:hover { color: #4F46E5; }

/* Metadata text */
.pg-meta {
    color: #6B7280;
    font-size: 12px;
    line-height: 1.4;
}

/* Price */
.pg-price {
    font-weight: 700;
    font-size: 14px;
    color: #111827;
}

/* Badge / chip */
.pg-badge {
    display: inline-block;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 999px;
    margin: 2px 4px 2px 0;
    white-space: nowrap;
}
.pg-b-eco { background: #ECFDF5; color: #059669; }
.pg-b-premium { background: #FFFBEB; color: #D97706; }
.pg-b-pers { background: #EEF2FF; color: #4F46E5; }
.pg-b-pack { background: #F3F4F6; color: #374151; }
.pg-b-corp { background: #F3F4F6; color: #374151; }

/* Selection reason */
.pg-reason {
    font-size: 12px;
    color: #374151;
    margin-top: 6px;
    line-height: 1.4;
}

/* Link */
.pg-link {
    color: #4F46E5;
    text-decoration: none;
    font-weight: 500;
    font-size: 12px;
}
.pg-link:hover { text-decoration: underline; }

/* Section title */
.pg-section-title {
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #9CA3AF;
    margin-bottom: 12px;
}

/* Score pill */
.pg-score-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

/* Score ring */
.pg-score-ring {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 52px;
    height: 52px;
    border-radius: 50%;
    font-weight: 700;
    font-size: 18px;
    flex-shrink: 0;
}

/* Budget utilization colors */
.pg-util-good { color: #059669; font-weight: 700; }
.pg-util-warn { color: #D97706; font-weight: 700; }
.pg-util-bad { color: #DC2626; font-weight: 700; }

/* Mode chip */
.pg-mode-chip {
    display: inline-block;
    font-size: 12px;
    font-weight: 600;
    padding: 3px 12px;
    border-radius: 999px;
    background: #F3F4F6;
    color: #374151;
}

/* Criterion group header */
.pg-criterion-group {
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: #9CA3AF;
    margin: 16px 0 8px 0;
}

/* Responsive image in product card */
.pg-product-img img {
    border-radius: 8px;
    max-width: 100%;
    height: auto;
}

/* Metric label in proposal header */
.pg-hdr-label {
    font-size: 11px;
    color: #9CA3AF;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}
.pg-hdr-value {
    font-size: 15px;
    font-weight: 700;
    color: #111827;
}

/* Warnings container */
.pg-warning {
    font-size: 12px;
    color: #DC2626;
    padding: 4px 0;
}

/* Product image */
.pg-product-img {
    border-radius: 8px;
    max-width: 100%;
    height: auto;
}

</style>
""",
        unsafe_allow_html=True,
    )


def render_module_selector():
    col1, col2 = st.columns([1, 1], gap="small")
    with col1:
        re_active = st.session_state.get("active_module", "RE") == "RE"
        if st.button(
            "Recommendation Engine",
            use_container_width=True,
            type="primary" if re_active else "secondary",
        ):
            st.session_state.active_module = "RE"
    with col2:
        sc_active = st.session_state.get("active_module") == "SC"
        if st.button(
            "Smart Catalog",
            use_container_width=True,
            type="primary" if sc_active else "secondary",
        ):
            st.session_state.active_module = "SC"
    return st.session_state.get("active_module", "RE")


st.set_page_config(page_title="Promotional Gifts AI", layout="wide")
inject_styles()

active_module = render_module_selector()

if active_module == "SC":
    render_smart_catalog()
    st.stop()

st.markdown(
    "<div style='margin-bottom:4px;font-size:28px;font-weight:700;color:#111827;'>"
    "Promotional Gifts AI</div>",
    unsafe_allow_html=True,
)
st.markdown(
    "<div style='color:#6B7280;font-size:14px;margin-bottom:24px;'>"
    "Copiloto comercial para propuestas de regalos promocionales</div>",
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_image_map():
    import json

    path = settings.enriched_path
    mapping = {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        for item in data:
            ref = item.get("reference")
            if not ref:
                continue
            thumb = item.get("thumbnail_url") or item.get("image_url")
            if not thumb:
                imgs = item.get("images") or []
                if imgs:
                    thumb = imgs[0]
            if thumb:
                mapping[ref] = thumb
            detail = item.get("detail_url") or item.get("url")
            if detail:
                mapping["__url__" + ref] = detail
    except Exception:
        pass
    return mapping


def score_band(score: float):
    if score >= 90:
        return "Excelente", SUCCESS
    if score >= 80:
        return "Muy buena", SUCCESS
    if score >= 70:
        return "Buena", WARNING
    if score >= 60:
        return "Aceptable", WARNING
    return "Baja", DANGER


def util_color(pct):
    if pct is None:
        return NEUTRAL
    if pct >= 80:
        return SUCCESS
    if pct >= 60:
        return WARNING
    return DANGER


def score_color(val):
    if val >= 80:
        return SUCCESS
    if val >= 60:
        return WARNING
    return DANGER


def compact_number(value: float) -> str:
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    if value >= 1_000:
        return f"{value/1_000:.0f}K"
    return f"{value:.0f}"


def get_intent_for(proposal, doc):
    if doc is not None:
        return doc.intent
    return st.session_state.get("last_intent")


def render_budget(intent: CommercialIntent, proposal):
    quantity = intent.quantity or proposal.units
    max_total = None
    if intent.budget_per_unit:
        max_total = intent.budget_per_unit * quantity
    elif intent.budget_total:
        max_total = intent.budget_total

    cols = st.columns(4)
    with cols[0]:
        st.markdown("<div class='pg-hdr-label'>Presupuesto m&aacute;ximo</div>", unsafe_allow_html=True)
        st.markdown(
            f"<div class='pg-hdr-value'>{f'{max_total:,.0f} COP' if max_total else '—'}</div>",
            unsafe_allow_html=True,
        )
    with cols[1]:
        st.markdown("<div class='pg-hdr-label'>Costo total</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='pg-hdr-value'>{proposal.total_cost}</div>", unsafe_allow_html=True)
    if max_total:
        used = proposal.total_cost.amount / max_total * 100
        ahorro = max_total - proposal.total_cost.amount
        col_c = util_color(used)
        with cols[2]:
            st.markdown("<div class='pg-hdr-label'>Utilizado</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div style='font-weight:700;font-size:15px;color:{col_c};'>{used:.0f} %</div>",
                unsafe_allow_html=True,
            )
        with cols[3]:
            st.markdown("<div class='pg-hdr-label'>Ahorro</div>", unsafe_allow_html=True)
            st.markdown(
                f"<div class='pg-hdr-value'>{ahorro:,.0f} COP</div>",
                unsafe_allow_html=True,
            )
    else:
        for i in range(2, 4):
            with cols[i]:
                st.markdown("<div class='pg-hdr-label'>—</div>", unsafe_allow_html=True)
                st.markdown("<div class='pg-hdr-value'>—</div>", unsafe_allow_html=True)


def build_recommendation_bullets(proposal, intent, util_pct):
    bullets = []
    if util_pct is not None:
        bullets.append(
            f"Aprovecha el {util_pct:.0f}% del presupuesto disponible."
        )
    if proposal.score_card:
        extras = [
            o for o in proposal.score_card.observations
            if "presupuesto" not in o.lower()
            and not o.lower().startswith("debilidad")
        ]
        for o in extras[:2]:
            bullets.append(o)
    roles = {it.role for it in proposal.items if it.role}
    if len(proposal.items) >= 2 and (
        "CORE" in roles or "UTILITY" in roles
    ):
        bullets.append("Combina productos complementarios en un solo kit.")
    if any(it.perceived_value_level == "alto" for it in proposal.items):
        bullets.append("Incluye productos de alto valor percibido.")
    if intent and intent.occasion:
        bullets.append(
            f"Adecuada para campañas de {intent.occasion}."
        )
    if not bullets:
        bullets.append("Cumple con los requisitos del cliente.")
    return bullets[:4]


def render_summary_facts(proposal, intent, util_pct):
    mode = (proposal.generation_mode or "balanced").capitalize()
    n_products = len(proposal.items)
    alto = any(it.perceived_value_level == "alto" for it in proposal.items)
    valor = "Alto" if alto else "Est&aacute;ndar"
    restr = []
    if intent:
        if intent.eco:
            restr.append("Eco")
        if intent.personalizable:
            restr.append("Personalizable")
        if intent.occasion:
            restr.append(intent.occasion.capitalize())
    cols = st.columns(4)
    cols[0].markdown("<div class='pg-hdr-label'>Modo</div>", unsafe_allow_html=True)
    cols[0].markdown(f"<div class='pg-hdr-value'>{mode}</div>", unsafe_allow_html=True)
    cols[1].markdown("<div class='pg-hdr-label'>Valor percibido</div>", unsafe_allow_html=True)
    cols[1].markdown(f"<div class='pg-hdr-value'>{valor}</div>", unsafe_allow_html=True)
    cols[2].markdown("<div class='pg-hdr-label'>Productos</div>", unsafe_allow_html=True)
    cols[2].markdown(f"<div class='pg-hdr-value'>{n_products}</div>", unsafe_allow_html=True)
    cols[3].markdown("<div class='pg-hdr-label'>Restricciones</div>", unsafe_allow_html=True)
    cols[3].markdown(
        f"<div class='pg-hdr-value'>{', '.join(restr) if restr else '—'}</div>",
        unsafe_allow_html=True,
    )


def render_product_card(item, image_map):
    thumb = item.thumbnail_url or image_map.get(item.reference)
    detail = item.detail_url or image_map.get("__url__" + item.reference)

    cols = st.columns([1, 3.5])
    with cols[0]:
        try:
            if thumb:
                st.image(thumb, width=120, caption=None)
            else:
                st.markdown(
                    "<div class='pg-img-placeholder'>Sin imagen</div>",
                    unsafe_allow_html=True,
                )
        except Exception:
            st.markdown(
                "<div class='pg-img-placeholder'>Sin imagen</div>",
                unsafe_allow_html=True,
            )

    with cols[1]:
        # Name
        if detail:
            st.markdown(
                f"<a href='{detail}' target='_blank' class='pg-name'>{item.name}</a>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"<span class='pg-name'>{item.name}</span>",
                unsafe_allow_html=True,
            )

        # Meta: reference · role
        meta_parts = []
        if item.reference:
            meta_parts.append(f"Ref: {item.reference}")
        if item.role:
            meta_parts.append(item.role)
        if meta_parts:
            st.markdown(
                f"<div class='pg-meta' style='margin-top:2px;'>{' · '.join(meta_parts)}</div>",
                unsafe_allow_html=True,
            )

        # Price line
        price_parts = []
        if item.unit_price:
            price_parts.append(f"<span class='pg-price'>{item.unit_price}</span>")
        if item.quantity:
            price_parts.append(f"Cant: {item.quantity}")
        if item.subtotal:
            price_parts.append(f"Sub: {item.subtotal}")
        if price_parts:
            st.markdown(
                f"<div class='pg-meta' style='margin-top:4px;'>{' · '.join(price_parts)}</div>",
                unsafe_allow_html=True,
            )

        # Badges
        badges = []
        if item.eco:
            badges.append("<span class='pg-badge pg-b-eco'>Eco</span>")
        if item.perceived_value_level == "alto":
            badges.append("<span class='pg-badge pg-b-premium'>Premium</span>")
        if item.personalizable:
            badges.append("<span class='pg-badge pg-b-pers'>Personalizable</span>")
        if item.role == "PACKAGING":
            badges.append("<span class='pg-badge pg-b-pack'>Packaging</span>")
        if item.role in ("CORE", "PROMOTIONAL"):
            badges.append("<span class='pg-badge pg-b-corp'>Corporativo</span>")
        if badges:
            st.markdown(
                f"<div style='margin-top:6px;'>{' '.join(badges)}</div>",
                unsafe_allow_html=True,
            )

        # Selection reason
        reason = (item.selection_reason or "").strip()
        if reason:
            st.markdown(
                f"<div class='pg-reason'>{reason}</div>",
                unsafe_allow_html=True,
            )

        # Detail link
        if detail:
            st.markdown(
                f"<div style='margin-top:6px;'><a href='{detail}' target='_blank' class='pg-link'>"
                f"Ver ficha →</a></div>",
                unsafe_allow_html=True,
            )


def render_executive_summary(text: str):
    if not text:
        return
    sections = {"Resumen": "", "Ventajas": [], "Ideal para": ""}
    current = None
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        low = line.lower()
        if low.startswith("resumen"):
            current = "Resumen"
            continue
        if low.startswith("ventajas"):
            current = "Ventajas"
            continue
        if low.startswith("ideal para"):
            current = "Ideal para"
            continue
        if current == "Resumen":
            sections["Resumen"] += line + " "
        elif current == "Ideal para":
            sections["Ideal para"] += line + " "
        elif current == "Ventajas":
            if line.startswith("•") or line.startswith("-"):
                sections["Ventajas"].append(line.lstrip("•- ").strip())
    if sections["Resumen"]:
        st.markdown(
            f"<div style='font-size:13px;color:#374151;margin-bottom:8px;'>{sections['Resumen'].strip()}</div>",
            unsafe_allow_html=True,
        )
    if sections["Ventajas"]:
        st.markdown(
            "<div style='font-size:12px;font-weight:600;color:#374151;margin-bottom:4px;'>Ventajas</div>",
            unsafe_allow_html=True,
        )
        for v in sections["Ventajas"][:3]:
            st.markdown(
                f"<div style='font-size:12px;color:#6B7280;margin-left:8px;'>• {v}</div>",
                unsafe_allow_html=True,
            )
    if sections["Ideal para"]:
        st.markdown(
            f"<div style='font-size:13px;color:#374151;margin-top:8px;'>"
            f"<strong>Ideal para:</strong> {sections['Ideal para'].strip()}</div>",
            unsafe_allow_html=True,
        )


def render_proposal_score_card(proposal):
    if not proposal.score_card:
        return
    card = proposal.score_card

    st.markdown(
        "<div class='pg-section-title' style='margin-top:0;'>Evaluaci&oacute;n detallada</div>",
        unsafe_allow_html=True,
    )

    SCORE_GROUPS = {
        "Presupuesto": [
            ("Eficiencia", card.budget_score),
        ],
        "Calidad": [
            ("Valor comercial", card.commercial_score),
            ("Coherencia", card.coherence_score),
            ("Utilidad", card.utility_score),
            ("Visibilidad de marca", card.brand_visibility_score),
            ("Premium", card.premium_score),
            ("Balance", card.balance_score),
            ("Complementariedad", card.complementarity_score),
        ],
        "Alineaci&oacute;n": [
            ("Ocasi&oacute;n", card.occasion_score),
            ("Audiencia", card.audience_score),
            ("Industria", card.industry_score),
            ("Modo", card.mode_coherence_score),
        ],
        "Diversidad": [
            ("Productos", card.diversity_score),
            ("Categor&iacute;as", card.category_diversity_score),
        ],
        "Sostenibilidad": [
            ("Eco", card.eco_score),
            ("Materiales", card.material_cleanliness_score),
        ],
        "Personalizaci&oacute;n": [
            ("Personalizaci&oacute;n", card.personalization_score),
        ],
    }

    for group_name, metrics in SCORE_GROUPS.items():
        st.markdown(
            f"<div class='pg-criterion-group'>{group_name}</div>",
            unsafe_allow_html=True,
        )
        gcols = st.columns(len(metrics))
        for ci, (label, val) in enumerate(metrics):
            with gcols[ci]:
                c = score_color(val)
                st.markdown(
                    f"<div style='font-size:11px;color:#9CA3AF;font-weight:500;text-align:center;'>{label}</div>",
                    unsafe_allow_html=True,
                )
                st.progress(val / 100.0 if val > 0 else 0.01)
                st.markdown(
                    f"<div style='font-size:13px;font-weight:700;color:{c};text-align:center;'>{val:.0f}</div>",
                    unsafe_allow_html=True,
                )

    # Criteria details
    if card.criteria:
        with st.expander("Ver criterios detallados", expanded=False):
            for c in card.criteria:
                st.markdown(
                    f"<div style='font-size:12px;margin-bottom:6px;'>"
                    f"<strong>{c.name}:</strong> "
                    f"<span style='color:{score_color(c.score)};font-weight:600;'>{c.score:.0f}/100</span>"
                    f" <span style='color:#9CA3AF;'>(peso {c.weight:.2f})</span>"
                    f"<br><span style='color:#6B7280;'>{c.reason}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

    # Observations
    if card.observations:
        with st.expander("Observaciones", expanded=False):
            for o in card.observations:
                st.markdown(
                    f"<div style='font-size:12px;color:#6B7280;margin-bottom:4px;'>• {o}</div>",
                    unsafe_allow_html=True,
                )


def render_proposal(proposal, key_prefix, parent_document=None):
    image_map = load_image_map()
    doc = parent_document
    intent = get_intent_for(proposal, doc)

    max_total = None
    if intent:
        quantity = intent.quantity or proposal.units
        if intent.budget_per_unit:
            max_total = intent.budget_per_unit * quantity
        elif intent.budget_total:
            max_total = intent.budget_total
    util_pct = (
        proposal.total_cost.amount / max_total * 100
        if (max_total and max_total > 0)
        else None
    )

    band, color = score_band(proposal.score)
    mode_label = (proposal.generation_mode or "balanced").capitalize()

    st.markdown("<div class='pg-card'>", unsafe_allow_html=True)

    # ---- HEADER: Title + Score + Mode + Metrics ----
    hcols = st.columns([2, 1.2, 1.2, 1.2, 1.2, 1])
    with hcols[0]:
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:10px;'>"
            f"<span style='font-size:20px;font-weight:700;color:#111827;'>{proposal.name}</span>"
            f"<span style='font-size:12px;font-weight:500;color:#9CA3AF;background:#F3F4F6;"
            f"padding:2px 8px;border-radius:6px;'>v{proposal.version}</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    with hcols[1]:
        ring_bg = f"{color}15"
        st.markdown(
            f"<div style='display:flex;align-items:center;gap:8px;'>"
            f"<div style='width:48px;height:48px;border-radius:50%;background:{ring_bg};"
            f"display:flex;align-items:center;justify-content:center;"
            f"color:{color};font-weight:700;font-size:18px;'>{proposal.score:.0f}</div>"
            f"<div><div style='font-weight:600;font-size:13px;color:{color};'>{band}</div>"
            f"<div style='font-size:11px;color:#9CA3AF;'>Score</div></div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    with hcols[2]:
        st.markdown("<div class='pg-hdr-label'>Modo</div>", unsafe_allow_html=True)
        st.markdown(f"<div><span class='pg-mode-chip'>{mode_label}</span></div>", unsafe_allow_html=True)

    with hcols[3]:
        st.markdown("<div class='pg-hdr-label'>Costo total</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='pg-hdr-value'>{proposal.total_cost}</div>", unsafe_allow_html=True)

    with hcols[4]:
        st.markdown("<div class='pg-hdr-label'>Por unidad</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='pg-hdr-value'>{proposal.per_unit_cost}</div>", unsafe_allow_html=True)

    with hcols[5]:
        st.markdown("<div class='pg-hdr-label'>Productos</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='pg-hdr-value'>{len(proposal.items)}</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin:16px 0;border-top:1px solid #F3F4F6;'></div>", unsafe_allow_html=True)

    # ---- BODY: Products (left) + Summary (right) ----
    left, right = st.columns([7, 3])

    with left:
        st.markdown("<div class='pg-section-title'>Productos</div>", unsafe_allow_html=True)
        for item in proposal.items:
            with st.container():
                render_product_card(item, image_map)

    with right:
        # Executive summary
        if proposal.commercial_description:
            st.markdown(
                "<div style='background:#F9FAFB;border-radius:10px;padding:16px;margin-bottom:12px;'>"
                "<div class='pg-section-title' style='margin-top:0;'>Resumen ejecutivo</div>",
                unsafe_allow_html=True,
            )
            render_executive_summary(proposal.commercial_description)
            st.markdown("</div>", unsafe_allow_html=True)

        # Warnings
        if proposal.warnings:
            st.markdown(
                f"<div style='background:#FEF2F2;border-radius:10px;padding:12px 16px;margin-bottom:12px;'>"
                f"<div style='display:flex;align-items:center;gap:6px;margin-bottom:6px;'>"
                f"<span style='color:{DANGER};font-weight:600;font-size:12px;'>⚠</span>"
                f"<span style='color:{DANGER};font-weight:600;font-size:12px;'>Advertencias</span>"
                f"</div>",
                unsafe_allow_html=True,
            )
            for w in proposal.warnings:
                st.markdown(
                    f"<div class='pg-warning'>• {w}</div>",
                    unsafe_allow_html=True,
                )
            st.markdown("</div>", unsafe_allow_html=True)

        # Why this proposal
        st.markdown(
            "<div style='background:#F9FAFB;border-radius:10px;padding:16px;margin-bottom:12px;'>"
            "<div class='pg-section-title' style='margin-top:0;'>¿Por qu&eacute; esta propuesta?</div>",
            unsafe_allow_html=True,
        )
        for bullet in build_recommendation_bullets(proposal, intent, util_pct):
            st.markdown(
                f"<div style='font-size:13px;color:#374151;margin-bottom:4px;'>• {bullet}</div>",
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        # Summary facts
        st.markdown(
            "<div style='background:#F9FAFB;border-radius:10px;padding:16px;margin-bottom:12px;'>",
            unsafe_allow_html=True,
        )
        render_summary_facts(proposal, intent, util_pct)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin:16px 0;border-top:1px solid #F3F4F6;'></div>", unsafe_allow_html=True)

    # ---- SCORE CARD ----
    render_proposal_score_card(proposal)

    st.markdown("<div style='margin:16px 0;border-top:1px solid #F3F4F6;'></div>", unsafe_allow_html=True)

    # ---- BUDGET ----
    render_budget(intent, proposal)

    st.markdown("<div style='margin:16px 0;border-top:1px solid #F3F4F6;'></div>", unsafe_allow_html=True)

    # ---- REFINE ----
    st.markdown("<div class='pg-section-title'>Refinar propuesta</div>", unsafe_allow_html=True)
    instruction = st.text_input(
        "Escribe una instrucci&oacute;n (ej. 'Cambia el mug por un termo', "
        "'Hazla m&aacute;s premium', 'No quiero pl&aacute;stico')",
        key=f"{key_prefix}_instruction",
        label_visibility="collapsed",
        placeholder="Ej: Cambia el mug por un termo, Hazla m&aacute;s premium...",
    )
    if st.button("Aplicar refinamiento", key=f"{key_prefix}_refine", type="primary"):
        if instruction.strip():
            with st.spinner("Refinando propuesta..."):
                try:
                    refine_uc = build_refine_proposal_use_case(
                        top_k=st.session_state.get("top_k_eff", settings.top_k * 10),
                        llm_model=st.session_state.get("model", settings.ollama_model),
                    )
                    original = st.session_state.proposals[proposal.proposal_id]
                    new_proposal, log, action = refine_uc.execute(
                        proposal=original,
                        instruction=instruction,
                        parent_document=parent_document,
                    )
                    st.session_state.proposals[new_proposal.proposal_id] = new_proposal
                    st.session_state.documents[new_proposal.proposal_id] = parent_document
                    st.session_state.log.append(
                        (new_proposal.proposal_id, action, log)
                    )
                    st.rerun()
                except Exception as exc:
                    st.error(f"No se pudo refinar la propuesta: {exc}")

    st.markdown("</div>", unsafe_allow_html=True)  # close pg-card


def render_saved_sidebar(workspace):
    st.sidebar.markdown(
        "<div style='font-size:16px;font-weight:700;color:#111827;margin-bottom:12px;'>"
        "Propuestas guardadas</div>",
        unsafe_allow_html=True,
    )
    docs = workspace.list_documents()
    if not docs:
        st.sidebar.caption("A&uacute;n no hay propuestas guardadas.")
        return
    options = {
        f"{d.proposal_id} | v{d.version} | {d.created_at[:10]} | {d.intent.occasion or '—'}": d.proposal_id
        for d in sorted(docs, key=lambda x: x.updated_at, reverse=True)
    }
    selected = st.sidebar.selectbox("Abrir propuesta", options=list(options.keys()), label_visibility="collapsed")
    if selected and st.sidebar.button("Cargar propuesta", use_container_width=True):
        doc = workspace.open(options[selected])
        if doc:
            st.session_state.proposals = {doc.proposal_id: doc.proposal}
            st.session_state.documents = {doc.proposal_id: doc}
            st.session_state.log = []
            st.rerun()

    st.sidebar.markdown(
        "<div style='font-size:14px;font-weight:600;color:#111827;margin:16px 0 8px 0;'>Buscar</div>",
        unsafe_allow_html=True,
    )
    q_text = st.sidebar.text_input("Texto", label_visibility="collapsed", placeholder="Texto")
    q_occ = st.sidebar.text_input("Ocasi&oacute;n", label_visibility="collapsed", placeholder="Ocasi&oacute;n")
    q_prod = st.sidebar.text_input("Producto", label_visibility="collapsed", placeholder="Producto")
    if st.sidebar.button("Buscar", use_container_width=True):
        found = workspace.search(text=q_text, occasion=q_occ, products=q_prod)
        st.session_state.search_results = [
            f"{d.proposal_id} | v{d.version} | {d.created_at[:10]}" for d in found
        ]

    st.sidebar.markdown(
        "<div style='font-size:14px;font-weight:600;color:#111827;margin:16px 0 8px 0;'>Versiones</div>",
        unsafe_allow_html=True,
    )
    root_options = {}
    for d in docs:
        root_options.setdefault(d.root_id, [])
        root_options[d.root_id].append(d)
    for root, versions in root_options.items():
        if len(versions) < 2:
            continue
        st.sidebar.markdown(
            f"<div style='font-size:12px;font-weight:600;color:#374151;'>{root}</div>",
            unsafe_allow_html=True,
        )
        labels = [f"v{v.version} ({v.created_at[:10]})" for v in versions]
        choice = st.sidebar.selectbox("Versi&oacute;n", labels, key=f"ver_{root}", label_visibility="collapsed")
        idx = labels.index(choice)
        if st.sidebar.button("Abrir versi&oacute;n", key=f"open_{root}", use_container_width=True):
            doc = versions[idx]
            st.session_state.proposals = {doc.proposal_id: doc.proposal}
            st.session_state.documents = {doc.proposal_id: doc}
            st.rerun()

        cmp_root = st.sidebar.selectbox("Comparar con", [""] + labels, key=f"cmp_{root}", label_visibility="collapsed")
        if cmp_root:
            other = versions[labels.index(cmp_root)]
            comparator = VersionComparator()
            comp = comparator.compare(versions[idx], other)
            with st.sidebar.expander("Comparaci&oacute;n"):
                st.caption(f"v{comp.from_version} -> v{comp.to_version}")
                for obs in comp.observations:
                    st.caption(obs)


def choose_top_k(intent: CommercialIntent, manual: bool, manual_k: int) -> int:
    if manual:
        return manual_k
    if intent is None:
        return settings.top_k * 10
    specificity = 0
    if intent.occasion:
        specificity += 1
    if intent.target_audience:
        specificity += 1
    if intent.budget_per_unit or intent.budget_total:
        specificity += 1
    if intent.eco or intent.personalizable:
        specificity += 1
    if specificity >= 3:
        return 30
    if specificity == 2:
        return 60
    return 100


# ---- SIDEBAR ----
with st.sidebar:
    st.markdown(
        "<div style='font-size:16px;font-weight:700;color:#111827;margin-bottom:16px;'>"
        "Configuraci&oacute;n</div>",
        unsafe_allow_html=True,
    )

    with st.container():
        st.markdown(
            "<div class='pg-section-title' style='margin-bottom:6px;'>Motor</div>",
            unsafe_allow_html=True,
        )
        model = st.text_input("Modelo Ollama", value=settings.ollama_model, key="model_input")
        st.session_state.setdefault("model", model)
        st.session_state.model = model

    st.markdown("<div style='margin:12px 0;'></div>", unsafe_allow_html=True)

    with st.container():
        st.markdown(
            "<div class='pg-section-title' style='margin-bottom:6px;'>Modo</div>",
            unsafe_allow_html=True,
        )
        mode = st.selectbox("Generaci&oacute;n", MODES, index=0, label_visibility="collapsed")

    st.markdown("<div style='margin:12px 0;'></div>", unsafe_allow_html=True)

    with st.container():
        st.markdown(
            "<div class='pg-section-title' style='margin-bottom:6px;'>B&uacute;squeda</div>",
            unsafe_allow_html=True,
        )
        search_mode = st.radio("Recuperaci&oacute;n", ["Autom&aacute;tico", "Manual"], index=0, horizontal=True)
        manual_k = st.number_input(
            "Top K", min_value=10, max_value=200, value=settings.top_k * 10, step=10,
            disabled=(search_mode == "Autom&aacute;tico"),
        )

    st.markdown("<div style='margin:16px 0;'></div>", unsafe_allow_html=True)

    with st.container():
        generate = st.button("Generar propuesta", type="primary", use_container_width=True)


# ---- MAIN FLOW ----
workspace = build_proposal_workspace()

if not is_catalog_indexed():
    st.error(
        "El cat&aacute;logo no est&aacute; indexado. Ejecuta primero:\n\n"
        "python scripts/index_catalog.py"
    )
    st.stop()

if not is_ollama_available(model):
    st.error(
        f"Ollama no est&aacute; disponible.\n\n"
        f"Modelo configurado: {model}\n"
        f"Host: {settings.ollama_host}\n\n"
        "Para iniciarlo:\n"
        "1. Instala Ollama (https://ollama.com)\n"
        f"2. ollama pull {model}\n"
        "3. ollama serve"
    )
    st.stop()

if "proposals" not in st.session_state:
    st.session_state.proposals = {}
if "documents" not in st.session_state:
    st.session_state.documents = {}
if "log" not in st.session_state:
    st.session_state.log = []

render_saved_sidebar(workspace)


def render_comparison_table(proposals_list):
    if len(proposals_list) < 2:
        return
    st.markdown(
        "<div class='pg-section-title'>Comparaci&oacute;n de propuestas</div>",
        unsafe_allow_html=True,
    )
    rows = []
    for p in proposals_list:
        rows.append({
            "Propuesta": p.name,
            "Score": f"{p.score:.0f}",
            "Modo": (p.generation_mode or "balanced").capitalize(),
            "Total": str(p.total_cost),
            "Unidad": str(p.per_unit_cost),
            "Productos": len(p.items),
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)


# ---- INPUT ----
st.markdown(
    "<div style='font-size:16px;font-weight:600;color:#111827;margin-bottom:8px;'>"
    "Describe la necesidad del cliente</div>",
    unsafe_allow_html=True,
)
text = st.text_area(
    "Necesidad",
    height=120,
    label_visibility="collapsed",
    placeholder="Ejemplo:\n"
    "Necesito 3800 regalos de cumpleaños para mujeres con un "
    "presupuesto máximo de 25000 COP por unidad.",
)

# ---- GENERATION ----
if generate and text.strip():
    from promotional_gifts.domain.services.generation_mode import GenerationMode

    gen_mode = GenerationMode.parse(mode)

    analyzer = IntentAnalyzer()
    intent = analyzer.analyze(text)
    top_k = choose_top_k(intent, search_mode == "Manual", manual_k)
    st.session_state.top_k_eff = top_k
    st.session_state.last_intent = intent

    with st.status("Generando propuestas comerciales...", expanded=False) as status:
        status.write("Analizando intenci&oacute;n del cliente...")
        status.write("Consultando cat&aacute;logo de productos...")
        status.write("Construyendo y evaluando propuestas...")

        use_case = build_generate_proposal_use_case(
            top_k=top_k, llm_model=model, mode=gen_mode, workspace=None
        )
        try:
            proposal_set = use_case.execute(text)
            proposals = proposal_set.proposals
        except Exception as exc:
            status.update(label="Error al generar", state="error")
            st.error(f"No se pudo generar la propuesta: {exc}")
            st.stop()

        status.write("Redactando descripciones comerciales...")
        status.update(label="Propuestas generadas", state="complete", expanded=False)

    if not proposals:
        st.warning("No se encontraron propuestas para esa solicitud.")
    else:
        for i, p in enumerate(proposals, start=1):
            if not p.proposal_id:
                p.proposal_id = f"P{i}"
            p.version = 1
            p.parent_version = 0
        st.session_state.proposals = {p.proposal_id: p for p in proposals}
        st.session_state.documents = {p.proposal_id: None for p in proposals}
        st.session_state.log = []
        if proposal_set and proposal_set.global_observations:
            with st.expander("An&aacute;lisis global del set", expanded=False):
                for obs in proposal_set.global_observations:
                    st.caption(obs)
        render_comparison_table(proposals)
        for proposal in proposals:
            render_proposal(proposal, proposal.proposal_id)
        st.success("Propuestas generadas correctamente.")

elif generate:
    st.info("Escribe la necesidad del cliente antes de generar.")
else:
    proposals = list(st.session_state.proposals.values())
    render_comparison_table(proposals)
    for pid, proposal in st.session_state.proposals.items():
        parent_doc = st.session_state.documents.get(pid)
        render_proposal(proposal, pid, parent_doc)

    if st.session_state.log:
        with st.expander("Bit&aacute;cora de refinamientos", expanded=False):
            for pid, action, entries in st.session_state.log:
                st.markdown(f"**{pid} — {action}**")
                for entry in entries:
                    st.caption(
                        f"- {entry.action} | afectado: {entry.affected_product or '—'} "
                        f"| nuevo: {entry.new_product or '—'} | {entry.result}"
                    )
