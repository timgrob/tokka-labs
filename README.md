# tokka-labs
RESTful API for tokka-labs' coding challenge

The api interacts with Etherscan's api to retrieve transaction data. At startup the latest transactions are fetched from Etherscan and then starts recording new incoming transactions (every 60 seconds).

NOTE: Given that there are many transactions already on the Uniswap pool, the API fetches the transactions of the last 10 blocks by default. However, this can be changed (see section Usage).

# setup
## 1: Virtual Environment
- Create a virtual environment (e.g. conda or venv) with Python Version = 3.10
- Activate virtual environment

Conda Example:
```
conda create -n {ENV_NAME} python=3.10
conda activate {ENV_NAME}
```

## 2: Install dependencies
Once the virtual environment is activated install ```requirements.txt``` dependencies by running: ```pip instal - r requirements.txt```

## 3: Create .env file
Due to security reasons, ```.env``` file is not checked in to the GitHub repository in order to not expose the Etherscan's api key. Therefore a ```.env``` file needs to be manually created in the project's root directory 

Type ```touch .env``` in the terminal when in the root directory of the project.

Open your favorite code editor and put the following code there: ```ETHERSCAN_API_KEY = "{YOUR_ETHERSCAN_API_KEY}"```

# Run Code
In the project's root directory run main.py file from the terminal by typing ```uvicorn main:app```
The application will be running at localhost ```http://127.0.0.1:8000```

# Docs
Once the application is running, a Swagger documentation can be viewed at ```http://127.0.0.1:8000/docs```
The Swagger interface also allows you to interact with the api.

# Usage
The EtherscanMonitor in the startup function takes an optional block_limit parameter. This parameter is currently set to block_limit=10. This means, only the transactions within the last 10 found blocks are fetched from Etherscan's api. This number can be changed manually or completely omitted. Yet if you omit the value, all transactions in the Uniswap pool will be fetched, which takes a long time. 