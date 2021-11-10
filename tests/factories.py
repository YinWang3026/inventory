"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyChoice, FuzzyInteger
from service.models import Inventory, Condition

QTY_LOW = 0
QTY_HIGH = 1000

class InventoryFactory(factory.Factory):
    """Creates fake inventory for testing"""

    class Meta:
        model = Inventory

    id = factory.Sequence(lambda n: n)
    name = FuzzyChoice(choices=["chocolate", "noodle", "fan", "computer", "speaker", "pencil"])
    quantity = FuzzyInteger(QTY_LOW, QTY_HIGH) # Random value between LOW and HIGH
    restock_level = FuzzyInteger(QTY_LOW, quantity.fuzz()) # Random vaue between LOW and QUANTITY
    condition = FuzzyChoice(
        choices=[Condition.new, Condition.used, Condition.slightly_used, Condition.unknown]
    )
