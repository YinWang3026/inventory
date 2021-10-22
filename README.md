# Inventory

This repository contains all the work of the Inventory Squad as part of the Fall '21 DevOps under [John Rofrano](https://github.com/rofrano).

## File Descritions

- .github
  - Contains Github templates
- .gitignore
  - Files to be ignored from repository
- contributing.md
  - Information on good coding practice
- requirements.txt
  - Python modules needed
- Vagrantfile
  - Builds the VM for running this project
- setup.cfg
  - Running arguments for nosetest
- .coveragerc
  - Used by Coverage tool
- config.py
  - Contains config for SQL Alchemy to set up database connection
- gunicorn.conf.py
  - Contains config for gunicorn, a HTTP server

## Running the App

- Clone the project folder
- "vagrant up" at the project folder root
- "vagrant ssh" to ssh into the VM
- "cd /vagrant/" to change directory to project folder root within the VM
- "flask run" to run the application
  - No need to do "export FLASK_APP=service:app"
  - Already done in Vagrantfile
