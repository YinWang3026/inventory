"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyChoice
from service.models import Inventory


class InventoryFactory(factory.Factory):
    """Creates fake inventory for testing"""

    class Meta:
        model = Inventory

    id = factory.Sequence(lambda n: n)
    name = FuzzyChoice(choices=["chocolate", "noodle", "fan", "computer", "speaker", "pencil"])
    quantity = factory.Faker("random_int")
