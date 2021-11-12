"""
Test cases for Inventory Model

Test cases can be run with:
    nosetests
    coverage report -m

"""
# from datetime import date
# import os
import logging
import unittest
# from werkzeug.exceptions import NotFound
from service.models import Condition, Inventory, DataValidationError, db
from service import app
from .factories import InventoryFactory

from config import DATABASE_URI

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
        inv = Inventory(
            name="paper", 
            quantity=100,
            condition=Condition.new.name,
            restock_level=50
        )
        self.assertTrue(inv != None)
        self.assertEqual(inv.id, None)
        self.assertEqual(inv.name, "paper")
        self.assertEqual(inv.quantity, 100)
        self.assertEqual(inv.condition, Condition.new.name)
        self.assertEqual(inv.restock_level, 50)

    def test_add_an_inventory(self):
        """Create an inventory and add it to the database"""
        inv = Inventory.find_all()
        self.assertEqual(inv, [])
        inv = Inventory(
            name="paper", 
            quantity=100,
            condition=Condition.new.name,
            restock_level=50
        )
        self.assertTrue(inv != None)
        self.assertEqual(inv.id, None)
        inv.create()
        # Asert that it was assigned an id and shows up in the database
        self.assertEqual(inv.id, 1)
        invs = Inventory.find_all()
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
        self.assertIn("condition", data)
        self.assertEqual(data["condition"], inventory.condition.name)
        self.assertIn("restock_level", data)
        self.assertEqual(data["restock_level"], inventory.restock_level)

    def test_deserialize(self):
        """Test deserialization of an item"""
        data = {
            "id": 1,
            "name": "flower",
            "quantity": 13,
            "restock_level": 5,
            "condition": "used"
        }
        inventory = Inventory()
        inventory.deserialize(data)
        self.assertNotEqual(inventory, None)
        self.assertEqual(inventory.id, 1)
        self.assertEqual(inventory.name, "flower")
        self.assertEqual(inventory.quantity, 13)
        self.assertEqual(inventory.restock_level, 5)
        self.assertEqual(inventory.condition, Condition.used)
    
    def test_deserialize_missing_data(self):
        """Test deserialization of a Inventory with missing data"""
        data = {"id": 1, "quantity": 10} # Missing name
        inv = Inventory()
        self.assertRaises(DataValidationError, inv.deserialize, data)

    def test_deserialize_bad_data(self):
        """Test deserialization of bad data"""
        data = "this is not a dictionary"
        inv = Inventory()
        self.assertRaises(DataValidationError, inv.deserialize, data)

    def test_deserialize_bad_quantity_type(self):
        """ Test deserialization of bad quantity type """
        test_inv = InventoryFactory()
        data = test_inv.serialize()
        data["quantity"] = "10" # Bad type
        inv = Inventory()
        self.assertRaises(DataValidationError, inv.deserialize, data)

    def test_deserialize_bad_quantity_value(self):
        """ Test deserialization of bad quantity value """
        test_inv = InventoryFactory()
        data = test_inv.serialize()
        data["quantity"] = -1 # Bad value
        inv = Inventory()
        self.assertRaises(DataValidationError, inv.deserialize, data)

    def test_deserialize_bad_restock_type(self):
        """ Test deserialization of bad restock type """
        test_inv = InventoryFactory()
        data = test_inv.serialize()
        data["restock_level"] = "5" # Bad value
        inv = Inventory()
        self.assertRaises(DataValidationError, inv.deserialize, data)

    def test_deserialize_bad_restock_value(self):
        """ Test deserialization of bad restock value """
        test_inv = InventoryFactory()
        data = test_inv.serialize()
        data["restock_level"] = -1 # Bad value
        inv = Inventory()
        self.assertRaises(DataValidationError, inv.deserialize, data)

    def test_find_by_id(self):
        """Find a Inventory by ID"""
        invs = InventoryFactory.create_batch(3)
        for inv in invs:
            inv.create()
        logging.debug(invs)
        # make sure they got saved
        self.assertEqual(len(Inventory.find_all()), 3)
        # find the 2nd inv in the list
        inv = Inventory.find_by_id(invs[1].id) # Find
        self.assertIsNot(inv, None)
        self.assertEqual(inv.id, invs[1].id)
        self.assertEqual(inv.name, invs[1].name)
        self.assertEqual(inv.quantity, invs[1].quantity)
        self.assertEqual(inv.restock_level, invs[1].restock_level)
        self.assertEqual(inv.condition, invs[1].condition)

    def test_find_all(self):
        """Test if find_all returns all entires"""
        invs = InventoryFactory.create_batch(3)
        for inv in invs:
            inv.create()
        logging.debug(invs)
        # make sure they got saved
        all = Inventory.find_all()
        self.assertEqual(len(all), 3)
        # match all to invs
        all.sort(key=lambda x:x.id)
        invs.sort(key=lambda x:x.id)
        for i in range(0, 3):
            self.assertEqual(all[i].id, invs[i].id)
            self.assertEqual(all[i].name, invs[i].name)
            self.assertEqual(all[i].quantity, invs[i].quantity)
            self.assertEqual(all[i].restock_level, invs[i].restock_level)
            self.assertEqual(all[i].condition, invs[i].condition)
    
    def test_repr(self):
        """Test __repr__"""
        test_inv = InventoryFactory()
        test_rep = test_inv.__repr__()
        actual_rep = "<id=%r name=%s quantity=%d condition=%s restock_level=%d>" % \
            (test_inv.id, test_inv.name, test_inv.quantity, test_inv.condition.name, test_inv.restock_level)
        self.assertEqual(test_rep, actual_rep)
        
    def test_update_an_inventory(self):
        """Test update an Inventory"""
        inv = InventoryFactory()
        logging.debug(inv)
        inv.create()
        logging.debug(inv)
        self.assertEqual(inv.id, 1)
        # Change it and save it
        inv.quantity = 101
        inv.name = "kindle-oasis"
        inv.condition = Condition.unknown
        original_id = inv.id
        inv.update()
        self.assertEqual(inv.id, original_id)
        self.assertEqual(inv.quantity, 101)
        self.assertEqual(inv.name, "kindle-oasis")
        self.assertEqual(inv.condition, Condition.unknown)
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        invs = Inventory.find_all()
        self.assertEqual(len(invs), 1)
        self.assertEqual(invs[0].id, 1)
        self.assertEqual(invs[0].quantity, 101)
        self.assertEqual(invs[0].name, "kindle-oasis")
        self.assertEqual(invs[0].condition, Condition.unknown)

    def test_update_no_id(self):
        """Test update an Inventory without id"""
        test_inv = InventoryFactory()
        test_inv.id = None
        self.assertRaises(DataValidationError, test_inv.update)

    def test_find_by_name(self):
        """Returns all inv with the name"""
        invs = InventoryFactory.create_batch(4)
        # Change inv[0],[1] to "DevOps"
        invs[0].name = "DevOps"
        invs[1].name = "DevOps"
        # Create the invs in Inventory
        for i in range(0, len(invs)):
            invs[i].create() 
        result = Inventory.find_by_name("DevOps") # Query
        invs_list = [inv for inv in result] # Convert to list
        self.assertEqual(len(invs_list), 2) # Should get 2 items back
    
    def test_find_by_name_empty(self):
        """Test find by name does not exist"""
        result = Inventory.find_by_name("") # Query
        invs_list = [inv for inv in result] # Convert to list
        self.assertEqual(len(invs_list), 0) # Should get 0 items back

    def test_find_by_need_restock(self):
        """Returns all inv that needs restock"""
        invs = InventoryFactory.create_batch(4)
        # Change inv[0],[1] quantity to below restock_level
        # Change inv[2],[3] quantity to above restock_level
        invs[0].quantity = 5
        invs[0].restock_level = 10
        invs[1].quantity = 10
        invs[1].restock_level = 10
        invs[2].quantity = 11
        invs[2].restock_level = 10
        invs[3].quantity = 12
        invs[3].restock_level = 10
        # Create the invs in Inventory
        for i in range(0, len(invs)):
            invs[i].create() 
        result = Inventory.find_by_need_restock() # Query
        invs_list = [inv for inv in result] # Convert to list
        self.assertEqual(len(invs_list), 2) # Should get 2 items back

    def test_find_by_condition(self):
        """Returns all inv with the condition"""
        invs = InventoryFactory.create_batch(4)
        invs[0].condition = Condition.new
        invs[1].condition = Condition.slightly_used
        invs[2].condition = Condition.used
        invs[3].condition = Condition.unknown
        # Create the invs in Inventory
        for i in range(0, len(invs)):
            invs[i].create() 
        result = Inventory.find_by_condition(Condition.new) # Query
        invs_list = [inv for inv in result] # Convert to list
        self.assertEqual(len(invs_list), 1) # Should get 1 item back
        
        result = Inventory.find_by_condition(Condition.slightly_used) # Query
        invs_list = [inv for inv in result] # Convert to list
        self.assertEqual(len(invs_list), 1) # Should get 1 item back
        
        result = Inventory.find_by_condition(Condition.used) # Query
        invs_list = [inv for inv in result] # Convert to list
        self.assertEqual(len(invs_list), 1) # Should get 1 item back
        
        result = Inventory.find_by_condition(Condition.unknown) # Query
        invs_list = [inv for inv in result] # Convert to list
        self.assertEqual(len(invs_list), 1) # Should get 1 item back