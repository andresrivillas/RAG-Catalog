from dataclasses import dataclass, field


@dataclass
class Evidence:
    source: str = ""
    value: str = ""
    weight: float = 0.0

    def to_dict(self) -> dict:
        return {"source": self.source, "value": self.value, "weight": self.weight}

    @staticmethod
    def from_dict(d: dict) -> "Evidence":
        return Evidence(source=d.get("source", ""), value=d.get("value", ""), weight=d.get("weight", 0.0))


@dataclass
class InferredAttribute:
    value: str = ""
    confidence: float = 0.0
    evidence: list[Evidence] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "value": self.value,
            "confidence": self.confidence,
            "evidence": [e.to_dict() for e in self.evidence],
        }

    @staticmethod
    def from_dict(d: dict) -> "InferredAttribute":
        return InferredAttribute(
            value=d.get("value", ""),
            confidence=d.get("confidence", 0.0),
            evidence=[Evidence.from_dict(e) for e in d.get("evidence", [])],
        )


@dataclass
class CatalogKnowledge:
    product_reference: str = ""
    product_family: InferredAttribute = field(default_factory=InferredAttribute)
    commercial_level: InferredAttribute = field(default_factory=InferredAttribute)
    premium_level: InferredAttribute = field(default_factory=InferredAttribute)
    executive_level: InferredAttribute = field(default_factory=InferredAttribute)
    commercial_value: InferredAttribute = field(default_factory=InferredAttribute)
    target_industries: list[InferredAttribute] = field(default_factory=list)
    target_customers: list[InferredAttribute] = field(default_factory=list)
    use_cases: list[InferredAttribute] = field(default_factory=list)
    gift_occasions: list[InferredAttribute] = field(default_factory=list)
    campaign_types: list[InferredAttribute] = field(default_factory=list)
    corporate_affinity: InferredAttribute = field(default_factory=InferredAttribute)
    innovation_level: InferredAttribute = field(default_factory=InferredAttribute)
    eco_level: InferredAttribute = field(default_factory=InferredAttribute)
    technology_level: InferredAttribute = field(default_factory=InferredAttribute)
    luxury_level: InferredAttribute = field(default_factory=InferredAttribute)
    practicality_level: InferredAttribute = field(default_factory=InferredAttribute)
    price_position: InferredAttribute = field(default_factory=InferredAttribute)
    differentiators: list[str] = field(default_factory=list)
    commercial_tags: list[str] = field(default_factory=list)
    overall_confidence: float = 0.0
    generated_from: str = "auto"
    generated_at: str = ""

    def to_dict(self) -> dict:
        return {
            "product_reference": self.product_reference,
            "product_family": self.product_family.to_dict(),
            "commercial_level": self.commercial_level.to_dict(),
            "premium_level": self.premium_level.to_dict(),
            "executive_level": self.executive_level.to_dict(),
            "commercial_value": self.commercial_value.to_dict(),
            "target_industries": [i.to_dict() for i in self.target_industries],
            "target_customers": [c.to_dict() for c in self.target_customers],
            "use_cases": [u.to_dict() for u in self.use_cases],
            "gift_occasions": [g.to_dict() for g in self.gift_occasions],
            "campaign_types": [c.to_dict() for c in self.campaign_types],
            "corporate_affinity": self.corporate_affinity.to_dict(),
            "innovation_level": self.innovation_level.to_dict(),
            "eco_level": self.eco_level.to_dict(),
            "technology_level": self.technology_level.to_dict(),
            "luxury_level": self.luxury_level.to_dict(),
            "practicality_level": self.practicality_level.to_dict(),
            "price_position": self.price_position.to_dict(),
            "differentiators": self.differentiators,
            "commercial_tags": self.commercial_tags,
            "overall_confidence": self.overall_confidence,
            "generated_from": self.generated_from,
            "generated_at": self.generated_at,
        }

    @staticmethod
    def from_dict(d: dict) -> "CatalogKnowledge":
        return CatalogKnowledge(
            product_reference=d.get("product_reference", ""),
            product_family=InferredAttribute.from_dict(d.get("product_family", {})),
            commercial_level=InferredAttribute.from_dict(d.get("commercial_level", {})),
            premium_level=InferredAttribute.from_dict(d.get("premium_level", {})),
            executive_level=InferredAttribute.from_dict(d.get("executive_level", {})),
            commercial_value=InferredAttribute.from_dict(d.get("commercial_value", {})),
            target_industries=[InferredAttribute.from_dict(i) for i in d.get("target_industries", [])],
            target_customers=[InferredAttribute.from_dict(c) for c in d.get("target_customers", [])],
            use_cases=[InferredAttribute.from_dict(u) for u in d.get("use_cases", [])],
            gift_occasions=[InferredAttribute.from_dict(g) for g in d.get("gift_occasions", [])],
            campaign_types=[InferredAttribute.from_dict(c) for c in d.get("campaign_types", [])],
            corporate_affinity=InferredAttribute.from_dict(d.get("corporate_affinity", {})),
            innovation_level=InferredAttribute.from_dict(d.get("innovation_level", {})),
            eco_level=InferredAttribute.from_dict(d.get("eco_level", {})),
            technology_level=InferredAttribute.from_dict(d.get("technology_level", {})),
            luxury_level=InferredAttribute.from_dict(d.get("luxury_level", {})),
            practicality_level=InferredAttribute.from_dict(d.get("practicality_level", {})),
            price_position=InferredAttribute.from_dict(d.get("price_position", {})),
            differentiators=d.get("differentiators", []),
            commercial_tags=d.get("commercial_tags", []),
            overall_confidence=d.get("overall_confidence", 0.0),
            generated_from=d.get("generated_from", "auto"),
            generated_at=d.get("generated_at", ""),
        )
