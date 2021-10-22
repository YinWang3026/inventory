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
    pass