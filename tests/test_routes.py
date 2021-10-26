"""
Inventory API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN

"""

import os
import logging
import unittest

from urllib.parse import quote_plus
from service import status  # HTTP Status Codes
from service.models import db, init_db
from service.routes import app
from .factories import InventoryFactory

# Disable all but ciritcal errors during normal test run
# uncomment for debugging failing tests
logging.disable(logging.CRITICAL)

# DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')
DATABASE_URI = os.getenv(
    "DATABASE_URI",
    "postgres://postgres:postgres@localhost:5432/postgres"
)
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
  	Factory method to create invs in bulk
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
		data = resp.get_json()
		self.assertEqual(data["name"], "Inventory REST API Service")
	
	def test_get_inventory(self):
		"""Get a single inventory with id"""
		# get the id of a inventory
		test_inv = self._create_invs(1)[0] # One item
		resp = self.app.get(
			"/inventory/{}".format(test_inv.id), content_type=CONTENT_TYPE_JSON
		)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		data = resp.get_json()
		self.assertEqual(data["name"], test_inv.name)

	def test_get_inventory_not_found(self):
		"""Get a Inventory thats not found"""
		resp = self.app.get("/inventory/0")
		self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

	def test_create_inventory(self):
		"""Create a new Inventory"""
		test_inv = InventoryFactory()
		logging.debug(test_inv)
		resp = self.app.post(
			BASE_URL, json=test_inv.serialize(), content_type=CONTENT_TYPE_JSON
		)
		self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
		# Make sure location header is set
		location = resp.headers.get("Location", None)
		self.assertIsNotNone(location)
		# Check the data is correct
		new_inv = resp.get_json()
		self.assertEqual(new_inv["name"], test_inv.name, "Name does not match")
		self.assertEqual(
			new_inv["quantity"], test_inv.quantity, "Quantity does not match"
		)
		# Check that the location header was correct
		resp = self.app.get(location, content_type=CONTENT_TYPE_JSON)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		new_inv = resp.get_json()
		self.assertEqual(new_inv["name"], test_inv.name, "Name does not match")
		self.assertEqual(
			new_inv["quantity"], test_inv.quantity, "Quantity does not match"
		)

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
		new_inv = resp.get_json()
		logging.debug(new_inv)
		new_inv["quantity"] = 50
		new_inv["name"] = "kindle-oasis"
		resp = self.app.put(
			"/inventory/{}".format(new_inv["id"]),
			json=new_inv,
			content_type=CONTENT_TYPE_JSON,
		)
		self.assertEqual(resp.status_code, status.HTTP_200_OK)
		updated_inv = resp.get_json()
		self.assertEqual(updated_inv["quantity"], 50)
		self.assertEqual(updated_inv["name"], "kindle-oasis")

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
			json=new_inv,
			content_type=CONTENT_TYPE_JSON,
		)
		self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
		self.assertEqual(len(resp.data), 0)
