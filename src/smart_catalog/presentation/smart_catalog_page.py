import streamlit as st

from .slices.search_catalog.ui import render_results
from .slices.query_understanding.service import QueryUnderstandingService
from .slices.conversation_context.service import ConversationContextService
from .slices.discovery.service import DiscoveryService
from .slices.discovery.ui import render_collections_grid, render_collection_detail
from ..container import build_search_catalog_service

SC_GLOBAL_CSS = """
<style>
/* ── dark theme base ── */
.stApp, [data-testid="stAppViewContainer"],
[data-testid="stHeader"], [data-testid="stToolbar"],
section[data-testid="stSidebar"] .stSidebarContent,
.main > div {
    background: #0F172A !important;
}
section[data-testid="stSidebar"] .stSidebarContent {
    border-right: 1px solid #1E293B;
}

/* ── header ── */
.sc-header {
    text-align: center;
    padding: 20px 16px 10px;
}
.sc-title {
    font-size: 28px;
    font-weight: 800;
    color: #F1F5F9;
    letter-spacing: -0.03em;
    line-height: 1.2;
}
.sc-subtitle {
    font-size: 13px;
    color: #64748B;
    margin-top: 4px;
    max-width: 360px;
    margin-left: auto;
    margin-right: auto;
}

/* ── tab bar ── */
.sc-tab-bar {
    display: flex;
    gap: 2px;
    padding: 3px;
    background: #1E293B;
    border-radius: 8px;
    max-width: 240px;
    margin: 12px auto 14px;
}

/* ── search ── */
.sc-search-wrap {
    max-width: 600px;
    margin: 0 auto 10px;
}
.sc-search-box {
    display: flex;
    gap: 0;
    border: 1.5px solid #334155;
    border-radius: 10px;
    overflow: hidden;
    background: #1E293B;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}
.sc-search-box:focus-within {
    border-color: #6366F1;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15);
}
.sc-search-box [data-testid="stTextInput"] {
    flex: 1;
}
.sc-search-box [data-testid="stTextInput"] input {
    background: transparent !important;
    border: none !important;
    color: #F1F5F9 !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    box-shadow: none !important;
}
.sc-search-box [data-testid="stTextInput"] input::placeholder {
    color: #64748B !important;
}
.sc-search-btn {
    background: #6366F1;
    color: #FFFFFF;
    border: none;
    padding: 0 18px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.15s ease;
}
.sc-search-btn:hover {
    background: #4F46E5;
}
.sc-examples {
    display: flex;
    gap: 6px;
    justify-content: center;
    flex-wrap: wrap;
    margin-top: 6px;
    margin-bottom: 2px;
}
.sc-example-chip {
    font-size: 11px;
    color: #64748B;
    background: #1E293B;
    padding: 3px 10px;
    border-radius: 6px;
    cursor: pointer;
    border: 1px solid #334155;
    transition: border-color 0.1s ease;
}
.sc-example-chip:hover {
    border-color: #6366F1;
}

/* ── context ── */
.sc-context-section {
    max-width: 600px;
    margin: 0 auto 10px;
}
.sc-context-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 6px;
}
.sc-context-label {
    font-size: 11px;
    font-weight: 600;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.sc-context-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
}
.sc-context-chip {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 999px;
    white-space: nowrap;
}
.sc-context-chip .x {
    font-size: 13px;
    line-height: 1;
    cursor: pointer;
    opacity: 0.5;
    margin-left: 2px;
}
.sc-context-chip .x:hover { opacity: 1; }
.sc-chip-product { background: #312E81; color: #A5B4FC; }
.sc-chip-material { background: #064E3B; color: #6EE7B7; }
.sc-chip-category { background: #334155; color: #94A3B8; }
.sc-chip-eco { background: #064E3B; color: #6EE7B7; }
.sc-chip-quality { background: #78350F; color: #FCD34D; }
.sc-chip-price-low { background: #7F1D1D; color: #FCA5A5; }
.sc-chip-price-high { background: #78350F; color: #FCD34D; }
.sc-chip-color { background: #312E81; color: #A5B4FC; }
.sc-clear-btn {
    font-size: 11px;
    color: #FCA5A5;
    background: none;
    border: 1px solid #7F1D1D;
    border-radius: 6px;
    padding: 2px 10px;
    cursor: pointer;
    transition: background 0.1s ease;
}
.sc-clear-btn:hover { background: #7F1D1D; }

/* ── history ── */
.sc-history-section {
    max-width: 600px;
    margin: 0 auto 10px;
}

/* ── streamlit overrides for dark theme ── */
[data-testid="stTextInput"] { flex: 1; }
[data-testid="stMarkdownContainer"] p { margin: 0; }
.stButton button[kind="secondary"] {
    background: transparent !important;
    color: #94A3B8 !important;
    border: 1px solid #334155 !important;
}
.stButton button[kind="primary"] {
    background: #6366F1 !important;
    color: #FFFFFF !important;
    border: none !important;
}
.stButton button:hover {
    filter: brightness(1.1);
}
.streamlit-expanderHeader {
    color: #94A3B8 !important;
    font-size: 12px !important;
}
[data-testid="stSpinner"] {
    color: #A5B4FC !important;
}

/* ── states ── */
.sc-empty-state {
    text-align: center;
    padding: 64px 20px;
}
.sc-empty-text {
    font-size: 14px;
    color: #64748B;
    line-height: 1.6;
}
.sc-error {
    text-align: center;
    padding: 32px 20px;
    color: #FCA5A5;
    font-size: 14px;
}
</style>
"""

