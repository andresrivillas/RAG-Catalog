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
from promotional_gifts.domain.services.workspace.version_comparator import (
    VersionComparator,
)

MODES = ["balanced", "premium", "budget", "eco"]

st.set_page_config(page_title="Promotional Gifts AI", layout="wide")

st.title("Promotional Gifts AI")
st.caption("Asistente Inteligente para Propuestas Comerciales")


def _assign_ids(proposals):
    for i, p in enumerate(proposals, start=1):
        if not p.proposal_id:
            p.proposal_id = f"P{i}"
        p.version = 1
        p.parent_version = 0


def _render_proposal(proposal, key_prefix, parent_document=None):
    with st.expander(f"{proposal.name} (v{proposal.version})", expanded=True):
        col1, col2, col3 = st.columns(3)
        col1.metric("Score", f"{proposal.score:.1f}")
        col2.metric("Costo por unidad", str(proposal.per_unit_cost))
        col3.metric("Costo total", str(proposal.total_cost))

        for item in proposal.items:
            with st.container():
                c1, c2 = st.columns([3, 1])
                c1.markdown(f"**{item.name}**")
                c1.caption(
                    f"Ref: {item.reference} · Cantidad: {item.quantity} · "
                    f"Precio: {item.unit_price} · Subtotal: {item.subtotal}"
                )
                c2.markdown(f"**Rol:** {item.role or '—'}")
                st.caption(f"Selección: {item.selection_reason}")
                st.divider()

        if proposal.commercial_description:
            st.markdown("**Descripción comercial**")
            st.write(proposal.commercial_description)

        if proposal.warnings:
            st.warning("Advertencias: " + " | ".join(proposal.warnings))

        if proposal.score_card:
            with st.expander("Score card (evaluación)"):
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
                            top_k=st.session_state.get("top_k", settings.top_k * 10),
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


def _render_saved_sidebar(workspace):
    st.sidebar.header("Propuestas guardadas")
    docs = workspace.list_documents()
    if not docs:
        st.sidebar.caption("Aún no hay propuestas guardadas.")
        return
    options = {
        f"{d.proposal_id} | v{d.version} | {d.created_at[:10]} | {d.intent.occasion or '—'}": d.proposal_id
        for d in sorted(docs, key=lambda x: x.updated_at, reverse=True)
    }
    selected = st.sidebar.selectbox(
        "Abrir propuesta", options=list(options.keys())
    )
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

        cmp_root = st.sidebar.selectbox(
            "Comparar con", [""] + labels, key=f"cmp_{root}"
        )
        if cmp_root:
            other = versions[[l for l in labels].index(cmp_root)]
            comparator = VersionComparator()
            comp = comparator.compare(versions[idx], other)
            with st.sidebar.expander("Comparación"):
                st.caption(f"v{comp.from_version} -> v{comp.to_version}")
                for obs in comp.observations:
                    st.caption(obs)


with st.sidebar:
    st.header("Configuración")
    model = st.text_input("Modelo Ollama utilizado", value=settings.ollama_model)
    top_k = st.number_input(
        "Top K", min_value=10, max_value=200, value=settings.top_k * 10, step=10
    )
    mode = st.selectbox("Modo de generación", MODES, index=0)
    generate = st.button("Generar propuesta")
    st.session_state.setdefault("model", model)
    st.session_state.setdefault("top_k", top_k)
    st.session_state.model = model
    st.session_state.top_k = top_k

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

_render_saved_sidebar(workspace)

st.subheader("Describe la necesidad del cliente")
text = st.text_area(
    "Necesidad",
    height=160,
    placeholder=(
        "Ejemplo:\n"
        "Necesito 3800 regalos de cumpleaños para mujeres con un "
        "presupuesto máximo de 25000 COP por unidad."
    ),
)

if generate and text.strip():
    query = text
    if mode != "balanced":
        query = f"{text} modo {mode}"

    with st.spinner("Generando propuestas comerciales..."):
        try:
            use_case = build_generate_proposal_use_case(
                top_k=top_k, llm_model=model
            )
            proposals = use_case.execute(query)
        except Exception as exc:
            st.error(f"No se pudo generar la propuesta: {exc}")
            st.stop()

    if not proposals:
        st.warning("No se encontraron propuestas para esa solicitud.")
    else:
        _assign_ids(proposals)
        st.session_state.proposals = {p.proposal_id: p for p in proposals}
        st.session_state.documents = {p.proposal_id: None for p in proposals}
        st.session_state.log = []
        for proposal in proposals:
            _render_proposal(proposal, proposal.proposal_id)
        st.success("Propuestas guardadas automáticamente.")

elif generate:
    st.info("Escribe la necesidad del cliente antes de generar.")
else:
    for pid, proposal in st.session_state.proposals.items():
        parent_doc = st.session_state.documents.get(pid)
        _render_proposal(proposal, pid, parent_doc)

    if st.session_state.log:
        with st.expander("Bitácora de refinamientos", expanded=False):
            for pid, action, entries in st.session_state.log:
                st.markdown(f"**{pid} — {action}**")
                for entry in entries:
                    st.caption(
                        f"- {entry.action} | afectado: {entry.affected_product or '—'} "
                        f"| nuevo: {entry.new_product or '—'} | {entry.result}"
                    )
