import streamlit as st

from ....domain.models.catalog_product import CatalogProduct
from ..search_catalog.ui import render_product_card_html, SC_CARD_CSS


def _price_fmt(price: float, currency: str) -> str:
    if currency == "COP":
        return f"$ {price:,.0f}"
    return f"{price:,.2f} {currency}"


DISCOVERY_CSS = """
<style>
/* ── header ── */
.sc-disc-header {
    text-align: center;
    padding: 4px 0 14px;
}
.sc-disc-title {
    font-size: 22px;
    font-weight: 800;
    color: #F1F5F9;
}
.sc-disc-sub {
    font-size: 13px;
    color: #64748B;
    margin-top: 2px;
}

/* ── collection grid ── */
.sc-disc-grid {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 16px;
}
.sc-disc-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
    padding: 12px 14px;
    display: flex;
    align-items: center;
    gap: 12px;
    transition: border-color 0.12s ease;
}
.sc-disc-card:hover {
    border-color: #475569;
}
.sc-disc-icon {
    font-size: 26px;
    flex-shrink: 0;
    width: 40px;
    text-align: center;
}
.sc-disc-info {
    flex: 1;
    min-width: 0;
}
.sc-disc-name {
    font-weight: 700;
    font-size: 14px;
    color: #F1F5F9;
}
.sc-disc-desc {
    font-size: 11px;
    color: #64748B;
    margin-top: 1px;
}
.sc-disc-stats {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-top: 4px;
}
.sc-disc-stat {
    font-size: 10px;
    color: #94A3B8;
    background: #0F172A;
    padding: 1px 7px;
    border-radius: 5px;
    white-space: nowrap;
}
.sc-disc-btn {
    background: #312E81;
    color: #A5B4FC;
    border: none;
    border-radius: 8px;
    padding: 6px 16px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    flex-shrink: 0;
    transition: background 0.12s ease;
}
.sc-disc-btn:hover {
    background: #4338CA;
    color: #FFFFFF;
}

/* ── detail ── */
.sc-back-btn {
    font-size: 13px;
    color: #A5B4FC;
    font-weight: 500;
    cursor: pointer;
    background: none;
    border: none;
    padding: 0;
    margin-bottom: 8px;
}
.sc-detail-header {
    margin-bottom: 14px;
}
.sc-detail-title {
    font-size: 20px;
    font-weight: 700;
    color: #F1F5F9;
}
.sc-detail-stats {
    font-size: 12px;
    color: #64748B;
    margin-top: 2px;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
}
</style>
"""


def render_collections_grid(collections: list[dict]):
    st.markdown(SC_CARD_CSS + DISCOVERY_CSS, unsafe_allow_html=True)

    st.markdown(
        "<div class='sc-disc-header'>"
        "<div class='sc-disc-title'>Explorar colecciones</div>"
        "<div class='sc-disc-sub'>Descubre productos seleccionados del catalogo</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    for col in collections:
        key = col["key"]

        st.markdown(
            f"<div class='sc-disc-card'>"
            f"<div class='sc-disc-icon'>{col['icon']}</div>"
            f"<div class='sc-disc-info'>"
            f"<div class='sc-disc-name'>{col['title']}</div>"
            f"<div class='sc-disc-desc'>{col['description']}</div>"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        if st.button(
            f"Explorar {col['title']}",
            key=f"disc_btn_{key}",
            use_container_width=True,
        ):
            return key

    return None


def render_collection_detail(
    collection_title: str,
    products: list[CatalogProduct],
    summary: dict,
) -> None:
    st.markdown(SC_CARD_CSS + DISCOVERY_CSS, unsafe_allow_html=True)

    if st.button("\u2190 Volver a colecciones", key="disc_back"):
        st.session_state.sc_discovery_collection = None
        st.rerun()

    avg_str = _price_fmt(summary["avg_price"], "COP") if summary.get("avg_price") else "-"
    st.markdown(
        f"<div class='sc-detail-header'>"
        f"<div class='sc-detail-title'>{collection_title}</div>"
        f"<div class='sc-detail-stats'>"
        f"<span>{summary['count']} productos</span>"
        f"<span>Prom. {avg_str}</span>"
        f"<span>Cat: {summary['top_category']}</span>"
        f"<span>Mat: {summary['top_material']}</span>"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='sc-card-grid'>", unsafe_allow_html=True)
    for product in products:
        st.markdown(render_product_card_html(product), unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
