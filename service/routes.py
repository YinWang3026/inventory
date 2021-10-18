"""
Inventory Service

Paths:
------
GET /items - Returns a list all of the Items
GET /items/{id} - Returns the item with a given id number
POST /items - creates a new item record in the database
PUT /items/{id} - updates a item record in the database
DELETE /items/{id} - deletes a item record in the database
"""

import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from . import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Inventory, DataValidationError

# Import Flask application
from . import app

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    return (
        jsonify(
            name="Inventory REST API Service",
            version="1.0",
            paths=url_for("list_items", _external=True),
        ),
        status.HTTP_200_OK,
    )