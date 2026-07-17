import streamlit as st

from ....domain.models.catalog_product import CatalogProduct
from ....domain.models.catalog_search_result import CatalogSearchResult
from ....domain.models.search_response import SearchResponse
from ....shared.commercial_price_calculator import calculate as calc_price

SC_CARD_CSS = """
<style>
.sc-result-count {
    font-size: 13px;
    color: #6B7280;
    margin-bottom: 20px;
    text-align: center;
}
.sc-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 16px;
    display: flex;
    gap: 16px;
    transition: box-shadow 0.15s ease;
}
.sc-card:hover {
    box-shadow: 0 4px 12px rgba(0,0,0,0.06);
}
.sc-card-img {
    width: 120px;
    height: 120px;
    object-fit: contain;
    border-radius: 10px;
    background: #F9FAFB;
    flex-shrink: 0;
}
.sc-card-img-placeholder {
    width: 120px;
    height: 120px;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #9CA3AF;
    font-size: 11px;
    background: #F9FAFB;
    flex-shrink: 0;
}
.sc-card-body {
    flex: 1;
    min-width: 0;
}
.sc-card-name {
    font-weight: 600;
    font-size: 15px;
    color: #111827;
    line-height: 1.3;
    margin-bottom: 4px;
}
.sc-card-ref {
    font-size: 12px;
    color: #9CA3AF;
    margin-bottom: 6px;
}
.sc-price-block {
    margin: 8px 0;
}
.sc-price-original {
    font-size: 13px;
    color: #9CA3AF;
    text-decoration: line-through;
}
.sc-price-discounted {
    font-size: 14px;
    color: #6B7280;
    margin-top: 1px;
}
.sc-price-final {
    font-weight: 700;
    font-size: 20px;
    color: #059669;
    margin-top: 2px;
}
.sc-price-net {
    font-weight: 700;
    font-size: 20px;
    color: #059669;
    margin-top: 2px;
}
.sc-price-badge {
    display: inline-block;
    font-size: 10px;
    font-weight: 700;
    padding: 1px 6px;
    border-radius: 4px;
    margin-right: 4px;
}
.sc-badge-catalog {
    background: #F3F4F6;
    color: #6B7280;
}
.sc-badge-discount {
    background: #FEF2F2;
    color: #DC2626;
}
.sc-badge-vat {
    background: #ECFDF5;
    color: #059669;
}
.sc-badge-net {
    background: #EEF2FF;
    color: #4F46E5;
}
.sc-card-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-bottom: 6px;
}
.sc-badge {
    display: inline-block;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 10px;
    border-radius: 999px;
    white-space: nowrap;
}
.sc-badge-cat {
    background: #EEF2FF;
    color: #4F46E5;
}
.sc-badge-eco {
    background: #ECFDF5;
    color: #059669;
}
.sc-badge-premium {
    background: #FFFBEB;
    color: #D97706;
}
.sc-chip {
    display: inline-block;
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 6px;
    background: #F3F4F6;
    color: #6B7280;
    white-space: nowrap;
}
.sc-card-score {
    font-size: 11px;
    color: #9CA3AF;
    margin-top: 6px;
}
.sc-explanation {
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid #F3F4F6;
}
.sc-explanation-summary {
    font-size: 12px;
    font-weight: 600;
    color: #4F46E5;
    margin-bottom: 6px;
}
.sc-explanation-label {
    font-size: 11px;
    color: #9CA3AF;
    margin-bottom: 4px;
}
.sc-explain-chip {
    display: inline-block;
    font-size: 10px;
    padding: 2px 8px;
    border-radius: 6px;
    background: #EEF2FF;
    color: #4F46E5;
    white-space: nowrap;
    margin: 1px 2px;
}
.sc-explain-chip-eco {
    background: #ECFDF5;
    color: #059669;
}
.sc-explain-chip-premium {
    background: #FFFBEB;
    color: #D97706;
}
.sc-explain-chip-price {
    background: #FEF2F2;
    color: #DC2626;
}
</style>
"""


def _price_fmt(price: float, currency: str) -> str:
    if currency == "COP":
        return f"$ {price:,.0f}"
    return f"{price:,.2f} {currency}"


def render_price_block(product: CatalogProduct) -> str:
    cp = calc_price(product)
    if cp.is_net_price:
        return (
            f"<div class='sc-price-block'>"
            f"<div><span class='sc-badge sc-badge-net'>PRECIO NETO</span></div>"
            f"<div class='sc-price-net'>{_price_fmt(cp.final_price, cp.currency)}</div>"
            f"</div>"
        )

    return (
        f"<div class='sc-price-block'>"
        f"<div>"
        f"<span class='sc-badge sc-badge-catalog'>CATÁLOGO</span>"
        f"<span class='sc-price-original'>{_price_fmt(cp.original_price, cp.currency)}</span>"
        f"</div>"
        f"<div>"
        f"<span class='sc-badge sc-badge-discount'>-{cp.discount_percentage:.0f}%</span>"
        f"<span class='sc-price-discounted'>{_price_fmt(cp.discounted_price, cp.currency)}</span>"
        f"</div>"
        f"<div>"
        f"<span class='sc-badge sc-badge-vat'>FINAL + IVA</span>"
        f"<span class='sc-price-final'>{_price_fmt(cp.final_price, cp.currency)}</span>"
        f"</div>"
        f"</div>"
    )


def _render_explanation(result: CatalogSearchResult) -> None:
    exp = result.explanation
    if not exp or not exp.summary:
        return

    st.markdown(
        f"<div class='sc-explanation'>"
        f"<div class='sc-explanation-label'>¿Por que aparece este resultado?</div>"
        f"<div class='sc-explanation-summary'>{exp.summary}</div>",
        unsafe_allow_html=True,
    )

    chips = ""

    for mat in exp.matched_materials:
        chips += f"<span class='sc-explain-chip'>Material: {mat.lower()}</span>"

    for cat in exp.matched_categories:
        chips += f"<span class='sc-explain-chip'>Categoria: {cat}</span>"

    if exp.matched_eco_intent:
        chips += f"<span class='sc-explain-chip sc-explain-chip-eco'>Eco</span>"

    if exp.matched_quality_intent:
        chips += f"<span class='sc-explain-chip sc-explain-chip-premium'>Premium</span>"

    if exp.matched_price_intent == "LOW_PRICE":
        chips += f"<span class='sc-explain-chip sc-explain-chip-price'>Bajo precio</span>"
    elif exp.matched_price_intent == "HIGH_PRICE":
        chips += f"<span class='sc-explain-chip sc-explain-chip-premium'>Alto precio</span>"

    for color in exp.matched_colors:
        chips += f"<span class='sc-explain-chip'>Color: {color.lower()}</span>"

    if chips:
        st.markdown(
            f"<div class='sc-card-tags'>{chips}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)


def _render_product_card(product: CatalogProduct, score: float) -> None:
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


def render_results(response: SearchResponse) -> None:
    st.markdown(SC_CARD_CSS, unsafe_allow_html=True)

    if not response.results:
        st.markdown(
            "<div style='text-align:center;padding:80px 20px;'>"
            "<div style='font-size:14px;color:#9CA3AF;'>"
            "No encontramos productos relacionados."
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        return

    elapsed = response.metadata.processing_time_ms if response.metadata else 0
    st.markdown(
        f"<div class='sc-result-count'>"
        f"{response.total_results} resultados encontrados "
        f"({elapsed:.0f}ms)"
        f"</div>",
        unsafe_allow_html=True,
    )

    for result in response.results:
        _render_product_card(result.product, result.relevance_score)
        _render_explanation(result)
