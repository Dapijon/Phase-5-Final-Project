# Money Transfer App Backend

Welcome to the backend repository for our Money Transfer App. This backend serves as the core functionality of our application, handling user authentication, transaction management, and administrative tasks. Below, you'll find instructions on how to set up and run the backend server locally.

# Prerequisites

Before getting started, ensure you have the following installed on your machine:

Python (https://www.python.org) - This project is built using Python programming language.

Flask (https://flask.palletsprojects.com) - Flask is a web framework for Python.

PostgreSQL (https://www.postgresql.org) - Our backend uses PostgreSQL as the database to store user information and transaction data.

# Installation

Clone this repository to your local machine:

bash

git clone https://github.com/your/repository.git

Navigate into the cloned directory:

bash

cd money-transfer-app-backend

# Backend Setup

Install backend dependencies using Pipenv:

pipenv install

# Create a virtual environment 

  pipenv shell
# Run database migrations:


flask db upgrade

# Seed the database with initial data:

python seed.py

# Run the Flask API on localhost:5555:

python3 app.py

# Contributing

We welcome contributions from the community to improve and extend the functionality of our Money Transfer App backend. Please follow the guidelines outlined in the CONTRIBUTING.md file for submitting pull requests.

# License

This project is licensed under the MIT License.

If you have any questions or need further assistance, feel free to reach out to us at leon.kinyanjui@student.moringaschool.com.

Thank you for using our Money Transfer App backend!
