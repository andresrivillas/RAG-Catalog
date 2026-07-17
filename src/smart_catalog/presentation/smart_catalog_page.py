import streamlit as st

from .slices.search_catalog.ui import render_results
from .slices.query_understanding.service import QueryUnderstandingService
from .slices.conversation_context.service import ConversationContextService
from .slices.discovery.service import DiscoveryService
from .slices.discovery.ui import render_collections_grid, render_collection_detail
from ..container import build_search_catalog_service


def inject_smart_catalog_styles():
    st.markdown(
        """
<style>
.sc-header {
    text-align: center;
    padding: 24px 20px 16px;
}
.sc-title {
    font-size: 30px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 6px;
    letter-spacing: -0.02em;
}
.sc-subtitle {
    font-size: 14px;
    color: #6B7280;
    line-height: 1.5;
    max-width: 400px;
    margin: 0 auto;
}
.sc-tabs {
    display: flex;
    gap: 4px;
    padding: 4px;
    background: #F3F4F6;
    border-radius: 10px;
    max-width: 320px;
    margin: 16px auto 24px;
}
.sc-tab {
    flex: 1;
    text-align: center;
    padding: 6px 16px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    border: none;
    background: transparent;
    color: #6B7280;
    transition: all 0.15s ease;
}
.sc-tab.active {
    background: #FFFFFF;
    color: #111827;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.sc-tab:hover:not(.active) {
    color: #374151;
}
.sc-search-container {
    max-width: 640px;
    margin: 0 auto 16px;
}
.sc-empty-state {
    text-align: center;
    padding: 100px 20px;
}
.sc-empty-text {
    font-size: 14px;
    color: #9CA3AF;
    line-height: 1.6;
}
.sc-error {
    text-align: center;
    padding: 40px 20px;
    color: #DC2626;
    font-size: 14px;
}
.sc-context-bar {
    max-width: 640px;
    margin: 0 auto 20px;
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
}
.sc-context-label {
    font-size: 12px;
    color: #6B7280;
    font-weight: 500;
}
.sc-context-chip {
    display: inline-block;
    font-size: 11px;
    padding: 3px 10px;
    border-radius: 999px;
    font-weight: 600;
    white-space: nowrap;
}
.sc-chip-product {
    background: #EEF2FF;
    color: #4F46E5;
}
.sc-chip-material {
    background: #ECFDF5;
    color: #059669;
}
.sc-chip-category {
    background: #F3F4F6;
    color: #374151;
}
.sc-chip-eco {
    background: #D1FAE5;
    color: #065F46;
}
.sc-chip-quality {
    background: #FFFBEB;
    color: #D97706;
}
.sc-chip-price-low {
    background: #FEF2F2;
    color: #DC2626;
}
.sc-chip-price-high {
    background: #FFFBEB;
    color: #D97706;
}
.sc-chip-color {
    background: #F3E8FF;
    color: #7C3AED;
}
.sc-history-section {
    max-width: 640px;
    margin: 0 auto 20px;
}
</style>
""",
        unsafe_allow_html=True,
    )


def _render_tabs(active_tab: str) -> str:
    tab1, tab2 = st.columns([1, 1])
    with tab1:
        if st.button(
            "Buscar",
            use_container_width=True,
            type="primary" if active_tab == "search" else "secondary",
            key="sc_tab_search",
        ):
            st.session_state.sc_tab = "search"
            st.rerun()
    with tab2:
        if st.button(
            "Explorar",
            use_container_width=True,
            type="primary" if active_tab == "discover" else "secondary",
            key="sc_tab_discover",
        ):
            st.session_state.sc_tab = "discover"
            st.rerun()
    return active_tab


def on_search_change():
    st.session_state.sc_should_search = True


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

    html = "<div class='sc-context-bar'><span class='sc-context-label'>Contexto:</span>"
    for chip in chips_data:
        cls = type_class.get(chip["type"], "sc-chip-category")
        html += f"<span class='sc-context-chip {cls}'>{chip['label']}</span>"
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Limpiar contexto", use_container_width=True, key="sc_clear_ctx"):
            st.session_state.sc_session = ctx_service.clear_session()
            st.session_state.sc_last_query = ""
            st.session_state.sc_last_response = None
            st.session_state.sc_last_structured = None
            st.rerun()

    session = st.session_state.get("sc_session")
    if session and session.history:
        with st.expander("Busquedas recientes"):
            for entry in reversed(session.history[-10:]):
                q = entry.get("query", "")
                prev = entry.get("previous", "")
                label = q
                if prev:
                    label = f"{q} (← {prev})"
                if st.button(label, key=f"hist_{q}_{len(session.history)}"):
                    st.session_state.sc_should_search = True
                    st.session_state.sc_search_input = q
                    st.rerun()


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

    st.markdown("<div class='sc-search-container'>", unsafe_allow_html=True)

    search_col, btn_col = st.columns([5, 1])
    with search_col:
        query = st.text_input(
            "Buscar productos",
            placeholder="Ej: botilitos metálicos, lapiceros baratos, productos ecológicos...",
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
            "Aún no se ha realizado ninguna búsqueda."
            "</div>"
            "</div>",
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
    inject_smart_catalog_styles()

    st.markdown(
        "<div class='sc-header'>"
        "<div class='sc-title'>Smart Catalog</div>"
        "<div class='sc-subtitle'>Busca cualquier producto utilizando lenguaje natural.</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    active_tab = st.session_state.get("sc_tab", "search")
    _render_tabs(active_tab)

    if active_tab == "discover":
        _render_discover_mode()
    else:
        _render_search_mode()
