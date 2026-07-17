import logging
import re
import unicodedata

from ..domain.models.catalog_product import CatalogProduct
from ..domain.models.commercial_price import CommercialPrice

logger = logging.getLogger("smart_catalog.pricing")

DISCOUNT_PCT = 0.52
VAT_PCT = 0.19

NETO_PATTERNS = [
    re.compile(r"\bprecio\s+neto\b"),
    re.compile(r"\bvalor\s+neto\b"),
    re.compile(r"\bneto\b"),
]


def _normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ascii", "ignore").decode("ascii")
    return text.lower()


def is_net_price(product: CatalogProduct) -> bool:
    if product.is_net_price:
        return True
    fields = [
        product.name,
        product.description,
        *product.tags,
    ]
    for field in fields:
        normalized = _normalize(field)
        for pattern in NETO_PATTERNS:
            if pattern.search(normalized):
                logger.debug("Precio neto detectado en %s: '%s'", product.reference, field[:60])
                return True
    return False


def calculate(product: CatalogProduct) -> CommercialPrice:
    original = product.price
    currency = product.currency
    neto = is_net_price(product)

    if neto:
        result = CommercialPrice(
            original_price=original,
            discount_percentage=0.0,
            discount_amount=0.0,
            discounted_price=original,
            vat_percentage=0.0,
            vat_amount=0.0,
            final_price=original,
            is_net_price=True,
            currency=currency,
        )
        logger.debug("Precio neto: %s -> final=%.2f %s", product.reference, original, currency)
        return result

    discount_amount = original * DISCOUNT_PCT
    discounted = original - discount_amount
    vat_amount = discounted * VAT_PCT
    final = discounted + vat_amount

    result = CommercialPrice(
        original_price=original,
        discount_percentage=DISCOUNT_PCT * 100,
        discount_amount=round(discount_amount, 2),
        discounted_price=round(discounted, 2),
        vat_percentage=VAT_PCT * 100,
        vat_amount=round(vat_amount, 2),
        final_price=round(final, 2),
        is_net_price=False,
        currency=currency,
    )
    logger.debug(
        "Precio calculado: %s -> original=%.2f desc=%.0f%% final=%.2f %s",
        product.reference, original, DISCOUNT_PCT * 100, final, currency,
    )
    return result
