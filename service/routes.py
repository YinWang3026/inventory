"""
Inventory Service

Paths:
------
GET /inventory - returns a list all of the inventory
GET /inventory/{id} - returns the inventory with a given id number
POST /inventory - creates a new inventory in the database
PUT /inventory/{id} - updates a inventory with a given id number 
DELETE /inventory/{id} - deletes a inventory with a given id number 
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
            paths=url_for("list_inventory", _external=True),
        ),
        status.HTTP_200_OK,
    )

######################################################################
# LIST ALL INVENTORY
######################################################################
@app.route("/inventory", methods=["GET"])
def list_inventory():
    """Returns all of the Inventory"""
    app.logger.info("Request for inventory list")
    invs = Inventory.all()
    results = [inv.serialize() for inv in invs]
    app.logger.info("Returning %d invs", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# RETRIEVE A INVENTORY
######################################################################
@app.route("/inventory/<int:inventory_id>", methods=["GET"])
def get_inventory(inventory_id):
    """
    Retrieve a single Inventory

    This endpoint will return a Inventory based on it's id
    """
    app.logger.info("Request for inventory with id: %s", inventory_id)
    inventory = Inventory.find(inventory_id)
    if not inventory:
        raise NotFound("Inventory with id '{}' was not found.".format(inventory_id))

    app.logger.info("Returning Inventory: %s", inventory.name)
    return make_response(jsonify(inventory.serialize()), status.HTTP_200_OK)

######################################################################
# ADD A NEW INVENTORY
######################################################################
@app.route("/inventory", methods=["POST"])
def create_inventory():
    """
    Creates an single Inventory
    This endpoint will create a Inventory based the data in the body that is posted
    """
    app.logger.info("Request to create a inventory")
    check_content_type("application/json")
    inventory = Inventory()
    inventory.deserialize(request.get_json())
    inventory.create()
    message = inventory.serialize()
    location_url = url_for("get_inventory", inventory_id=inventory.id, _external=True)

    app.logger.info("Inventory with ID [%s] created.", inventory.id)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# UPDATE AN EXISTING INVENTORY
######################################################################
@app.route("/inventory/<int:inventory_id>", methods=["PUT"])
def update_inventory(inventory_id):
    pass 

######################################################################
# DELETE A INVENTORY
######################################################################
@app.route("/inventory/<int:inventory_id>", methods=["DELETE"])
def delete_inventory(inventory_id):
    pass 

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        "Content-Type must be {}".format(media_type),
    )
