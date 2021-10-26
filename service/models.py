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
    """Initialies the SQLAlchemy app"""
    Inventory.init_db(app)

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """

    pass

class Inventory(db.Model):
    
    app:Flask = None
    
    # Inventory Schema
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Integer)
    
    ##################################################
    # INSTANCE METHODS
    ##################################################
    
    def __repr__(self):
        return "<id=%r name=%s quantity=%s>" % (self.id, self.name, self.quantity)
    
    def create(self):
        """
        Creates a Inventory to the database
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
        pass

    def serialize(self) -> dict:
        """Serializes an Inventory into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "quantity": self.quantity,
        }
    
    def deserialize(self, data):
        """ 
        Deserializes a Inventory from a dictionary 
        Args:
            data (dict): A dictionary containing the Inventory data
        """
        try:
            self.id = data["id"]
            self.name = data["name"]
            if isinstance(data["quantity"], int):
                if data["quantity"] >= 0:
                    self.quantity = data["quantity"]
                else:
                    raise DataValidationError("Invalid value for [quantity>=0]: " + data["quantity"])
            else:
                raise DataValidationError("Invalid type for int [quantity]: " + str(type(data["quantity"])))
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0])
        except KeyError as error:
            raise DataValidationError("Invalid Inventory: missing " + error.args[0])
        except TypeError as error:
            raise DataValidationError("Invalid Inventory: body of request contained bad or no data")
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def init_db(cls, app:Flask):
        """Initializes the database session

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
    def all(cls) -> list:
        """Returns all of the Inventory in the database"""
        logger.info("Processing all Inventory")
        return cls.query.all()
    
    @classmethod
    def find(cls, inv_id:int):
        """Find an Inventory by it's id

        :param inv_id: the id of the Inventory to find
        :type inv_id: int

        :return: an instance with the inv_id, or None if not found
        :rtype: Inventory

        """
        logger.info("Processing lookup for id %s ...", inv_id)
        return cls.query.get(inv_id)
