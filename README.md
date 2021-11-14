[![Run Python Tests](https://github.com/Inventory-Devops-Fall21/inventory/actions/workflows/workflow.yml/badge.svg)](https://github.com/Inventory-Devops-Fall21/inventory/actions/workflows/workflow.yml)
[![codecov](https://codecov.io/gh/Inventory-Devops-Fall21/inventory/branch/main/graph/badge.svg?token=8LLHNZEGQZ)](https://codecov.io/gh/Inventory-Devops-Fall21/inventory)

# Inventory

This repository contains all the work of the Inventory Squad as part of the Fall '21 DevOps under [John Rofrano](https://github.com/rofrano).

## Cloud URL

<https://nyu-inventory-service-fall2103.us-south.cf.appdomain.cloud/>

## To contribute, checkout [contribution.md](./contributing.md)

## File Descritions

- .github
  - Contains Github templates
- .gitignore
  - Files to be ignored from repository
- contributing.md
  - Information on good coding practice that this project follows
- requirements.txt
  - Python modules needed
- Vagrantfile
  - Builds the VM for running this project
- setup.cfg
  - Running arguments for nosetest
- .coveragerc
  - Used by Coverage tool
- config.py
  - Shared variables across the project
  - Contains config for SQL Alchemy to set up database connection
- workflow.yml
  - Used by Git Action to setup environment and run tests
  - Continuous Integration
- gunicorn.conf.py
  - Contains config for gunicorn, a HTTP server
- Procfile
  - config for gunicorn server to run the app
  - Don't hardcode a port, use environment variable
  - Used by CloudFoundry and honcho to start the app
- manifest.yml
  - Tells CloudFoundry how to deploy the app
- runtime.txt
  - The environment to use for CloudFoundry

## Running the App

- Clone the project folder
- `vagrant up` at the project folder root
- `vagrant ssh` to ssh into the VM
- `cd /vagrant/` to change directory to project folder root within the VM
- `export FLASK_APP=service:app` to set the environment variable to run flask app
- `flask run -h 0.0.0.0` to run the application
  - On host machine, visist: <http://127.0.0.1:5000/>
- `nosetests` to run the tests
- `coverage report -m` to see test coverage

- OR
- `honcho start` to run the app using settings in Procfile to run gunicorn server
  - Default port = 5000
  - Otherwise specifiy in environment var `PORT='a_port'`
