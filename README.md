### IBKR API Client

This is just another Python client for the Interactive Brokers API, which is using the OAuth1.0a protocol for authentication.
Main benefits of this client are:
 - You don't need to install Client Portal Gateway
 - Automatic authentication with live session token renewal

### Setup

1. You must have an account on Interactive Brokers.
2. Go to [page](https://www.interactivebrokers.co.uk/oauth/), follow instructions to generate Consumer Key and Tokens.
3. Install package locally for your python environment using `python -m pip install .`
4. Set environment variables (or just hardcode values for config)
    - `API_IBKR_CONSUMER_KEY` - Consumer Key
    - `API_IBKR_TOKEN` - Access Token
    - `API_IBKR_SECRET` - Access Secret Token
    - `API_IBKR_DH_PARAM` - path to dhparam.pem file
    - `API_IBKR_DH_PRIVATE_ENCRYPTION` - path to private_encryption.pem file
    - `API_IBKR_DH_PRIVATE_SIGNATURE` - path to private_signature.pem file
5. Use the client
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
 - [ ] Accounts
 - [ ] Contract
 - [ ] FA Allocation Management
 - [ ] FYIs and Notifications
 - [ ] Market Data
 - [ ] Option Chains
 - [ ] Order Monitoring
 - [ ] Orders
 - [x] Portfolio
 - [x] Portfolio Analyst
 - [ ] Scanner
 - [ ] Session
 - [ ] Watchlists
 
### Notes
 - Have no clue how to connect to Paper Trading account

### Disclaimer
 - Use at your own risk