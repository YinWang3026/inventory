"""
Models for the Inventory Service

All of the models are stored in this module

Models
------
Inventory - An Inventory used keep track of items

Attributes:
-----------
item_name (string) - the name of the item
count (int) - the count of individual items in the inventory

"""
import logging
from enum import Enum
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

    pass

class Inventory(db.Model):
    
    app:Flask = None
    
    # Inventory Schema
    
    prod_Id = db.Column(db.Integer, primary_key=True)
    prod_Name = db.Column(db.String(80), nullable=False)
    available = db.Column(db.Boolean(), nullable=False, default=False)
    quantity = db.Column(db.Integer)
    
    ##################################################
    # INSTANCE METHODS
    ##################################################
    
    def __repr__(self):
        return "<prod_Id>" % (self.prod_Id)
    
    def serialize(self) -> dict:
        """Serializes a each Inventory record into a dictionary"""
        return {
            "id": self.prod_Id,
            "name": self.prod_Name,
            "available": self.available,
            "quantity": self.quantity,
        }
    
    def deserialize(self, data):
        """ Deserializes an Inventory record from a dictionary """
        try:
            self.product_Id = data["prod_ID"]
            self.prod_Name = data["prod_Name]
            self.available = data["available"]
            self.quantity = data["quantity"]
        except KeyError as error:
            raise DataValidationError("Invalid Inventory record: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError("Invalid Inventory record: body of request contained bad or no data")
        return self
