# Pricer App

This is a small demo program, written as a learning exercise.
It implements a simple data store for market data on FastAPI and the Black76 pricing model.

Data storage is implemented on SQLModel and PyDantic.

The code is licensed under the GNU Affero License.

# Running this demo

This is a tiny demo API store market data for options, there is one pricing model, Black76.

### Start the web app
In a terminal, start the webapp:

```bash
$ python pricer_app/main.py
INFO:     Started server process [<PID>]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

Swagger docs are available to describe the API here:

http://0.0.0.0:8000/docs

### Verify the app is up

Use curl to check the app is up:

```bash
curl -X GET "http://localhost:8000/market_data" -H "accept: application/json" 
[]%
```

Since there is no data in the app it returns an empty list.

### Populate the app by uploading data

This is a good time to upload some data:
    
```bash
$ curl -X 'POST' \
  'http://0.0.0.0:8000/market_data' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
    "exchange_code": "NYMEX",
    "contract": "BRN Jun21 Call Strike 50.0 USD",
    "pricing_model": "Black76",
    "market_data": {
        "forward_price": 100.0,
        "strike_price": 50.0,
        "time_to_expiration": 0.5,
        "volatility": 0.2,
        "risk_free_interest_rate": 0.03
    }
}
```

The data is returned, along with an id (for retrieval) and an upload timestamp.

```json
{"exchange_code":"NYMEX","upload_timestamp":"2024-02-13T22:04:02.168780","id":1,"contract":"BRN Jun21 Call Strike 50.0 USD","market_data":"{\"forward_price\": 100.0, \"strike_price\": 50.0, \"time_to_expiration\": 0.5, \"volatility\": 0.2, \"risk_free_interest_rate\": 0.03}"}% 
```

# Retrieving market data:

Endpoints for retrieval are 

/market_data/{option_id}
GET a single market data entry.

/market_data
GET all market data entries.

## Retrieve a market data entry:

Assuming the id of the market data created was, 1:
```bash
$ curl -X 'GET' \
  'http://0.0.0.0:8000/market_data/1' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json'
```

Data is returned:

```json
{"exchange_code":"NYMEX","upload_timestamp":"2024-02-13T22:04:02.168780","id":1,"contract":"BRN Jun21 Call Strike 50.0 USD","market_data":"{\"forward_price\": 100.0, \"strike_price\": 50.0, \"time_to_expiration\": 0.5, \"volatility\": 0.2, \"risk_free_interest_rate\": 0.03}"}
```

# Options Pricing

## Intro

An endpoint to calculate the present value (PV) is provided at 

/option_pricing/{option_id}

The user posts, the option type (call or put), a forward strike price 'F' and an option_id (the id of the market data object uploaded earlier).

Data from the market data object is fetched so that present value can be calculated using Black76.

For reference here is a table of the parameters from the POST and Market Data:
### Data from POST

| Parameter         | Description                            | Example Data Type |
|-------------------|----------------------------------------|-------------------|
| option_type       | Type of the option (e.g., Call or Put) | String            |
| K (Strike Price)  | Strike price of the option             | Float             |

### Market Data
| Parameter            | Description                                       | Type  |
|----------------------|---------------------------------------------------|-------|
| F (Forward Price)    | Forward price of the asset underlying the option  | Float |
| r (Risk-Free Rate)   | Risk-free interest rate applicable to the option  | Float |
| sigma (Volatility)   | Volatility of the underlying asset                | Float |
| T (Time to Maturity) | Time remaining until the option's expiration date | Float |


### Demo

```bash
$ curl -X POST "http://<your-server-address>/option_pricing/1" \
     -H "Content-Type: application/json" \
     -d '{
           "option_type": "call",
           "K": 50.0
         }'
```

A present value is returned:

```json
{"pv":49.25559786808824}
```

