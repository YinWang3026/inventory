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

    
    def test_serialize(self):
        """Test serialization of an item"""
        inventory = InventoryFactory()
        data = inventory.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], inventory.prod_Id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], inventory.prod_Name)
        self.assertIn("available", data)
        self.assertEqual(data["available"], inventory.available)
        self.assertIn("quantity", data)
        self.assertEqual(data["quantity"], inventory.quantity)

    def test_deserialize(self):
        """Test deserialization of an item"""
        data = {
            "id": 1,
            "name": "flower",
            "available": True,
            "quantity": 13,
        }
        inventory = Inventory
        inventory.deserialize(data)
        self.assertNotEqual(inventory, None)
        self.assertEqual(inventory.prod_Id, None)
        self.assertEqual(inventory.prod_Name, "flower")
        self.assertEqual(inventory.available, True)
        self.assertEqual(inventory.quantity, 13)