from dataclasses import dataclass
from typing import Optional


@dataclass
class Money:
    amount: float
    currency: str = "COP"

    def __str__(self) -> str:
        return f"{self.amount:,.0f} {self.currency}"
