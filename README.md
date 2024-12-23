### IBKR API Client

This is just another Python client for the [Interactive Brokers Client Portal REST API](https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#introduction),
which is using the OAuth1.0a protocol for authentication. Main benefits of this client are:
 - You don't need to install Client Portal Gateway
 - Automatic authentication with live session token renewal

### Setup

1. You must have an account on Interactive Brokers.
2. Login to IBKR for Paper or Live trading account.
3. Go to [page](https://www.interactivebrokers.co.uk/oauth/), follow instructions to generate Consumer Key and Tokens.
4. Install package locally for your python environment using `python -m pip install .`
5. Set environment variables (or just hardcode values for config)
    - `API_IBKR_CONSUMER_KEY` - Consumer Key
    - `API_IBKR_TOKEN` - Access Token
    - `API_IBKR_SECRET` - Access Secret Token
    - `API_IBKR_DH_PARAM` - path to dhparam.pem file
    - `API_IBKR_DH_PRIVATE_ENCRYPTION` - path to private_encryption.pem file
    - `API_IBKR_DH_PRIVATE_SIGNATURE` - path to private_signature.pem file
6. Use the client
```python
import os
from pathlib import Path
from ibkr_web_client import IBKRConfig, IBKRHttpClient

config = IBKRConfig(
    token_access=os.getenv("API_IBKR_TOKEN"),     
    token_secret=os.getenv("API_IBKR_SECRET"),
    consumer_key=os.getenv("API_IBKR_CONSUMER_KEY"),
    dh_param_path=Path(os.getenv("API_IBKR_DH_PARAM")),
    dh_private_encryption_path=Path(os.getenv("API_IBKR_DH_PRIVATE_ENCRYPTION")),
    dh_private_signature_path=Path(os.getenv("API_IBKR_DH_PRIVATE_SIGNATURE")),
)

client = IBKRHttpClient(config)
client.portfolio_accounts()
```

### Documentation
- General information: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#introduction
- OAuth for IB https://www.interactivebrokers.com/webtradingapi/oauth.pdf

### TODO notes
 - [x] Authentication
 - [ ] Alerts
   - [x] Create or Modify Alert
    - For now only Price, Margin and Trade conditions are added
   - [x] Get a list of available alerts
   - [x] Get details of a specific alert
   - [ ] Get MTA Alert
   - [x] Activate or deactivate an alert
   - [x] Delete an alert
 - [ ] Accounts
 - [ ] Contract
   - [x] Search the security definition by Contract ID
   - [x] All Conids by Exchange
   - [x] Contract information by Contract ID
   - [x] Currency pairs
   - [x] Currency Exchange Rate
   - [x] Find all Info and rules for a given contract
   - [ ] Search Algo Params by Contract ID
   - [ ] Search Bond Filter Information
   - [ ] Search Contract by Symbol
   - [ ] Search Contract Rules
   - [ ] Search SecDef information by conid
   - [ ] Search Strikes by Underlying Contract ID
   - [x] Search Future by Symbol
   - [x] Search Stocks by Symbol
   - [ ] Trading Schedule by Symbol
 - [ ] FA Allocation Management
 - [ ] FYIs and Notifications
 - [ ] Market Data
   - [x] Live Market Data Snapshot
   - [ ] Regulatory Snapshot 
   - [ ] Historical Market Data
   - [ ] Unsubscribe (Single)
   - [ ] Unsubscribe (All)
 - [ ] Option Chains
 - [ ] Order Monitoring
 - [ ] Orders
 - [x] Portfolio
   - [x] Portfolio Accounts
   - [x] Portfolio Subaccounts
   - [x] Portfolio Subaccounts (Large Account Structures)
   - [x] Specific Account's Portfolio Information
   - [x] Portfolio Allocation (Single)
   - [x] Combination Positions
   - [x] Portfolio Allocation (All)
   - [x] Positions
   - [x] Positions by Conid
   - [x] Invalidate Backend Portfolio Cache
   - [x] Portfolio Summary
   - [x] Portfolio Ledger
   - [x] Position & Contract Info
 - [x] Portfolio Analyst
   - [x] Account Performance
   - [x] Transaction History
 - [ ] Scanner
   - [x] Iserver Scanner Parameters
   - [x] Iserver Market Scanner
   - [ ] HMDS Scanner Parameters (Not working)
   - [ ] HMDS Market Scanner (Not working)
 - [ ] Session
 - [x] Watchlists
   - [x] Create a Watchlist
   - [x] Get All Watchlists
   - [x] Get Watchlist Information
   - [x] Delete a Watchlist

### Tests
To run tests you need to have your own Paper Trading account.
Run tests with `pytest`:
```python
pytest
```
### Disclaimer
 - Use at your own risk
