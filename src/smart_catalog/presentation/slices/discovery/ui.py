import streamlit as st

from ....domain.models.catalog_product import CatalogProduct
from ....shared.commercial_price_calculator import calculate as calc_price
from ..search_catalog.ui import render_price_block, SC_CARD_CSS


def _price_fmt(price: float, currency: str) -> str:
    if currency == "COP":
        return f"$ {price:,.0f}"
    return f"{price:,.2f} {currency}"


DISCOVERY_CSS = """
<style>
.sc-discovery-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 24px;
}
.sc-discovery-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 14px;
    padding: 20px;
    flex: 1;
    min-width: 180px;
    cursor: pointer;
    transition: box-shadow 0.15s ease, transform 0.1s ease;
    text-align: center;
}
.sc-discovery-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    transform: translateY(-2px);
}
.sc-discovery-icon {
    font-size: 28px;
    margin-bottom: 8px;
}
.sc-discovery-title {
    font-weight: 700;
    font-size: 14px;
    color: #111827;
    margin-bottom: 4px;
}
.sc-discovery-desc {
    font-size: 11px;
    color: #6B7280;
    line-height: 1.4;
}
.sc-discovery-meta {
    font-size: 11px;
    color: #9CA3AF;
    margin-top: 8px;
    display: flex;
    gap: 8px;
    justify-content: center;
    flex-wrap: wrap;
}
.sc-discovery-meta-item {
    background: #F3F4F6;
    padding: 2px 8px;
    border-radius: 6px;
}
.sc-discovery-header {
    margin-bottom: 20px;
}
.sc-discovery-back {
    font-size: 13px;
    color: #4F46E5;
    cursor: pointer;
    margin-bottom: 16px;
    display: inline-block;
}
.sc-discovery-stats {
    font-size: 12px;
    color: #6B7280;
    margin-bottom: 16px;
}
</style>
"""


def render_collections_grid(
    collections: list[dict],
    on_select=None,
):
    st.markdown(SC_CARD_CSS + DISCOVERY_CSS, unsafe_allow_html=True)

    st.markdown(
        "<div style='text-align:center;padding:24px 0 12px;'>"
        "<div style='font-size:22px;font-weight:700;color:#111827;'>"
        "Explorar productos</div>"
        "<div style='font-size:13px;color:#6B7280;margin-top:4px;'>"
        "Descubre colecciones seleccionadas del catálogo</div>"
        "</div>",
        unsafe_allow_html=True,
    )

    for col in collections:
        key = col["key"]
        with st.container():
            col1, col2 = st.columns([1, 3])
            with col1:
                st.markdown(
                    f"<div style='font-size:32px;text-align:center;'>{col['icon']}</div>",
                    unsafe_allow_html=True,
                )
            with col2:
                st.markdown(
                    f"<div style='font-weight:700;font-size:15px;color:#111827;'>"
                    f"{col['title']}</div>",
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f"<div style='font-size:12px;color:#6B7280;'>{col['description']}</div>",
                    unsafe_allow_html=True,
                )

            if st.button(
                f"Ver {col['title']}",
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

    if st.button("← Volver a colecciones", key="disc_back"):
        st.session_state.sc_discovery_collection = None
        st.rerun()

    st.markdown(
        f"<div class='sc-discovery-header'>"
        f"<div style='font-size:22px;font-weight:700;color:#111827;'>{collection_title}</div>"
        f"<div class='sc-discovery-stats'>"
        f"{summary['count']} productos | "
        f"Precio prom: {_price_fmt(summary['avg_price'], 'COP')} | "
        f"Categoría: {summary['top_category']} | "
        f"Material: {summary['top_material']}"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    for product in products:
        _render_discovery_product_card(product)


def _render_discovery_product_card(product: CatalogProduct) -> None:
    cols = st.columns([1, 3])
    with cols[0]:
        if product.image_url:
            try:
                st.image(product.image_url, width=120)
            except Exception:
                st.markdown(
                    "<div class='sc-card-img-placeholder'>Sin imagen</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                "<div class='sc-card-img-placeholder'>Sin imagen</div>",
                unsafe_allow_html=True,
            )

    with cols[1]:
        st.markdown(
            f"<div class='sc-card-name'>{product.name}</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"<div class='sc-card-ref'>Ref: {product.reference}</div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            render_price_block(product),
            unsafe_allow_html=True,
        )

        tags_html = ""
        if product.category:
            tags_html += (
                f"<span class='sc-badge sc-badge-cat'>{product.category}</span>"
            )
        if product.eco_friendly:
            tags_html += "<span class='sc-badge sc-badge-eco'>Eco</span>"
        if "premium" in product.tags or "alto" in product.tags:
            tags_html += "<span class='sc-badge sc-badge-premium'>Premium</span>"
        if tags_html:
            st.markdown(
                f"<div class='sc-card-tags'>{tags_html}</div>",
                unsafe_allow_html=True,
            )

        if product.material:
            materials = [m.strip() for m in product.material.split(",") if m.strip()]
            if materials:
                chips = "".join(
                    f"<span class='sc-chip'>{m}</span>" for m in materials[:4]
                )
                st.markdown(
                    f"<div class='sc-card-tags'>{chips}</div>",
                    unsafe_allow_html=True,
                )

        if product.detail_url:
            st.markdown(
                f"<a href='{product.detail_url}' target='_blank' "
                f"style='display:inline-block;margin-top:8px;padding:6px 16px;"
                f"border-radius:8px;background:#4F46E5;color:#FFFFFF;"
                f"font-size:12px;font-weight:600;text-decoration:none;'>"
                f"Ver producto →</a>",
                unsafe_allow_html=True,
            )
