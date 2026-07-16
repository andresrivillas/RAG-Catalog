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


st.set_page_config(page_title="Promotional Gifts AI", layout="wide")
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
        return "Excelente", "#1b7f3b"
    if score >= 80:
        return "Muy buena", "#2e8b57"
    if score >= 70:
        return "Buena", "#b8860b"
    if score >= 60:
        return "Aceptable", "#c97a16"
    return "Baja", "#b22222"


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
    img_col, info_col = st.columns([1, 3])
    thumb = item.thumbnail_url or image_map.get(item.reference)
    with img_col:
        try:
            if thumb:
                st.image(thumb, width=130, caption=None, use_container_width=False)
            else:
                st.markdown(
                    "<div style='width:130px;height:130px;border:1px solid #ddd;"
                    "display:flex;align-items:center;justify-content:center;"
                    "color:#999;font-size:11px;border-radius:8px;'>Sin imagen</div>",
                    unsafe_allow_html=True,
                )
        except Exception:
            st.markdown(
                "<div style='width:130px;height:130px;border:1px solid #ddd;"
                "display:flex;align-items:center;justify-content:center;"
                "color:#999;font-size:11px;border-radius:8px;'>Sin imagen</div>",
                unsafe_allow_html=True,
            )
    with info_col:
        detail = item.detail_url or image_map.get("__url__" + item.reference)
        if detail:
            st.markdown(
                f"<a href='{detail}' target='_blank' style='font-weight:700;"
                f"font-size:15px;color:#1a3e72;text-decoration:none;'>{item.name}</a>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(f"**{item.name}**")

        meta_bits = []
        if item.reference:
            meta_bits.append(f"Ref: {item.reference}")
        if item.role:
            meta_bits.append(f"Rol: {item.role}")
        if item.category and len(item.category) <= 40:
            meta_bits.append(f"Categoría: {item.category}")
        st.caption(" · ".join(meta_bits))

        price_bits = []
        if item.unit_price:
            price_bits.append(f"Precio: {item.unit_price}")
        if item.quantity:
            price_bits.append(f"Cant: {item.quantity}")
        if item.subtotal:
            price_bits.append(f"Subtotal: {item.subtotal}")
        if price_bits:
            st.caption(" · ".join(price_bits))

        attr_bits = []
        if item.materials:
            attr_bits.append(f"Material: {item.materials}")
        if item.colors:
            attr_bits.append(f"Color: {item.colors}")
        if item.capacity:
            attr_bits.append(f"Capacidad: {item.capacity}")
        if item.customization:
            attr_bits.append(f"Personalización: {item.customization}")
        badges = []
        if item.eco:
            badges.append("🌱 Eco")
        if item.personalizable:
            badges.append("🎨 Personalizable")
        if item.perceived_value_level == "alto":
            badges.append("⭐ Alto valor")
        if attr_bits:
            st.caption(" · ".join(attr_bits))
        if badges:
            st.markdown(" ".join(badges))

        reason = (item.selection_reason or "").strip()
        if reason:
            if len(reason) > 200:
                reason = reason[:197] + "..."
            st.caption(f"Por qué: {reason}")


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
    header = f"{proposal.name} · v{proposal.version}"
    header += f" · Score {proposal.score:.1f}"
    header += f" · {proposal.total_cost}"
    if util_pct is not None:
        header += f" · {util_pct:.0f}%"
    header += f" · {len(proposal.items)} productos"
    header += f" · {(proposal.generation_mode or 'balanced').capitalize()}"

    with st.expander(header, expanded=True):
        band, color = score_band(proposal.score)
        col_s, col_u, col_t, col_p = st.columns(4)
        col_s.markdown(
            f"**Score:** <span style='color:{color};font-weight:700'>{proposal.score:.1f}</span> "
            f"({band})",
            unsafe_allow_html=True,
        )
        col_u.metric("Costo por unidad", str(proposal.per_unit_cost))
        col_t.metric("Costo total", str(proposal.total_cost))
        if util_pct is not None:
            col_p.metric("Utilización", f"{util_pct:.0f} %")
        else:
            col_p.metric("Utilización", "—")

        st.divider()
        render_summary_facts(proposal, intent, util_pct)

        st.divider()
        st.markdown("**¿Por qué recomendamos esta propuesta?**")
        for bullet in build_recommendation_bullets(proposal, intent, util_pct):
            st.markdown(f"• {bullet}")

        st.divider()
        render_budget(intent, proposal)

        st.divider()
        st.subheader("Productos")
        for item in proposal.items:
            render_product_card(item, image_map)
            st.divider()

        st.divider()
        st.subheader("Resumen ejecutivo")
        render_executive_summary(proposal.commercial_description)

        if proposal.warnings:
            st.divider()
            st.warning("Advertencias: " + " | ".join(proposal.warnings))

        with st.expander("Ver análisis detallado", expanded=False):
            if proposal.score_card:
                for c in proposal.score_card.criteria:
                    st.caption(f"{c.name}: {c.score:.0f}/100 — {c.reason}")

        st.markdown("**Refinar propuesta**")
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
    model = st.text_input("Modelo Ollama utilizado", value=settings.ollama_model)
    search_mode = st.radio("Modo de búsqueda", ["Automático", "Manual"], index=0)
    manual_k = st.number_input(
        "Top K", min_value=10, max_value=200, value=settings.top_k * 10, step=10,
        disabled=(search_mode == "Automático"),
    )
    mode = st.selectbox("Modo de generación", MODES, index=0)
    generate = st.button("Generar propuesta")
    st.session_state.setdefault("model", model)
    st.session_state.model = model

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
            proposals = use_case.execute(text)
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
        for proposal in proposals:
            render_proposal(proposal, proposal.proposal_id)
        st.success("Propuestas guardadas automáticamente.")

elif generate:
    st.info("Escribe la necesidad del cliente antes de generar.")
else:
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
