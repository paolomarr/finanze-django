A personal finance and accounting app, based on a Django backend serving a RESTful API + a React frontend to consume it.

## Requirements

For docker install:
- docker
- docker-compose

For hosted install:
- python3
- node

## Installation

### Docker install

Use the wrapper script `deploy_docker.sh` to prepare your environment and deploy a fully dockerized instance of the app.  
The script requires user interaction if some of the required .env files are not present (typically at first installation).  
For developers: the script is idempotent, i.e. it can be called to update the installation after making any changes to the source code.

### Hosted install

Refer to the content of `Dockerfile_django` and `Dockerfile_react` files to derive the steps required to install the system physically on your machine.

## Features

Accounting:
- keep track of your expenses and incomes by recording your daily movements
- periodically record your actual assets balance and check it against the movements you traked to verify you didn't miss anythin
- get insights of your spending habits and improve your saving attitude
Finance:
- record your trading operations and track the evolution of your assets over time