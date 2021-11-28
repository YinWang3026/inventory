[![Run Python Tests](https://github.com/Inventory-Devops-Fall21/inventory/actions/workflows/workflow.yml/badge.svg)](https://github.com/Inventory-Devops-Fall21/inventory/actions/workflows/workflow.yml)
[![codecov](https://codecov.io/gh/Inventory-Devops-Fall21/inventory/branch/main/graph/badge.svg?token=8LLHNZEGQZ)](https://codecov.io/gh/Inventory-Devops-Fall21/inventory)

# Inventory

This repository contains all the work of the Inventory Squad as part of the Fall '21 DevOps under [John Rofrano](https://github.com/rofrano).

## Cloud URL

<https://nyu-inventory-service-fall2103.us-south.cf.appdomain.cloud/>

## To contribute, checkout [contribution.md](./contributing.md)

## Vagrant Port Forwards to 8080

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
  - Don't hardcode a port, use environment variable (see dot-env-example)
  - Used by CloudFoundry and honcho to start the app
- manifest.yml
  - Tells CloudFoundry how to deploy the app
  - `ic cf push` to push the code to CloudFoundry
- runtime.txt
  - The environment to use for CloudFoundry
- dot-env-example
  - cp dot-env-example .env
  - Adds to the environment variables
  - PORT specifies the port that the Flask App and honcho should start on
- .cfignore
  - Files to be ignored from CloudFoundry

## Starting the VM

- Clone the project folder
- `vagrant up` at the project folder root
- `vagrant ssh` to ssh into the VM
- `cd /vagrant/` to change directory to project folder root within the VM

## Running the App with Flask

- `export FLASK_APP=service:app` to set the environment variable to run flask app
- `flask run -h 0.0.0.0 -p 8080` to run the application
  - Default on 5000, changed to 8080
  - On host machine, visit: <http://127.0.0.1:8080/>

## Running the App with Honcho

- `honcho start` to run the app using settings in Procfile to run gunicorn server
  - Default port = 5000
  - Otherwise specifiy in environment var `PORT=XXXX`
    - Use dot-env-example to set port to 8080

## Test Driven Development

- At the root of the project folder, run
- `nosetests` to run the tests
- `coverage report -m` to see test coverage

## Behavior Driven Development

- At the root of the project folder, run
- `behave` to run all the feature tests in one terminal
- `honcho start` to run the server in another terminal