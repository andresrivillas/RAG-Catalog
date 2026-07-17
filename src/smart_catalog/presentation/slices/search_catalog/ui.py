import streamlit as st

from ....domain.models.catalog_product import CatalogProduct
from ....domain.models.catalog_search_result import CatalogSearchResult
from ....domain.models.search_response import SearchResponse
from ....shared.commercial_price_calculator import calculate as calc_price

SC_CARD_CSS = """
<style>
/* ── theme ── */
.sc-result-count {
    font-size: 12px;
    color: #94A3B8;
    margin-bottom: 14px;
    text-align: center;
}

/* ── responsive grid ── */
.sc-card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
    gap: 12px;
}

@media (min-width: 1200px) { .sc-card-grid { grid-template-columns: repeat(4, 1fr); } }
@media (min-width: 900px) and (max-width: 1199px) { .sc-card-grid { grid-template-columns: repeat(3, 1fr); } }
@media (min-width: 600px) and (max-width: 899px) { .sc-card-grid { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 599px) { .sc-card-grid { grid-template-columns: 1fr; } }

/* ── card ── */
.sc-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 12px;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
    height: 100%;
}
.sc-card:hover {
    border-color: #475569;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2);
}

/* ── image ── */
.sc-card-img-wrap {
    width: 100%;
    aspect-ratio: 1 / 1;
    background: #0F172A;
    display: flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
}
.sc-card-img-wrap img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}
.sc-card-img-placeholder {
    width: 100%;
    aspect-ratio: 1 / 1;
    background: #0F172A;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #475569;
    font-size: 12px;
}

/* ── body ── */
.sc-card-body {
    padding: 10px 12px 8px;
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 3px;
}
.sc-card-name {
    font-weight: 700;
    font-size: 13px;
    color: #F1F5F9;
    line-height: 1.35;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.sc-card-ref {
    font-size: 11px;
    color: #64748B;
}
.sc-card-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin: 2px 0;
}
.sc-badge {
    display: inline-block;
    font-size: 10px;
    font-weight: 600;
    padding: 1px 8px;
    border-radius: 999px;
    white-space: nowrap;
}
.sc-badge-cat { background: #312E81; color: #A5B4FC; }
.sc-badge-eco { background: #064E3B; color: #6EE7B7; }
.sc-badge-premium { background: #78350F; color: #FCD34D; }
.sc-chip {
    display: inline-block;
    font-size: 10px;
    padding: 1px 7px;
    border-radius: 5px;
    background: #334155;
    color: #94A3B8;
    white-space: nowrap;
}
.sc-chip-overflow {
    font-size: 10px;
    color: #64748B;
    padding: 1px 4px;
}

/* ── price ── */
.sc-price-block {
    margin: 4px 0;
    padding: 6px 8px;
    background: #0F172A;
    border-radius: 8px;
}
.sc-price-line {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
}
.sc-price-original {
    font-size: 11px;
    color: #64748B;
    text-decoration: line-through;
}
.sc-price-discounted {
    font-size: 11px;
    color: #94A3B8;
}
.sc-price-final {
    font-weight: 800;
    font-size: 18px;
    color: #34D399;
}
.sc-price-badge {
    font-size: 9px;
    font-weight: 700;
    padding: 1px 5px;
    border-radius: 3px;
}
.sc-badge-catalog { background: #334155; color: #94A3B8; }
.sc-badge-discount { background: #7F1D1D; color: #FCA5A5; }
.sc-badge-vat { background: #064E3B; color: #6EE7B7; }
.sc-badge-net { background: #78350F; color: #FCD34D; font-size: 10px; padding: 1px 8px; border-radius: 4px; display: inline-block; margin-bottom: 2px; }

/* ── explanation ── */
.sc-explain-box {
    margin-top: 6px;
    padding: 6px 8px;
    background: #0F172A;
    border-radius: 8px;
    border-left: 3px solid #6366F1;
}
.sc-explain-summary {
    font-size: 11px;
    font-weight: 600;
    color: #A5B4FC;
    margin-bottom: 3px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.sc-explain-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 3px;
}
.sc-explain-chip {
    font-size: 9px;
    padding: 1px 6px;
    border-radius: 4px;
    background: #312E81;
    color: #A5B4FC;
    white-space: nowrap;
}
.sc-explain-chip-eco { background: #064E3B; color: #6EE7B7; }
.sc-explain-chip-premium { background: #78350F; color: #FCD34D; }
.sc-explain-chip-price { background: #7F1D1D; color: #FCA5A5; }

/* ── link ── */
.sc-card-link {
    display: block;
    text-align: center;
    padding: 8px;
    margin: 8px 12px 12px;
    background: #312E81;
    color: #A5B4FC;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
    text-decoration: none;
    transition: background 0.12s ease;
    flex-shrink: 0;
}
.sc-card-link:hover {
    background: #4338CA;
    color: #FFFFFF;
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
            f"<span class='sc-badge-net'>PRECIO NETO</span>"
            f"<div class='sc-price-line' style='margin-top:4px;'>"
            f"<span class='sc-price-final'>{_price_fmt(cp.final_price, cp.currency)}</span>"
            f"</div>"
            f"</div>"
        )

    return (
        f"<div class='sc-price-block'>"
        f"<div class='sc-price-line'>"
        f"<span class='sc-badge sc-badge-catalog'>CAT</span>"
        f"<span class='sc-price-original'>{_price_fmt(cp.original_price, cp.currency)}</span>"
        f"</div>"
        f"<div class='sc-price-line'>"
        f"<span class='sc-badge sc-badge-discount'>-{cp.discount_percentage:.0f}%</span>"
        f"<span class='sc-price-discounted'>{_price_fmt(cp.discounted_price, cp.currency)}</span>"
        f"</div>"
        f"<div class='sc-price-line' style='margin-top:2px;'>"
        f"<span class='sc-badge sc-badge-vat'>FINAL</span>"
        f"<span class='sc-price-final'>{_price_fmt(cp.final_price, cp.currency)}</span>"
        f"</div>"
        f"</div>"
    )


def _render_card(product: CatalogProduct, result: CatalogSearchResult) -> str:
    exp = result.explanation

    img_html = (
        f"<img src='{product.image_url}' alt='' loading='lazy' />"
        if product.image_url
        else "<div class='sc-card-img-placeholder'>Sin imagen</div>"
    )

    badges = ""
    if product.category:
        badges += f"<span class='sc-badge sc-badge-cat'>{product.category}</span>"
    if product.eco_friendly:
        badges += "<span class='sc-badge sc-badge-eco'>Eco</span>"
    if "premium" in product.tags or "alto" in product.tags:
        badges += "<span class='sc-badge sc-badge-premium'>Premium</span>"

    mats = ""
    if product.material:
        materials = [m.strip() for m in product.material.split(",") if m.strip()]
        if materials:
            chips = "".join(
                f"<span class='sc-chip'>{m}</span>" for m in materials[:3]
            )
            if len(materials) > 3:
                chips += f"<span class='sc-chip-overflow'>+{len(materials)-3}</span>"
            mats = f"<div class='sc-card-badges'>{chips}</div>"

    explain_html = ""
    if exp and exp.summary:
        e_chips = ""
        for m in exp.matched_materials:
            e_chips += f"<span class='sc-explain-chip'>Mat: {m.lower()}</span>"
        for c in exp.matched_categories:
            e_chips += f"<span class='sc-explain-chip'>Cat: {c}</span>"
        if exp.matched_eco_intent:
            e_chips += "<span class='sc-explain-chip sc-explain-chip-eco'>Eco</span>"
        if exp.matched_quality_intent:
            e_chips += "<span class='sc-explain-chip sc-explain-chip-premium'>Prem</span>"
        if exp.matched_price_intent == "LOW_PRICE":
            e_chips += "<span class='sc-explain-chip sc-explain-chip-price'>Bajo $</span>"
        elif exp.matched_price_intent == "HIGH_PRICE":
            e_chips += "<span class='sc-explain-chip sc-explain-chip-premium'>Alto $</span>"
        for co in exp.matched_colors:
            e_chips += f"<span class='sc-explain-chip'>{co.lower()}</span>"

        explain_html = (
            f"<div class='sc-explain-box'>"
            f"<div class='sc-explain-summary'>{exp.summary}</div>"
            + (f"<div class='sc-explain-chips'>{e_chips}</div>" if e_chips else "")
            + f"</div>"
        )

    link_html = ""
    if product.detail_url:
        link_html = (
            f"<a href='{product.detail_url}' target='_blank' class='sc-card-link'>"
            f"Ver producto \u2192</a>"
        )

    return (
        f"<div class='sc-card'>"
        f"<div class='sc-card-img-wrap'>{img_html}</div>"
        f"<div class='sc-card-body'>"
        f"<div class='sc-card-name'>{product.name}</div>"
        f"<div class='sc-card-ref'>Ref: {product.reference}</div>"
        + (f"<div class='sc-card-badges'>{badges}</div>" if badges else "")
        + mats
        + render_price_block(product)
        + explain_html
        + f"</div>"
        + link_html
        + f"</div>"
    )


def render_product_card_html(product: CatalogProduct) -> str:
    img_html = (
        f"<img src='{product.image_url}' alt='' loading='lazy' />"
        if product.image_url
        else "<div class='sc-card-img-placeholder'>Sin imagen</div>"
    )
    badges = ""
    if product.category:
        badges += f"<span class='sc-badge sc-badge-cat'>{product.category}</span>"
    if product.eco_friendly:
        badges += "<span class='sc-badge sc-badge-eco'>Eco</span>"
    if "premium" in product.tags or "alto" in product.tags:
        badges += "<span class='sc-badge sc-badge-premium'>Premium</span>"
    mats = ""
    if product.material:
        materials = [m.strip() for m in product.material.split(",") if m.strip()]
        if materials:
            chips = "".join(f"<span class='sc-chip'>{m}</span>" for m in materials[:3])
            if len(materials) > 3:
                chips += f"<span class='sc-chip-overflow'>+{len(materials)-3}</span>"
            mats = f"<div class='sc-card-badges'>{chips}</div>"
    link_html = ""
    if product.detail_url:
        link_html = (
            f"<a href='{product.detail_url}' target='_blank' class='sc-card-link'>"
            f"Ver producto \u2192</a>"
        )
    return (
        f"<div class='sc-card'>"
        f"<div class='sc-card-img-wrap'>{img_html}</div>"
        f"<div class='sc-card-body'>"
        f"<div class='sc-card-name'>{product.name}</div>"
        f"<div class='sc-card-ref'>Ref: {product.reference}</div>"
        + (f"<div class='sc-card-badges'>{badges}</div>" if badges else "")
        + mats
        + render_price_block(product)
        + f"</div>"
        + link_html
        + f"</div>"
    )


def render_results(response: SearchResponse) -> None:
    st.markdown(SC_CARD_CSS, unsafe_allow_html=True)

    if not response.results:
        st.markdown(
            "<div style='text-align:center;padding:60px 20px;'>"
            "<div style='font-size:14px;color:#64748B;'>"
            "No encontramos productos relacionados.</div></div>",
            unsafe_allow_html=True,
        )
        return

    elapsed = response.metadata.processing_time_ms if response.metadata else 0
    st.markdown(
        f"<div class='sc-result-count'>"
        f"{response.total_results} resultados ({elapsed:.0f}ms)</div>",
        unsafe_allow_html=True,
    )

    cards_html = "<div class='sc-card-grid'>"
    for result in response.results:
        cards_html += _render_card(result.product, result)
    cards_html += "</div>"

    st.markdown(cards_html, unsafe_allow_html=True)