EXAMPLE_QUERIES = [
    "botilitos metálicos",
    "regalos ecológicos",
    "termos premium",
    "lapiceros baratos",
]


def on_search_change():
    st.session_state.sc_should_search = True


def _render_tabs(active_tab: str) -> str:
    st.markdown("<div class='sc-tab-bar'>", unsafe_allow_html=True)
    cols = st.columns(2)
    with cols[0]:
        if st.button(
            "Buscar",
            use_container_width=True,
            type="primary" if active_tab == "search" else "secondary",
            key="sc_tab_search",
        ):
            st.session_state.sc_tab = "search"
            st.rerun()
    with cols[1]:
        if st.button(
            "Explorar",
            use_container_width=True,
            type="primary" if active_tab == "discover" else "secondary",
            key="sc_tab_discover",
        ):
            st.session_state.sc_tab = "discover"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    return active_tab


def render_context_chips(ctx_service: ConversationContextService):
    session = st.session_state.get("sc_session")
    if not session or not session.current_structured:
        return

    chips_data = ctx_service.get_context_chips(session.current_structured)
    if not chips_data:
        return

    type_class = {
        "product": "sc-chip-product",
        "material": "sc-chip-material",
        "category": "sc-chip-category",
        "eco": "sc-chip-eco",
        "quality": "sc-chip-quality",
        "price_low": "sc-chip-price-low",
        "price_high": "sc-chip-price-high",
        "color": "sc-chip-color",
    }

    st.markdown("<div class='sc-context-section'>", unsafe_allow_html=True)
    st.markdown(
        "<div class='sc-context-header'>"
        "<span class='sc-context-label'>Filtros activos</span>",
        unsafe_allow_html=True,
    )

    if st.button("Limpiar", key="sc_clear_ctx", help="Limpiar todos los filtros"):
        st.session_state.sc_session = ctx_service.clear_session()
        st.session_state.sc_last_query = ""
        st.session_state.sc_last_response = None
        st.session_state.sc_last_structured = None
        st.rerun()

    html = "<div class='sc-context-chips'>"
    for i, chip in enumerate(chips_data):
        cls = type_class.get(chip["type"], "sc-chip-category")
        html += (
            f"<span class='sc-context-chip {cls}'>"
            f"{chip['label']}<span class='x'>\u2715</span>"
            f"</span>"
        )
    html += "</div></div>"
    st.markdown(html, unsafe_allow_html=True)

    with st.expander("Busquedas recientes", expanded=False):
        session = st.session_state.get("sc_session")
        if session and session.history:
            html = "<div style='display:flex;flex-wrap:wrap;gap:6px;'>"
            for entry in reversed(session.history[-8:]):
                q = entry.get("query", "")
                html += (
                    f"<span style='font-size:12px;color:#A5B4FC;background:#312E81;"
                    f"padding:4px 12px;border-radius:8px;cursor:pointer;"
                    f"border:1px solid #4338CA;'>{q}</span>"
                )
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)


