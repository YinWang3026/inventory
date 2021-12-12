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
# from typing_extensions import Required
# from flask import Flask, jsonify, request, url_for, make_response, abort
from . import status, app  # HTTP Status Codes and Flask App
from service.models import Inventory, Condition
from flask_restx import Api, Resource, fields, reqparse, inputs
# from werkzeug.exceptions import NotFound, BadRequest

# For this example we'll use SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
# from flask_sqlalchemy import SQLAlchemy

######################################################################
# GET INDEX
# Configure the Root route before OpenAPI
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
# Configure Swagger before initializing it
######################################################################
api = Api(app,
    version='1.0.0',
    title='Inventory REST API Service',
    description='This is a simple Inventory server.',
    default='Inventory',
    default_label='Inventory Operations',
    doc='/apidocs', 
    prefix='/api' 
)

# Model from http requests
inv_request_model = api.model('Inventory Request Model', {
    'name': fields.String(
        required=True,
        description='The name of the Inventory'),
    'quantity': fields.Integer(
        required=True,
        description='The quantity of the Inventory'),
    'restock_level': fields.Integer(
        required=True,
        description='The restock level of the Inventory'),
    'condition': fields.String(
        required=True,
        enum=Condition._member_names_, 
        description='The condition of the Inventory')
})

# Entire Inventory model
inventory_model = api.inherit(
    'Inventory Response Model', # Name of the model
    inv_request_model, # Inheritance
    {
        'id': fields.Integer(
            readOnly=True, # Read only, database sets it
            description='The unique id assigned internally by db service'),
    }
)

# Increase Inventory Model
increase_model = api.model(
    'Incrase Inventory Model', 
    {
    'add_stock': fields.Integer(
        required=True,
        description='The quantity to add to the Inventory'),
    }
)

# Possible URL args
inv_args = reqparse.RequestParser()
inv_args.add_argument('name', type=str, 
    required=False, help='List Inventory by name')
inv_args.add_argument('condition', type=str, 
    required=False, help='List Inventory by condition')
inv_args.add_argument('need_restock', type=inputs.boolean, 
    required=False, help='List Inventory by whether it needs restock')

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################
def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)

######################################################################
#  PATH: /inventory
######################################################################
@api.route('/inventory', strict_slashes=False) # diff route, just /inventory
class InvCollection(Resource):
    """
    Handles all interactions with a collection of Inventory

    POST /inventory - Returns a Inventory with the id
    GET /Inventory - Returns a list of Inventory
    DELETE /inventory/{id} - deletes a inventory with a given id number 
    """
    #------------------------------------------------------------------
    # CREATE A NEW INVENTORY
    #------------------------------------------------------------------
    @api.doc('create_inventory')
    @api.response(400, 'The posted data was not valid')
    @api.expect(inv_request_model)
    @api.marshal_with(inventory_model, code=201)
    def post(self):
        """
        Creates a single Inventory

        This endpoint will create an Inventory based the data in the body that is posted
        """
        app.logger.info("Request to create a inventory")
        app.logger.debug('Payload = %s', api.payload) # payload = body of request
        inv = Inventory()
        inv.deserialize(api.payload) # Only accepts JSON
        inv.create()
        location_url = api.url_for(InvResource, inv_id=inv.id, _external=True)
        # _external means to generate an absolute UR, and not a relative URL
        # since this url is going to be used to access the resource from outside
        app.logger.info("Inventory with ID [%s] created.", inv.id)
        # Only returns JSON
        return inv.serialize(), status.HTTP_201_CREATED, {"Location": location_url}
    
    #------------------------------------------------------------------
    # LIST ALL INVENTORY
    #------------------------------------------------------------------
    @api.doc('list_inventory')
    @api.expect(inv_args, validate=True) # expect inv args and validate them
    @api.marshal_list_with(inventory_model)
    def get(self):
        """ 
        Returns all of the Inventory with matching query
        
        This endpoint will list Inventory based the query option in the args
        """
        app.logger.info("Request for inventory list")
        invs = []
        args = inv_args.parse_args()
        if args['name']:
            app.logger.info('Filtering by name: %s', args['name'])
            invs = Inventory.find_by_name(args['name'])
        elif args['condition']:
            app.logger.info('Filtering by condition: %s', args['name'])
            condition_enum = getattr(Condition, args['condition'])
            invs = Inventory.find_by_condition(condition_enum)
        elif args['need_restock']==True:
            app.logger.info('Filtering by need restock')
            invs = Inventory.find_by_need_restock()
        else:
            app.logger.info('Filtering by all')
            invs = Inventory.find_all()
        results = [inv.serialize() for inv in invs]
        app.logger.info("Returning %d invs", len(results))
        return results, status.HTTP_200_OK

