import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

import streamlit as st

from config.settings import settings
from promotional_gifts.container import (
    build_generate_proposal_use_case,
    build_refine_proposal_use_case,
    build_proposal_workspace,
    is_catalog_indexed,
    is_ollama_available,
)
from promotional_gifts.application.intent_analyzer import IntentAnalyzer
from promotional_gifts.domain.services.budget_optimizer import BudgetOptimizer
from promotional_gifts.domain.services.workspace.version_comparator import (
    VersionComparator,
)
from promotional_gifts.domain.entities.commercial_intent import CommercialIntent

MODES = ["balanced", "premium", "budget", "eco"]

GREEN = "#1f9254"
ORANGE = "#c97a16"
RED = "#c0392b"
BLUE = "#1a3e72"
GREY = "#6b7280"


def inject_styles():
    st.markdown(
        """
        <style>
        html, body, [data-testid="stAppViewContainer"] {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        .pg-card {
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 14px 16px;
            background: #ffffff;
            margin-bottom: 12px;
        }
        .pg-card:hover { box-shadow: 0 2px 10px rgba(0,0,0,0.06); }
        .pg-product {
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 14px;
            background: #ffffff;
            margin-bottom: 12px;
            height: 100%;
        }
        .pg-name { font-weight: 700; font-size: 15px; color: #111827; line-height: 1.2; }
        .pg-meta { color: #6b7280; font-size: 12px; margin-top: 2px; }
        .pg-price { font-weight: 700; font-size: 14px; color: #111827; }
        .pg-badge {
            display: inline-block; font-size: 11px; font-weight: 600;
            padding: 2px 8px; border-radius: 999px; margin: 2px 4px 2px 0;
        }
        .pg-b-eco { background: #e7f6ee; color: #1f9254; }
        .pg-b-premium { background: #fef3e2; color: #c97a16; }
        .pg-b-pers { background: #eef2ff; color: #3b5bdb; }
        .pg-b-pack { background: #f1f5f9; color: #475569; }
        .pg-b-corp { background: #f1f5f9; color: #475569; }
        .pg-reason { font-size: 12px; color: #374151; margin-top: 8px; }
        .pg-score-pill {
            display: inline-flex; align-items: center; gap: 6px;
            font-weight: 700; font-size: 15px;
        }
        .pg-section-title {
            font-size: 13px; font-weight: 700; text-transform: uppercase;
            letter-spacing: 0.04em; color: #6b7280; margin: 4px 0 8px 0;
        }
        .pg-link { color: #1a3e72; text-decoration: none; font-weight: 600; font-size: 12px; }
        .pg-util-good { color: #1f9254; font-weight: 700; }
        .pg-util-warn { color: #c97a16; font-weight: 700; }
        .pg-util-bad { color: #c0392b; font-weight: 700; }
        </style>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(page_title="Promotional Gifts AI", layout="wide")
inject_styles()
st.title("Promotional Gifts AI")
st.caption("Copiloto comercial para propuestas de regalos promocionales")


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
        return "Excelente", GREEN
    if score >= 80:
        return "Muy buena", "#2e8b57"
    if score >= 70:
        return "Buena", ORANGE
    if score >= 60:
        return "Aceptable", ORANGE
    return "Baja", RED


def util_color(pct):
    if pct is None:
        return GREY
    if pct >= 80:
        return GREEN
    if pct >= 60:
        return ORANGE
    return RED


def compact_number(value: float) -> str:
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f} M"
    if value >= 1_000:
        return f"{value/1_000:.0f} K"
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

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Presupuesto máximo", f"{max_total:,.0f} COP" if max_total else "—")
    c2.metric("Costo", str(proposal.total_cost))
    if max_total:
        used = proposal.total_cost.amount / max_total * 100
        ahorro = max_total - proposal.total_cost.amount
        c3.metric("Utilizado", f"{used:.0f} %")
        c4.metric("Ahorro", f"{ahorro:,.0f} COP")
    else:
        c3.metric("Utilizado", "—")
        c4.metric("Ahorro", "—")


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
    valor = "Alto" if alto else "Estándar"
    restr = []
    if intent:
        if intent.eco:
            restr.append("Eco")
        if intent.personalizable:
            restr.append("Personalizable")
        if intent.occasion:
            restr.append(intent.occasion.capitalize())
    cols = st.columns(4)
    cols[0].metric("Modo", mode)
    cols[1].metric("Valor percibido", valor)
    cols[2].metric("Productos", str(n_products))
    cols[3].metric(
        "Restricciones", ", ".join(restr) if restr else "—"
    )


def render_product_card(item, image_map):
    thumb = item.thumbnail_url or image_map.get(item.reference)
    detail = item.detail_url or image_map.get("__url__" + item.reference)

    with st.container(border=True):
        cols = st.columns([1, 3])
        with cols[0]:
            try:
                if thumb:
                    st.image(thumb, width=120, caption=None, use_container_width=False)
                else:
                    st.markdown(
                        "<div style='width:120px;height:120px;border:1px solid #e5e7eb;"
                        "display:flex;align-items:center;justify-content:center;"
                        "color:#9ca3af;font-size:11px;border-radius:8px;'>Sin imagen</div>",
                        unsafe_allow_html=True,
                    )
            except Exception:
                st.markdown(
                    "<div style='width:120px;height:120px;border:1px solid #e5e7eb;"
                    "display:flex;align-items:center;justify-content:center;"
                    "color:#9ca3af;font-size:11px;border-radius:8px;'>Sin imagen</div>",
                    unsafe_allow_html=True,
                )
        with cols[1]:
            if detail:
                st.markdown(
                    f"<a href='{detail}' target='_blank' class='pg-name'>{item.name}</a>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(f"<span class='pg-name'>{item.name}</span>", unsafe_allow_html=True)

            meta = []
            if item.reference:
                meta.append(f"Ref: {item.reference}")
            if item.role:
                meta.append(item.role)
            st.markdown(
                f"<div class='pg-meta'>{' · '.join(meta)}</div>", unsafe_allow_html=True
            )

            price_line = ""
            if item.unit_price:
                price_line += f"Precio {item.unit_price}"
            if item.quantity:
                price_line += f" · Cant {item.quantity}"
            if item.subtotal:
                price_line += f" · Subtotal {item.subtotal}"
            if price_line:
                st.markdown(f"<div class='pg-meta'>{price_line}</div>", unsafe_allow_html=True)

            badges = []
            if item.eco:
                badges.append("<span class='pg-badge pg-b-eco'>🟢 Eco</span>")
            if item.perceived_value_level == "alto":
                badges.append("<span class='pg-badge pg-b-premium'>⭐ Premium</span>")
            if item.personalizable:
                badges.append("<span class='pg-badge pg-b-pers'>🎨 Personalizable</span>")
            if item.role == "PACKAGING":
                badges.append("<span class='pg-badge pg-b-pack'>📦 Packaging</span>")
            if item.role in ("CORE", "PROMOTIONAL"):
                badges.append("<span class='pg-badge pg-b-corp'>💼 Corporativo</span>")
            if badges:
                st.markdown(" ".join(badges), unsafe_allow_html=True)

            reason = (item.selection_reason or "").strip()
            if reason:
                if len(reason) > 120:
                    reason = reason[:117] + "..."
                st.markdown(f"<div class='pg-reason'>💡 {reason}</div>", unsafe_allow_html=True)

            if detail:
                st.markdown(
                    f"<a href='{detail}' target='_blank' class='pg-link'>Ver ficha →</a>",
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
        st.markdown(f"**Resumen:** {sections['Resumen'].strip()}")
    if sections["Ventajas"]:
        st.markdown("**Ventajas:**")
        for v in sections["Ventajas"][:3]:
            st.markdown(f"• {v}")
    if sections["Ideal para"]:
        st.markdown(f"**Ideal para:** {sections['Ideal para'].strip()}")


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

    # ---- BLOCK 1: Header metrics row ----
    band, color = score_band(proposal.score)
    util_col = util_color(util_pct)
    h_cols = st.columns([2, 1, 1, 1, 1, 1, 1])
    with h_cols[0]:
        st.markdown(
            f"<div style='font-weight:700;font-size:18px;color:#111827'>"
            f"{proposal.name} <span style='color:#6b7280;font-size:13px;font-weight:500'>"
            f"v{proposal.version}</span></div>",
            unsafe_allow_html=True,
        )
    with h_cols[1]:
        st.markdown(
            f"<div class='pg-score-pill'><span style='color:{color}'>🟠 {proposal.score:.0f}</span>"
            f"<span style='color:#6b7280;font-size:12px;font-weight:500'>{band}</span></div>",
            unsafe_allow_html=True,
        )
    with h_cols[2]:
        st.markdown(
            f"<div class='pg-meta'>Modo</div>"
            f"<div style='font-weight:700'>{ (proposal.generation_mode or 'balanced').capitalize() }</div>",
            unsafe_allow_html=True,
        )
    with h_cols[3]:
        st.markdown(
            f"<div class='pg-meta'>Costo total</div>"
            f"<div style='font-weight:700'>{proposal.total_cost}</div>",
            unsafe_allow_html=True,
        )
    with h_cols[4]:
        st.markdown(
            f"<div class='pg-meta'>Por unidad</div>"
            f"<div style='font-weight:700'>{proposal.per_unit_cost}</div>",
            unsafe_allow_html=True,
        )
    with h_cols[5]:
        util_disp = f"{util_pct:.0f} %" if util_pct is not None else "—"
        st.markdown(
            f"<div class='pg-meta'>Utilización</div>"
            f"<div class='pg-util-{'good' if util_col==GREEN else 'warn' if util_col==ORANGE else 'bad'}'>"
            f"{util_disp}</div>",
            unsafe_allow_html=True,
        )
    with h_cols[6]:
        st.markdown(
            f"<div class='pg-meta'>Productos</div>"
            f"<div style='font-weight:700'>{len(proposal.items)}</div>",
            unsafe_allow_html=True,
        )

    st.divider()

    # ---- BLOCK 2: Body 70/30 ----
    left, right = st.columns([7, 3])

    with left:
        st.markdown("<div class='pg-section-title'>Propuesta de productos</div>", unsafe_allow_html=True)
        for item in proposal.items:
            render_product_card(item, image_map)

    with right:
        with st.container(border=True):
            st.markdown("<div class='pg-section-title'>Resumen ejecutivo</div>", unsafe_allow_html=True)
            render_executive_summary(proposal.commercial_description)

            if proposal.warnings:
                st.markdown(
                    f"<div class='pg-badge' style='background:#fdecea;color:{RED}'>"
                    f"⚠ {len(proposal.warnings)} advertencia(s)</div>",
                    unsafe_allow_html=True,
                )
                for w in proposal.warnings:
                    st.caption(w)

        with st.container(border=True):
            st.markdown("<div class='pg-section-title'>¿Por qué esta propuesta?</div>", unsafe_allow_html=True)
            for bullet in build_recommendation_bullets(proposal, intent, util_pct):
                st.markdown(f"• {bullet}")

        with st.container(border=True):
            render_summary_facts(proposal, intent, util_pct)

    st.divider()

    # ---- BLOCK 3: Budget overview ----
    render_budget(intent, proposal)

    st.divider()

    # ---- BLOCK 4: Footer — refine + analysis ----
    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("<div class='pg-section-title'>Refinar propuesta</div>", unsafe_allow_html=True)
        instruction = st.text_input(
            "Escribe una instrucción (ej. 'Cambia el mug por un termo', "
            "'Hazla más premium', 'No quiero plástico')",
            key=f"{key_prefix}_instruction",
        )
        if st.button("Aplicar refinamiento", key=f"{key_prefix}_refine"):
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

    with c2:
        with st.expander("Análisis detallado", expanded=False):
            if proposal.score_card:
                for c in proposal.score_card.criteria:
                    st.caption(f"{c.name}: {c.score:.0f}/100 — {c.reason}")


def render_saved_sidebar(workspace):
    st.sidebar.header("Propuestas guardadas")
    docs = workspace.list_documents()
    if not docs:
        st.sidebar.caption("Aún no hay propuestas guardadas.")
        return
    options = {
        f"{d.proposal_id} | v{d.version} | {d.created_at[:10]} | {d.intent.occasion or '—'}": d.proposal_id
        for d in sorted(docs, key=lambda x: x.updated_at, reverse=True)
    }
    selected = st.sidebar.selectbox("Abrir propuesta", options=list(options.keys()))
    if selected and st.sidebar.button("Cargar propuesta"):
        doc = workspace.open(options[selected])
        if doc:
            st.session_state.proposals = {doc.proposal_id: doc.proposal}
            st.session_state.documents = {doc.proposal_id: doc}
            st.session_state.log = []
            st.rerun()

    st.sidebar.subheader("Buscar")
    q_text = st.sidebar.text_input("Texto")
    q_occ = st.sidebar.text_input("Ocasión")
    q_prod = st.sidebar.text_input("Producto")
    if st.sidebar.button("Buscar"):
        found = workspace.search(text=q_text, occasion=q_occ, products=q_prod)
        st.session_state.search_results = [
            f"{d.proposal_id} | v{d.version} | {d.created_at[:10]}" for d in found
        ]

    st.sidebar.subheader("Versiones")
    root_options = {}
    for d in docs:
        root_options.setdefault(d.root_id, [])
        root_options[d.root_id].append(d)
    for root, versions in root_options.items():
        if len(versions) < 2:
            continue
        st.sidebar.markdown(f"**{root}** ({len(versions)} versiones)")
        labels = [f"v{v.version} ({v.created_at[:10]})" for v in versions]
        choice = st.sidebar.selectbox("Versión", labels, key=f"ver_{root}")
        idx = labels.index(choice)
        if st.sidebar.button("Abrir versión", key=f"open_{root}"):
            doc = versions[idx]
            st.session_state.proposals = {doc.proposal_id: doc.proposal}
            st.session_state.documents = {doc.proposal_id: doc}
            st.rerun()

        cmp_root = st.sidebar.selectbox("Comparar con", [""] + labels, key=f"cmp_{root}")
        if cmp_root:
            other = versions[labels.index(cmp_root)]
            comparator = VersionComparator()
            comp = comparator.compare(versions[idx], other)
            with st.sidebar.expander("Comparación"):
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


with st.sidebar:
    st.header("Configuración")

    with st.container(border=True):
        st.markdown("<div class='pg-section-title'>Motor</div>", unsafe_allow_html=True)
        model = st.text_input("Modelo Ollama", value=settings.ollama_model, key="model_input")
        st.session_state.setdefault("model", model)
        st.session_state.model = model

    with st.container(border=True):
        st.markdown("<div class='pg-section-title'>Modo</div>", unsafe_allow_html=True)
        mode = st.selectbox("Generación", MODES, index=0)

    with st.container(border=True):
        st.markdown("<div class='pg-section-title'>Búsqueda</div>", unsafe_allow_html=True)
        search_mode = st.radio("Recuperación", ["Automático", "Manual"], index=0, horizontal=True)
        manual_k = st.number_input(
            "Top K", min_value=10, max_value=200, value=settings.top_k * 10, step=10,
            disabled=(search_mode == "Manual"),
        )

    with st.container(border=True):
        st.markdown("<div class='pg-section-title'>Opciones</div>", unsafe_allow_html=True)
        generate = st.button("Generar propuesta", type="primary", use_container_width=True)

workspace = build_proposal_workspace()

if not is_catalog_indexed():
    st.error(
        "El catálogo no está indexado. Ejecuta primero:\n\n"
        "python scripts/index_catalog.py"
    )
    st.stop()

if not is_ollama_available(model):
    st.error(
        f"Ollama no está disponible.\n\n"
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


def render_comparison_table(proposals):
    if len(proposals) < 2:
        return
    st.markdown("<div class='pg-section-title'>Comparación de propuestas</div>", unsafe_allow_html=True)
    rows = []
    for p in proposals:
        util = None
        rows.append({
            "Propuesta": p.name,
            "Score": f"{p.score:.0f}",
            "Modo": (p.generation_mode or "balanced").capitalize(),
            "Total": str(p.total_cost),
            "Unidad": str(p.per_unit_cost),
            "Productos": len(p.items),
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)

st.subheader("Describe la necesidad del cliente")
text = st.text_area(
    "Necesidad",
    height=120,
    placeholder=(
        "Ejemplo:\n"
        "Necesito 3800 regalos de cumpleaños para mujeres con un "
        "presupuesto máximo de 25000 COP por unidad."
    ),
)

if generate and text.strip():
    from promotional_gifts.domain.services.generation_mode import GenerationMode

    gen_mode = GenerationMode.parse(mode)

    analyzer = IntentAnalyzer()
    intent = analyzer.analyze(text)
    top_k = choose_top_k(intent, search_mode == "Manual", manual_k)
    st.session_state.top_k_eff = top_k
    st.session_state.last_intent = intent

    with st.spinner("Generando propuestas comerciales..."):
        try:
            use_case = build_generate_proposal_use_case(
                top_k=top_k, llm_model=model, mode=gen_mode
            )
            proposal_set = use_case.execute(text)
            proposals = proposal_set.proposals
        except Exception as exc:
            st.error(f"No se pudo generar la propuesta: {exc}")
            st.stop()

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
            with st.expander("Análisis global del set", expanded=False):
                for obs in proposal_set.global_observations:
                    st.caption(obs)
        render_comparison_table(proposals)
        for proposal in proposals:
            render_proposal(proposal, proposal.proposal_id)
        st.success("Propuestas guardadas automáticamente.")

elif generate:
    st.info("Escribe la necesidad del cliente antes de generar.")
else:
    proposals = list(st.session_state.proposals.values())
    render_comparison_table(proposals)
    for pid, proposal in st.session_state.proposals.items():
        parent_doc = st.session_state.documents.get(pid)
        render_proposal(proposal, pid, parent_doc)

    if st.session_state.log:
        with st.expander("Bitácora de refinamientos", expanded=False):
            for pid, action, entries in st.session_state.log:
                st.markdown(f"**{pid} — {action}**")
                for entry in entries:
                    st.caption(
                        f"- {entry.action} | afectado: {entry.affected_product or '—'} "
                        f"| nuevo: {entry.new_product or '—'} | {entry.result}"
                    )