def _render_discover_mode():
    discovery = DiscoveryService()
    active_collection = st.session_state.get("sc_discovery_collection")

    if active_collection:
        with st.spinner("Cargando coleccion..."):
            products, summary = discovery.load_collection(active_collection)
            collections = {c["key"]: c for c in discovery.get_collections()}
            info = collections.get(active_collection, {})
            render_collection_detail(
                info.get("title", active_collection),
                products,
                summary,
            )
    else:
        collections = discovery.get_collections()
        selected = render_collections_grid(collections)
        if selected:
            st.session_state.sc_discovery_collection = selected
            st.rerun()


def _render_search_mode():
    ctx_service = ConversationContextService()

    if "sc_session" not in st.session_state:
        st.session_state.sc_session = ctx_service.clear_session()

    st.markdown("<div class='sc-search-wrap'>", unsafe_allow_html=True)
    st.markdown("<div class='sc-search-box'>", unsafe_allow_html=True)

    search_col, btn_col = st.columns([5, 1.2])
    with search_col:
        query = st.text_input(
            "Buscar productos",
            placeholder="Busca productos usando lenguaje natural...",
            label_visibility="collapsed",
            key="sc_search_input",
            on_change=on_search_change,
        )
    with btn_col:
        search_clicked = st.button(
            "Buscar",
            type="primary",
            use_container_width=True,
            key="sc_search_btn",
        )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        "<div class='sc-examples'>"
        + "".join(
            f"<span class='sc-example-chip'>{ex}</span>" for ex in EXAMPLE_QUERIES
        )
        + "</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    render_context_chips(ctx_service)

    should_search = search_clicked or st.session_state.get("sc_should_search", False)

    if should_search and query:
        if st.session_state.get("sc_should_search"):
            st.session_state.sc_should_search = False
        session = st.session_state.sc_session
        resolved, session = ctx_service.resolve(query, session)
        session.current_query = resolved
        st.session_state.sc_session = session
        st.session_state.sc_last_query = resolved
        st.session_state.sc_searching = True
        st.rerun()

    is_searching = st.session_state.get("sc_searching", False)
    last_query = st.session_state.get("sc_last_query", "")

    if is_searching and last_query:
        with st.spinner("Buscando productos..."):
            try:
                query_understanding = QueryUnderstandingService()
                catalog_service = build_search_catalog_service()
                structured = query_understanding.understand(last_query)
                response = catalog_service.search(structured)
                session = st.session_state.sc_session
                session = ctx_service.update_session(
                    session, st.session_state.get("sc_search_input", last_query),
                    structured, None, response,
                )
                st.session_state.sc_session = session
                st.session_state.sc_last_response = response
                st.session_state.sc_last_structured = structured
            except Exception as exc:
                st.session_state.sc_last_error = str(exc)
                st.session_state.sc_last_response = None
            finally:
                st.session_state.sc_searching = False
                st.rerun()

    if not last_query:
        st.markdown(
            "<div class='sc-empty-state'>"
            "<div class='sc-empty-text'>"
            "Aun no se ha realizado ninguna busqueda."
            "</div></div>",
            unsafe_allow_html=True,
        )
        return

    error = st.session_state.get("sc_last_error")
    if error:
        st.markdown(
            f"<div class='sc-error'>Error: {error}</div>",
            unsafe_allow_html=True,
        )
        return

    response = st.session_state.get("sc_last_response")
    if response is not None:
        render_results(response)


def render_smart_catalog():
    st.markdown(SC_GLOBAL_CSS, unsafe_allow_html=True)

    st.markdown(
        "<div class='sc-header'>"
        "<div class='sc-title'>Smart Catalog</div>"
        "<div class='sc-subtitle'>Busca cualquier producto usando lenguaje natural</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    active_tab = st.session_state.get("sc_tab", "search")
    _render_tabs(active_tab)

    if active_tab == "discover":
        _render_discover_mode()
    else:
        _render_search_mode()
