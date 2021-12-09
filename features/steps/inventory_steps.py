"""
Inventory Steps

Steps file for inventory.feature

For information on Waiting until elements are present in the HTML see:
    https://selenium-python.readthedocs.io/waits.html
"""
import json
import requests
from behave import given
from compare import expect

@given('the following inventory')
def step_impl(context):
    """ Delete all Inventory and load new ones """
    headers = {'Content-Type': 'application/json'}
    # list all of the inventory and delete them one by one
    context.resp = requests.get(context.base_url + '/inventory', headers=headers)
    expect(context.resp.status_code).to_equal(200)
    for inv in context.resp.json():
        context.resp = requests.delete(context.base_url + '/inventory/' + str(inv["id"]), headers=headers)
        expect(context.resp.status_code).to_equal(204)
    
    # load the database with new inventory
    create_url = context.base_url + '/inventory'
    context.ids = []
    for row in context.table:
        data = {
            "name": row['name'],
            "quantity": int(row['quantity']),
            "condition": row['condition'],
            "restock_level": int(row['restock_level'])
        }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        data = context.resp.json()
        context.ids.append(data["id"])
        expect(context.resp.status_code).to_equal(201)