######################################################################
#  PATH: /inventory/{id}
######################################################################
@api.route('/inventory/<inv_id>')  # route for the class
@api.param('inv_id', 'The Inventory ID')
class InvResource(Resource):
    """
    Resource class

    Allows the manipulation of a SINGLE Inventory
    GET /inventory/{id} - Returns an Inventory with the id
    PUT /inventory/{id} - Update an Inventory with the id
    DELETE /inventory/{id} -  Deletes an Inventory with the id
    """

    #------------------------------------------------------------------
    # RETRIEVE AN INVENTORY
    #------------------------------------------------------------------
    @api.doc('get_inventory') 
    @api.response(404, 'Inventory not found') 
    @api.marshal_with(inventory_model)
    def get(self, inv_id):
        """
        Retrieve a single Inventory

        This endpoint will return an Inventory based on it's id
        """
        app.logger.info("Request to Retrieve an Inventory with id [%s]", inv_id)
        inv = Inventory.find_by_id(inv_id)
        if not inv:
            abort(status.HTTP_404_NOT_FOUND, "Inventory with id '{}' was not found.".format(inv_id))
        return inv.serialize(), status.HTTP_200_OK

    #------------------------------------------------------------------
    # DELETE AN INVENTORY
    #------------------------------------------------------------------
    @api.doc('delete_inventory')
    @api.response(204, 'Inventory deleted')
    def delete(self, inv_id):
        """
        Delete a Inventory
        This endpoint will delete a Inventory based the id specified in the path
        """
        app.logger.info("Request to delete the inventory with key {}".format(inv_id))
        inventory = Inventory.find_by_id(inv_id)
        if inventory:
            inventory.delete()
            app.logger.info("Inventory with id {} deleted".format(inv_id))
        return '', status.HTTP_204_NO_CONTENT

    #------------------------------------------------------------------
    # UPDATE AN EXISTING INVENTORY
    #------------------------------------------------------------------
    @api.doc('update_inventory')
    @api.response(404, 'Inventory not found')
    @api.response(400, 'Inventory data invalid')
    @api.expect(inv_request_model)
    @api.marshal_with(inventory_model)
    def put(self, inv_id):
        """
        Update an Inventory

        This endpoint will update an Inventory based the body that is posted
        """
        app.logger.info('Request to Update an Inventory with id [%s]', inv_id)
        inv = Inventory.find_by_id(inv_id)
        if not inv:
            abort(status.HTTP_404_NOT_FOUND, "Inventory with id '{}' was not found.".format(inv_id))
        app.logger.debug('Payload = %s', api.payload)
        inv.deserialize(api.payload)
        inv.id = inv_id
        inv.update()
        app.logger.info("Inventory with ID [%s] updated.", inv.id)
        return inv.serialize(), status.HTTP_200_OK

######################################################################
#  PATH: /inventory/{id}/increase
######################################################################
@api.route('/inventory/<inv_id>/increase')
@api.param('inv_id', 'The Inventory ID')
class AddStockResource(Resource): # action
    """ 
    Increase actions on an Inventory 
    """

    #------------------------------------------------------------------
    # INCREASE AN INVENTORY STOCK
    #------------------------------------------------------------------
    @api.doc('increase_inventory')
    @api.response(404, 'Inventory not found')
    @api.response(400, 'Invalid quantity value')
    @api.expect(increase_model, validate=True)
    @api.marshal_with(inventory_model)
    def put(self, inv_id):
        """
        Increase inventory stock

        This endpoint will increase inventory stocks
        """
        quantity = api.payload["add_stock"]
        app.logger.info('Request to increases inventory [{}] stock by [{}]'.format(inv_id, quantity))

        inv = Inventory.find_by_id(inv_id)
        if not inv:
            abort(status.HTTP_404_NOT_FOUND, 'Inventory with id [{}] was not found.'.format(inv_id))
        
        if (quantity < 0):
            abort(status.HTTP_400_BAD_REQUEST, 'Quantity with value [{}] is invalid.'.format(quantity))

        inv.quantity += quantity
        inv.update()

        app.logger.info('Inventory with id [{}] stock increased successfully'.format(inv_id))
        return inv.serialize(), status.HTTP_200_OK
