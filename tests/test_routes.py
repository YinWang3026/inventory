"""
Inventory API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN

"""

# import os
import logging
import unittest

from urllib.parse import quote_plus
from service import status  # HTTP Status Codes
from service.models import db, init_db
from service.routes import app
from .factories import InventoryFactory

from config import DATABASE_URI

# Disable all but ciritcal errors during normal test run
# uncomment for debugging failing tests
logging.disable(logging.CRITICAL)

BASE_URL = "/inventory"
CONTENT_TYPE_JSON = "application/json"

######################################################################
#  T E S T   C A S E S
######################################################################
class TestInventoryServer(unittest.TestCase):
	"""Inventory Server Tests"""
	
	@classmethod
	def setUpClass(cls):
		"""Run once before all tests"""
		app.config["TESTING"] = True
		app.config["DEBUG"] = False
		# Set up the test database
		app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
		app.logger.setLevel(logging.CRITICAL)
		init_db(app)

	@classmethod
	def tearDownClass(cls):
		"""Run once after all tests"""
		db.session.close()
	
	def setUp(self):
		"""Runs before each test"""
		db.drop_all()  # clean up the last tests
		db.create_all()  # create new tables
		self.app = app.test_client()

	def tearDown(self):
		db.session.remove()
		db.drop_all()
	
	def _create_invs(self, count):
		"""
		Factory method to create invs in database in bulk
		Returns the created inventory in a list
		"""
		invs = []
		for _ in range(count):
			test_inv = InventoryFactory()
			resp = self.app.post( # Created an inventory using the POST /inventory route
				BASE_URL, json=test_inv.serialize(), content_type=CONTENT_TYPE_JSON
			)
			self.assertEqual(
				resp.status_code, status.HTTP_201_CREATED, "Could not create test inv"
			)
			new_inv = resp.get_json()
			test_inv.id = new_inv["id"]
			invs.append(test_inv)
		return invs
	
	def test_index(self):
		"""Test the Home Page"""
		resp = self.app.get("/")
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
	
	def test_get_inventory(self):
		"""Get a single inventory with id"""
		# get the id of a inventory
		test_inv = self._create_invs(1)[0] # One item
		resp = self.app.get(
			"/inventory/{}".format(test_inv.id), content_type=CONTENT_TYPE_JSON
		)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		data = resp.get_json()
		self.assertEqual(data["id"], test_inv.id)
		self.assertEqual(data["name"], test_inv.name)
		self.assertEqual(data["quantity"], test_inv.quantity)
		self.assertEqual(data["condition"], test_inv.condition.name)
		self.assertEqual(data["restock_level"], test_inv.restock_level)

	def test_get_inventory_not_found(self):
		"""Get a Inventory thats not found"""
		resp = self.app.get("/inventory/0")
		self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

	def test_create_inventory(self):
		"""Create a new Inventory"""
		test_inv = InventoryFactory()
		test_inv.id = None
		logging.debug(test_inv)
		resp = self.app.post(
			BASE_URL, json=test_inv.serialize(), content_type=CONTENT_TYPE_JSON
		)
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		# Make sure location header is set
		location = resp.headers.get("Location", None)
		self.assertIsNotNone(location)
		# Check the data is correct
		data = resp.get_json()
		inv_id = data["id"] # ID gets updated when creating in database
		self.assertEqual(data["name"], test_inv.name)
		self.assertEqual(data["quantity"], test_inv.quantity)
		self.assertEqual(data["condition"], test_inv.condition.name)
		self.assertEqual(data["restock_level"], test_inv.restock_level)
		# Check that the location header was correct
		resp = self.app.get(location, content_type=CONTENT_TYPE_JSON)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		data = resp.get_json()
		self.assertEqual(data["id"], inv_id, "Location")
		self.assertEqual(data["name"], test_inv.name)
		self.assertEqual(data["quantity"], test_inv.quantity)
		self.assertEqual(data["condition"], test_inv.condition.name)
		self.assertEqual(data["restock_level"], test_inv.restock_level)

	def test_create_inventory_no_data(self):
		"""Create a Inventory with missing data"""
		resp = self.app.post(BASE_URL, json={}, content_type=CONTENT_TYPE_JSON)
		self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
		# DataValidationError = Bad request

	def test_create_inventory_no_content_type(self):
		"""Create a Inventory with no content type"""
		resp = self.app.post(BASE_URL)
		self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

	def test_create_inventory_bad_quantity_type(self):
		""" Create a Inventory with bad quantity type """
		test_inv = InventoryFactory()
		logging.debug(test_inv)
		test_inv.quantity = "100" # Bad type
		resp = self.app.post(
			BASE_URL, json=test_inv.serialize(), content_type="application/json"
		)
		self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
		# DataValidationError = Bad request

	def test_create_inventory_bad_quantity_value(self):
		""" Create a Inventory with bad quantity value """
		inv = InventoryFactory()
		logging.debug(inv)
		test_inv = inv.serialize()
		test_inv["quantity"] = -1 # Bad value
		resp = self.app.post(
			BASE_URL, json=test_inv, content_type="application/json"
		)
		self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
		# DataValidationError = Bad request
	
	def test_create_inventory_bad_restock_type(self):
		""" Create a Inventory with bad restock_level type """
		test_inv = InventoryFactory()
		logging.debug(test_inv)
		test_inv.restock_level = "100" # Bad type
		resp = self.app.post(
			BASE_URL, json=test_inv.serialize(), content_type="application/json"
		)
		self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
		# DataValidationError = Bad request

	def test_create_inventory_bad_restock_value(self):
		""" Create a Inventory with bad restock_level value """
		inv = InventoryFactory()
		logging.debug(inv)
		test_inv = inv.serialize()
		test_inv["restock_level"] = -1 # Bad value
		resp = self.app.post(
			BASE_URL, json=test_inv, content_type="application/json"
		)
		self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
		# DataValidationError = Bad request

	def test_get_inv_list(self):
		"""Get a list of Inventory"""
		self._create_invs(5)
		resp = self.app.get(BASE_URL)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		data = resp.get_json()
		self.assertEqual(len(data), 5)
		
	def test_update_inventory(self):
		"""Update an existing Inventory"""
		# create an inventory to update
		test_inv = InventoryFactory()
		resp = self.app.post( # Create the inventory
			BASE_URL, json=test_inv.serialize(), content_type=CONTENT_TYPE_JSON
		)
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

		# update the inv
		data = resp.get_json()
		logging.debug(data)
		data["quantity"] = 50
		data["name"] = "kindle-oasis"
		resp = self.app.put(
			"/inventory/{}".format(data["id"]),
			json=data,
			content_type=CONTENT_TYPE_JSON,
		)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		updated_inv = resp.get_json()
		self.assertEqual(data["id"], updated_inv["id"])
		self.assertEqual(data["name"], updated_inv["name"])
		self.assertEqual(data["quantity"], updated_inv["quantity"])
		self.assertEqual(data["condition"], updated_inv["condition"])
		self.assertEqual(data["restock_level"], updated_inv["restock_level"])

	def test_update_inventory_not_found(self):
		"""Update a non-existing Inventory"""
		# create an update request
		new_inv = InventoryFactory()
		resp = self.app.put(
			"/inventory/{}".format(new_inv.id),
			json=new_inv.serialize(),
			content_type=CONTENT_TYPE_JSON,
		)
		self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

	def test_delete_inventory(self):
		"""Delete an Inventory"""
		# create an inventory to update
		test_inv = InventoryFactory()
		resp = self.app.post( # Create the inventory
			BASE_URL, json=test_inv.serialize(), content_type=CONTENT_TYPE_JSON
		)
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

		# Delete the inv
		new_inv = resp.get_json()
		logging.debug(new_inv)
		resp = self.app.delete(
			"/inventory/{}".format(new_inv["id"]),
			content_type=CONTENT_TYPE_JSON,
		)
		self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
		self.assertEqual(len(resp.data), 0)

	def test_delete_empty_inventory(self):
		"""Delete an Inventory that does not exist"""
		# Delete the inv
		resp = self.app.delete(
			"/inventory/{}".format(10),
			content_type=CONTENT_TYPE_JSON,
		)
		self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
		self.assertEqual(len(resp.data), 0)

	def test_add_stock(self):
		""""Increase the stock of an existing inventory"""
		inv = self._create_invs(1)[0] # Create 1 inventory and added it to database
		data = {"add_stock" : 50} # Create JSON for add_stock
		resp = self.app.put( # Action to update stock
			"/inventory/{}/add_stock".format(inv.id),
			json=data,
			content_type=CONTENT_TYPE_JSON,
		)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		
		updated_inv = resp.get_json() # Updated Inventory is returned as JSON
		self.assertEqual(updated_inv["id"], inv.id)
		self.assertEqual(updated_inv["name"], inv.name)
		self.assertEqual(updated_inv["quantity"], inv.quantity+data["add_stock"]) # Check stock updated
		self.assertEqual(updated_inv["condition"], inv.condition.name)
		self.assertEqual(updated_inv["restock_level"], inv.restock_level)

	def test_add_stock_no_inv(self):
		""""Increase the stock of a non-existing inventory"""
		data = {"add_stock" : 50} # Create JSON for add_stock
		resp = self.app.put( # Action to update stock
			"/inventory/{}/add_stock".format(10),
			json=data,
			content_type=CONTENT_TYPE_JSON,
		)
		self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
		
	def test_missing_add_stock(self):
		""""Increase the stock of an existing inventory without add_stock"""
		inv = self._create_invs(1)[0] # Create 1 inventory and added it to database
		resp = self.app.put( # Action to update stock
			"/inventory/{}/add_stock".format(inv.id),
			json={},
			content_type=CONTENT_TYPE_JSON,
		)
		self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
	
	def test_add_stock_bad_value(self):
		""""Increase the stock of an existing inventory"""
		inv = self._create_invs(1)[0] # Create 1 inventory and added it to database
		data = {"add_stock" : -50} # Create JSON for add_stock
		resp = self.app.put( # Action to update stock
			"/inventory/{}/add_stock".format(inv.id),
			json=data,
			content_type=CONTENT_TYPE_JSON,
		)
		self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
	
	def test_query_inv_list_by_name(self):
		"""Query Inventory by Name"""
		invs = InventoryFactory.create_batch(4)
		# Change inv[0],[1] name to "DevOps"
		invs[0].name = "DevOps"
		invs[1].name = "DevOps"
		# Create the invs in Inventory
		for i in range(0, len(invs)):
			invs[i].create()
		resp = self.app.get(
			BASE_URL, query_string="name={}".format(quote_plus("DevOps"))
		)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		data = resp.get_json()
		self.assertEqual(len(data), 2) # Should get 2 items
		for inv in data:
			# Check the name just to be sure
			self.assertEqual(inv["name"], "DevOps")
	
	def test_query_inv_list_no_name(self):
		"""Query by name does not exist"""
		resp = self.app.get(
			BASE_URL, query_string="name={}".format(quote_plus("DevOps"))
		)
		self.assertEqual(resp.status_code, status.HTTP_200_OK) # OK
		data = resp.get_json()
		self.assertTrue(isinstance(data, list)) # Should be a list
		self.assertEqual(len(data), 0) # Should get 0 items back
	
	def test_query_need_restock(self):
		"""Query inv that needs restock"""
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
		resp = self.app.get(
			BASE_URL, query_string="restock=1"
		)
		self.assertEqual(resp.status_code, status.HTTP_200_OK) # OK
		data = resp.get_json()
		self.assertEqual(len(data), 2) # Should get 2 items back
		for inv in data:
			if inv["id"] == invs[0].id:
				self.assertEqual(inv["quantity"], invs[0].quantity)
				self.assertEqual(inv["restock_level"], invs[0].restock_level)
			else:
				self.assertEqual(inv["quantity"], invs[1].quantity)
				self.assertEqual(inv["restock_level"], invs[1].restock_level)
	
	def test_query_by_condition(self):
		"""Returns all inv with the condition"""
		invs = self._create_invs(10)
		test_condition = invs[0].condition
		# Create a list of same condition invs
		condition_invs = [inv for inv in invs if inv.condition == test_condition]
		resp = self.app.get(
			BASE_URL, query_string="condition={}".format(quote_plus(test_condition.name))
		)
		self.assertEqual(resp.status_code, status.HTTP_200_OK) # Ok
		data = resp.get_json()
		self.assertEqual(len(data), len(condition_invs)) # Should be same length
		for inv in data:
			# Check the condition just to be sure
			self.assertEqual(inv["condition"], test_condition.name)