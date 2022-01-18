# Inventory

[![Run Python Tests](https://github.com/Inventory-Devops-Fall21/inventory/actions/workflows/workflow.yml/badge.svg)](https://github.com/Inventory-Devops-Fall21/inventory/actions/workflows/workflow.yml)
[![codecov](https://codecov.io/gh/Inventory-Devops-Fall21/inventory/branch/main/graph/badge.svg?token=8LLHNZEGQZ)](https://codecov.io/gh/Inventory-Devops-Fall21/inventory)

This repository contains all the work of the Inventory Squad as part of the Fall '21 DevOps under [John Rofrano](https://github.com/rofrano).

## Cloud URL

* Dev: <https://nyu-inventory-service-fall2103-dev.us-south.cf.appdomain.cloud/>
* Prod: <https://nyu-inventory-service-fall2103.us-south.cf.appdomain.cloud/>

## To contribute, checkout [contribution.md](./contributing.md)

## Vagrant Port Forwards to 8080

## File Descritions

* .github
  * Contains Github templates
* .gitignore
  * Files to be ignored from repository
* contributing.md
  * Information on good coding practice that this project follows
* requirements.txt
  * Python modules needed
* Vagrantfile
  * Builds the VM for running this project
* setup.cfg
  * Running arguments for nosetest
* .coveragerc
  * Used by Coverage tool
* config.py
  * Shared variables across the project
  * Contains config for SQL Alchemy to set up database connection
* workflow.yml
  * Used by Git Action to setup environment and run tests
  * Continuous Integration
* gunicorn.conf.py
  * Contains config for gunicorn, a HTTP server
* Procfile
  * config for gunicorn server to run the app
  * Don't hardcode a port, use environment variable (see dot-env-example)
  * Contains start command used by CloudFoundry and honcho to start the app
* manifest.yml
  * Tells CloudFoundry how to deploy the app
  * `ic cf push` to push the code to CloudFoundry
* runtime.txt
  * The environment to use for CloudFoundry
* dot-env-example
  * cp dot-env-example .env
  * Read by Application to add to the environment variables
  * PORT specifies the port that the Flask App and honcho should start on
* .cfignore
  * Files to be ignored from CloudFoundry
* Dockerfile
  * Create docker image
* .dockerignore
  * Files to not add to the docker image
* docker-compose.yml
  * Run multiple docker images
* .devcontainer
  * Runs the project in a Docker container

## Starting the VM

* Clone the project folder
* `vagrant up` at the project folder root
* `vagrant ssh` to ssh into the VM
* `cd /vagrant/` to change directory to project folder root within the VM

## Running the App with Flask

* `export FLASK_APP=service:app` to set the environment variable to run flask app
* `flask run -h 0.0.0.0 -p 8080` to run the application
  * Default on 5000, changed to 8080
  * On host machine, visit: <http://127.0.0.1:8080/>

## Running the App with Honcho

* `honcho start` to run the app using settings in Procfile to run gunicorn server
  * Default port = 5000
  * Otherwise specifiy in environment var `PORT=XXXX`
    * Use dot-env-example to set port to 8080

## Test Driven Development

* At the root of the project folder, run
* `nosetests` to run the tests
* `coverage report -m` to see test coverage

## Behavior Driven Development

* At the root of the project folder, run
* `behave` to run all the feature tests in one terminal
* `honcho start` to run the server in another terminal

## Deploy to Cloud

* Login to ibmcloud tool
  * `ibmcloud login -a https://cloud.ibm.com --apikey @~/.bluemix/apikey.json -r us-south`
* Set ibm target
  * `ic target --cf`
* Create User Provided Service
  * `ic cf cups ElephantSQL-dev -p '{"url":"postgres://xxxx"}'`
  * `ic cf cups ElephantSQL-prod -p '{"url":"postgres://xxxx"}'`
* Push to CloudFoundry
  * `ic cf push -f manifest-dev.yml`
  * `ic cf push -f manifest-prod.yml`

## Docker

* Build image for our service
  * `docker build -t inventory:latest .`
  * Change tag if needed
* Running the Inventory Service Image
  * `docker run --name inventory --rm -p 8080:8080 --link postgres -e DATABASE_URI="postgres://postgres:postgres@postgres:5432/" inventory:latest`
* Running the Postgers Image
  * `docker run -d --name postgres --rm -p 5432:5432 -v psql_data:/var/lib/postgresql/data -e POSTGRES_PASSWORD=postgres postgres:alpine`
* To run both images with docker compose
  * `docker-compose up -d`
  * This will also run an NGINX server

## DevContainers

* Windows 11 does not support VirtualBox at the moment, using Devcontainers with Docker instead
* Simply use VS Code to open the folder in a container
* If nosetests do not find the tests, run `chmod -x $(find tests/ -name '*.py')`
