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

# import os
# import sys
# import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from . import status  # HTTP Status Codes
from werkzeug.exceptions import NotFound, BadRequest

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Inventory, Condition

# Import Flask application
from . import app

######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """ Root URL response """
    # return (
    #     jsonify(
    #         name="Inventory REST API Service",
    #         version="1.0",
    #         paths=url_for("list_inventory", _external=True),
    #     ),
    #     status.HTTP_200_OK,
    # )
    return app.send_static_file("index.html")

######################################################################
# LIST ALL INVENTORY
######################################################################
@app.route("/inventory", methods=["GET"])
def list_inventory():
    """ Returns all of the Inventory """
    app.logger.info("Request for inventory list")
    invs = []
    name = request.args.get("name") # Query by name
    condition = request.args.get("condition") # Query by condition (string)
    need_restock = request.args.get("need_restock") # Query by restock need
    if name:
        invs = Inventory.find_by_name(name)
    elif condition:
        condition_enum = getattr(Condition, condition)
        invs = Inventory.find_by_condition(condition_enum)
    elif need_restock=="true":
        invs = Inventory.find_by_need_restock()
    else:
        invs = Inventory.find_all()
    results = [inv.serialize() for inv in invs]
    app.logger.info("Returning %d invs", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# RETRIEVE A INVENTORY
######################################################################
@app.route("/inventory/<int:id>", methods=["GET"])
def get_inventory(id):
    """
    Retrieve a single Inventory
    This endpoint will return a Inventory based on it's id
    """
    app.logger.info("Request for inventory with id: %s", id)
    inventory = Inventory.find_by_id(id)
    if not inventory:
        raise NotFound("Inventory with id '{}' was not found.".format(id))

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
    inv = Inventory()
    inv.deserialize(request.get_json())
    inv.create()
    location_url = url_for("get_inventory", id=inv.id, _external=True)

    app.logger.info("Inventory with ID [%s] created.", inv.id)
    return make_response(
        jsonify(inv.serialize()), status.HTTP_201_CREATED, {"Location": location_url}
    )

######################################################################
# UPDATE AN EXISTING INVENTORY
######################################################################
@app.route("/inventory/<int:id>", methods=["PUT"])
def update_inventory(id):
    """
    Update an Inventory
    This endpoint will update an Inventory based the body that is posted
    """
    app.logger.info("Request to update inventory with id: %s", id)
    check_content_type("application/json")
    inv = Inventory.find_by_id(id)
    if not inv:
        raise NotFound("Inventory with id '{}' was not found.".format(id))
    inv.deserialize(request.get_json())
    inv.id = id
    inv.update()

    app.logger.info("Inventory with ID [%s] updated.", inv.id)
    return make_response(jsonify(inv.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE A INVENTORY
######################################################################
@app.route("/inventory/<int:id>", methods=["DELETE"])
def delete_inventory(id):
    """
    Delete a Inventory
    This endpoint will delete a Inventory based the id specified in the path
    """
    app.logger.info("Request to delete the inventory with key {}".format(id))
    check_content_type("application/json")
    inventory = Inventory.find_by_id(id)
    if inventory:
        inventory.delete()
    app.logger.info("Inventory with id {} deleted".format(id))
    return make_response("", status.HTTP_204_NO_CONTENT)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def check_content_type(media_type):
    """
    Checks that the media type is correct
    """
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        "Content-Type must be {}".format(media_type),
    )

######################################################################
# UPDATE AN EXISTING INVENTORY QUNATITY ACTION
######################################################################
@app.route("/inventory/<int:id>/add_stock", methods=["PUT"])
def add_stock(id):
    """
    This endpoint will increase an Inventory stock based the body that is posted
    """
    app.logger.info("Request to add_stock with id: {}".format(id))
    check_content_type("application/json")
    inv = Inventory.find_by_id(id)
    if not inv:
        raise NotFound("Inventory with id '{}' was not found.".format(id))
    
    body = request.get_json()
    if "add_stock" not in body.keys():
        raise BadRequest("add_stock is missing from request body")
        
    quantity = body["add_stock"]
    if (quantity < 0) or (not isinstance(quantity, int)): 
        raise BadRequest("add_stock '{}' is of incorrect type or value".format(quantity))
        # status.HTTP_400_BAD_REQUEST  
          
    inv.quantity += quantity
    inv.update()
    app.logger.info("Inventory with ID [%s] updated.", inv.id)
    return make_response(jsonify(inv.serialize()), status.HTTP_200_OK)