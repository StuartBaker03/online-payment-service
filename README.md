# Online Payment Service

A full-stack Django web application developed as part of a university Web Applications and Services project.

The application implements a simplified online payment service, allowing users to create accounts, send and request payments, view transaction history, and hold balances in multiple currencies. Currency conversion is handled through a REST API.

## Features

- User registration, login and logout
- User accounts with GBP, USD or EUR balances
- Direct payments between registered users
- Payment requests with accept/reject functionality
- Transaction history and account balance tracking
- Currency conversion through a RESTful web service
- Administrator views for managing users and transactions
- Authentication and access control
- CSRF, XSS, SQL injection and clickjacking protections

## Technologies

- Python
- Django
- Django REST Framework
- SQLite
- HTML / CSS
- Bootstrap

## Running the Project

Install the required dependencies:

```bash
pip install -r requirements.txt
```

Run the Django development server:

```bash
python manage.py runserver
```

## About

This project was created for university coursework and represents a simplified payment system using simulated funds only. It is not intended for production use or for processing real financial transactions.