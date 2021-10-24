"""
Test cases for Inventory Model

Test cases can be run with:
    nosetests
    coverage report -m

"""
from datetime import date
import os
import logging
import unittest
from werkzeug.exceptions import NotFound
from service.models import Inventory, DataValidationError, db
from service import app
from .factories import InventoryFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI",
    "postgres://postgres:postgres@localhost:5432/postgres"
)

######################################################################
#  I N V E N T O R Y   M O D E L   T E S T   C A S E S
######################################################################
class TestInventoryModel(unittest.TestCase):
    """Test Cases for Inventory Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Inventory.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.drop_all()  # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()
        db.drop_all()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_an_inventory(self):
        """Create an inventory and assert that it exists"""
        inv = inventory(name="paper", quantity=100)
        self.assertTrue(inv != None)
        self.assertEqual(inv.id, None)
        self.assertEqual(inv.name, "paper")
        self.assertEqual(inv.quantity, 100)

    def test_add_an_inventory(self):
        """Create an inventory and add it to the database"""
        inv = Inventory.all()
        self.assertEqual(inv, [])
        inv = inventory(name="paper", quantity=100)
        self.assertTrue(inv != None)
        self.assertEqual(inv.id, None)
        inv.create()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(inv.id, 1)
        invs = Inventory.all()
        self.assertEqual(len(invs), 1)
    
    def test_serialize(self):
        """Test serialization of an item"""
        inventory = InventoryFactory()
        data = inventory.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], inventory.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], inventory.name)
        self.assertIn("quantity", data)
        self.assertEqual(data["quantity"], inventory.quantity)

    def test_deserialize(self):
        """Test deserialization of an item"""
        data = {
            "id": 1,
            "name": "flower",
            "quantity": 13,
        }
        inventory = Inventory
        inventory.deserialize(data)
        self.assertNotEqual(inventory, None)
        self.assertEqual(inventory.id, None)
        self.assertEqual(inventory.name, "flower")
        self.assertEqual(inventory.quantity, 13)
    
    def test_deserialize_missing_data(self):
        """Test deserialization of a Inventory with missing data"""
        data = {"id": 1, "name": "kitty", "category": "cat"}
        inv = Inventory()
        self.assertRaises(DataValidationError, inv.deserialize, data)

    def test_deserialize_bad_data(self):
        """Test deserialization of bad data"""
        data = "this is not a dictionary"
        inv = Inventory()
        self.assertRaises(DataValidationError, inv.deserialize, data)

    def test_deserialize_bad_available(self):
        """ Test deserialization of bad available attribute """
        test_inv = InventoryFactory()
        data = test_inv.serialize()
        data["available"] = "true"
        inv = Inventory()
        self.assertRaises(DataValidationError, inv.deserialize, data)

    def test_deserialize_bad_gender(self):
        """ Test deserialization of bad gender attribute """
        test_inv = InventoryFactory()
        data = test_inv.serialize()
        data["gender"] = "male" # wrong case
        inv = Inventory()
        self.assertRaises(DataValidationError, inv.deserialize, data)

    def test_find_pet(self):
        """Find a Pet by ID"""
        pets = PetFactory.create_batch(3)
        for pet in pets:
            pet.create()
        logging.debug(pets)
        # make sure they got saved
        self.assertEqual(len(Pet.all()), 3)
        # find the 2nd pet in the list
        pet = Pet.find(pets[1].id)
        self.assertIsNot(pet, None)
        self.assertEqual(pet.id, pets[1].id)
        self.assertEqual(pet.name, pets[1].name)
        self.assertEqual(pet.available, pets[1].available)