from dataclasses import dataclass
from typing import Optional


@dataclass
class CommercialPrice:
    original_price: float = 0.0
    discount_percentage: float = 0.0
    discount_amount: float = 0.0
    discounted_price: float = 0.0
    vat_percentage: float = 0.0
    vat_amount: float = 0.0
    final_price: float = 0.0
    is_net_price: bool = False
    currency: str = "COP"
