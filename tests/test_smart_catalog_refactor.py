import unittest

from smart_catalog.commercial_knowledge.discovery import get_commercial_collections
from smart_catalog.commercial_knowledge.service import CommercialKnowledgeService
from smart_catalog.domain.models.catalog_product import CatalogProduct
from smart_catalog.presentation.slices.discovery.service import DiscoveryService


class CommercialKnowledgeServiceTest(unittest.TestCase):
    def test_falls_back_to_rule_based_knowledge_without_store(self):
        service = CommercialKnowledgeService()
        product = CatalogProduct(
            reference="TE-001",
            name="Puerto USB Ejecutivo",
            category="Tecnologia",
            price=25000,
        )

        knowledge = service.get_knowledge(product)

        self.assertEqual(knowledge.product_reference, "TE-001")
        self.assertGreater(knowledge.confidence, 0)


class DiscoveryServiceTest(unittest.TestCase):
    def test_accepts_extra_collections_without_presentation_wiring(self):
        service = DiscoveryService(extra_collections=get_commercial_collections())

        keys = {collection["key"] for collection in service.get_collections()}

        self.assertIn("ecologicos", keys)
        self.assertIn("para_ejecutivos", keys)


if __name__ == "__main__":
    unittest.main()
