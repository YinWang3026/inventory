"""
Models for the Inventory Service

All of the models are stored in this module

Models
------
Inventory - An Inventory used keep track of products

Attributes:
-----------
name (string) - the name of the product
quantity (int) - the quantity of the product

"""
import logging
from enum import Enum
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

def init_db(app):
    """
    Initialies the SQLAlchemy app
    """
    Inventory.init_db(app)

class DataValidationError(Exception):
    """
    Used for an data validation errors when deserializing
    """
    pass

class Condition(Enum):
    """ 
    Enumeration of Condition of an Inventory 
    """
    used = 0
    slightly_used = 1
    new = 2
    unknown = 3

class Inventory(db.Model):
    
    app:Flask = None
    
    # Inventory Schema 
    id = db.Column(db.Integer, primary_key=True) # row entries
    name = db.Column(db.String(80), nullable=False)
    condition = db.Column(
        db.Enum(Condition), nullable=False, server_default=(Condition.unknown.name)
    )
    quantity = db.Column(db.Integer, nullable=False)
    restock_level = db.Column(db.Integer, nullable=False)
    
    ##################################################
    # INSTANCE METHODS
    ##################################################
    
    def __repr__(self):
        """ 
        String representation of an Inventory 
        """
        return "<id=%r name=%s quantity=%d condition=%s restock_level=%d>" % \
            (self.id, self.name, self.quantity, self.condition.name, self.restock_level)
    
    def create(self):
        """
        Creates an Inventory to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # id must be none to generate next primary key
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        """
        Updates an Inventory to the database
        """
        logger.info("Updating %s", self.name)
        if not self.id:
            raise DataValidationError("Update called with empty ID field")
        db.session.commit()

    def delete(self):
        """
        Removes an Inventory from the data store
        """
        logger.info("Deleting %s", self.name)
        db.session.delete(self)
        db.session.commit()

    def serialize(self) -> dict:
        """
        Serializes an Inventory into a dictionary
        """
        return {
            "id": self.id,
            "name": self.name,
            "condition": self.condition.name, # enum to string
            "quantity": self.quantity,
            "restock_level": self.restock_level
        }
    
    def deserialize(self, data):
        """ 
        Deserializes an Inventory from a dictionary 
        Args:
            data (dict): A dictionary containing the Inventory data
        """
        try:
            self.id = data["id"]
            self.name = data["name"]
            self.condition = getattr(Condition, data["condition"]) # string to enmu
            if isinstance(data["quantity"], int) and data["quantity"] >= 0:
                self.quantity = data["quantity"]
            else:
                raise DataValidationError("Invalid type/value for quantity [%s] [%d]" % (str(type(data["quantity"])), data["quantity"]))
            if isinstance(data["restock_level"], int) and data["restock_level"] >= 0:
                self.restock_level = data["restock_level"]
            else:
                raise DataValidationError("Invalid type/value for restock_level [%s] [%d]" % (str(type(data["restock_level"])), data["restock_level"]))
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0])
        except KeyError as error:
            raise DataValidationError("Invalid Inventory record: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError("Invalid Inventory record: body contained bad or no data")

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def init_db(cls, app:Flask):
        """
        Initializes the database session

        :param app: the Flask app
        :type data: Flask

        """
        logger.info("Initializing database")
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables
    
    @classmethod
    def find_all(cls) -> list:
        """
        Returns all of the Inventory in the database
        """
        logger.info("Processing all Inventory")
        return cls.query.all()
    
    @classmethod
    def find_by_id(cls, id:int):
        """
        Find an Inventory by it's id

        :param id: the id of the Inventory to find
        :type id: int

        :return: an instance with the id, or None if not found
        :rtype: Inventory

        """
        logger.info("Processing lookup for id %s ...", id)
        return cls.query.get(id)