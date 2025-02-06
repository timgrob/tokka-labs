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
Once the virtual environment is activated install ```requirements.txt``` dependencies by running: 

```
pip install - r requirements.txt
```

## 3: Create .env file
Due to security reasons, ```.env``` file is not checked in to the GitHub repository in order to not expose the Etherscan's api key. Therefore a ```.env``` file needs to be manually created in the project's root directory 

Type ```touch .env``` in the terminal when in the root directory of the project or create a new ```.env``` via the system explorer.

Open your favorite code editor and put the following code in your newly created ```.env``` file: 
```
ETHERSCAN_API_KEY = "{YOUR_ETHERSCAN_API_KEY}"
```

# Run Code
In the project's root directory run main.py file from the terminal by typing: 
```
uvicorn main:app
```

The application will be running at localhost ```http://127.0.0.1:8000```

# Run Tests
All tests can be run by running the follwing command from the terminal when in the project's root directory:
```
python -m pytest
```

# Docs
Once the application is running, a Swagger documentation can be viewed at ```http://127.0.0.1:8000/docs```
The Swagger interface also allows you to interact with the api.

# Usage
The EtherscanMonitor in the startup function takes an optional ```block_limit``` parameter. This parameter is currently set to ```block_limit=10```. This means, only the transactions within the last 10 found blocks are fetched from Etherscan's api. This number can be changed manually or completely omitted. Yet if you omit the value, all transactions in the Uniswap pool will be fetched, which takes a long time. 

# Bonus Questions
## Availability
Given that the system currently runs locally, availability is low. Once the local server is terminated, the api is no longer accessible. Therefore, the application should be deployed on a private server or a cloud provider platform, where the cloud provider guarantees a high percentage of up-time.

Given that the application can be technically split in three parts: 
- api: server runs the api and fetches transaction data from database
- database: server where database is run and transaction data is stored
- data recording: server that continously fetches the latest transaction data from the Etherscan api and stored into the database

These three parts should "live" on separate servers, to improve availability. Because currently, if the local server goes down, the entire app is down and the database is whiped (I clear the database at shutdown, which is by design). Yet, if for instance only data recording server goes bust, then the api would still be accessible and older transactions can still be fetched. 

## Scalability
The api has been designed in a modular way with services (either modules or functions), which all work stand alone. These services could also be executed individually by running them in lambda functions or have different cloud servers running the service. 

Due to the small number of end points (only two were required, yet I build some more just for fun) routing was not consiered. Yet, for larger projects with more end points a routing system should be used. FastAPI, just like most other frontend and backend frameworks, pro provides such a routing system out of the box. This way, different routes can "live" in different directories which keeps the code nicely segragated.

My solution, however, takes api versioning into account, which makes upgrading to a higher version or adding more functionalities to a higher versioned api possible, without jeopardizing the currently running api.  

## Relability
Good care was taken to catch errors early e.g. SQLModel is used which uses Pydantic under the hood to check user input. Errors where also tried to be caught whenever they occur to then also display a Reasonable error message or warning. 
Also, all functionalities have corresponding tests (more tests could have been written of course). The tests use their own in memory sqlite database. With these tests in place, one can guarantee a certain behavior and errors can again be caught early.

Where my solution falls short is by fetching the current ETH/USDT price from Binance's api. Since the prices are fetched from Binance's "candle stick" api (```klines```) with a set resolution of 1 min, the price for the most recent transactions (withing the last 60s) may fluctuate because the "candle stick" prices have not yet been ultimately determined. Also, within this 1 min "candle stick" resolution window, the closing price is taken, which may not the exact price of the timestamp of the transaction, which may make the transaction fee returned by the api differ to the transaction fees seen on Etherscan.