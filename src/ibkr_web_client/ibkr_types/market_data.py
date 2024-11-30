from enum import Enum


class MarketDataTimeline(Enum):
    REAL_TIME = "R"  # Data is relayed back in real time without delay, market data subscription(s) are required
    DELAYED = "D"  # Data is relayed back 15-20 min delayed
    FROZEN = "Z"  # Last recorded data at market close, relayed back in real time
    FROZEN_DELAYED = "Y"  # Last recorded data at market close, relayed back delayed
    NOT_SUBSCRIBED = "N"  # User does not have the required market data subscription(s) to relay back either real time or delayed data


class MarketDataStructure(Enum):
    SNAPSHOT = "P"  # Snapshot request is available for contract
    CONSOLIDATED = "p"  # Market data is aggregated across multiple exchanges or venues


class MarketDataType(Enum):
    BOOK = "B"  # Top of the book data is available for contract


class MarketDataAvailability:
    """
    Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#md-availability
    """

    def __init__(self, timeline: MarketDataTimeline, structure: MarketDataStructure, data_type: MarketDataType):
        self.timeline = timeline
        self.structure = structure
        self.data_type = data_type

    @property
    def value(self):
        return f"{self.__empty_or_value(self.timeline)}{self.__empty_or_value(self.structure)}{self.__empty_or_value(self.data_type)}"

    def __empty_or_value(self, enum_obj: Enum) -> str:
        return enum_obj.value if enum_obj else ""


class MarketDataField(Enum):
    """
    Source: https://www.interactivebrokers.com/campus/ibkr-api-page/cpapi-v1/#market-data-fields
    """
    LAST_PRICE = 31  # The last price at which the contract traded. May contain one of the following prefixes: C – Previous day’s closing price. H – Trading has halted.
    SYMBOL = 55
    TEXT = 58
    HIGH = 70  # Current day high price
    LOW = 71  # Current day low price
    MARKET_VALUE = 73  # The current market value of your position in the security. Market Value is calculated with real time market data (even when not subscribed to market data).
    AVG_PRICE = 74  # The average price of the position.
    UNREALIZED_PNL = 75  # Unrealized profit or loss. Unrealized PnL is calculated with real time market data (even when not subscribed to market data).
    FORMATTED_POSITION = 76
    FORMATTED_UNREALIZED_PNL = 77
    DAILY_PNL = 78  # Your profit or loss of the day since prior close. Daily PnL is calculated with real time market data (even when not subscribed to market data).
    REALIZED_PNL = 79  # Realized profit or loss. Realized PnL is calculated with real time market data (even when not subscribed to market data).
    UNREALIZED_PNL_PRCT = 80  # Unrealized profit or loss expressed in percentage.
    CHANGE = 82  # The difference between the last price and the close on the previous trading day
    CHANGE_PRCT = 83  # The difference between the last price and the close on the previous trading day in percentage.
    BID_PRICE = 84  # The highest-priced bid on the contract.
    ASK_SIZE = 85  # The number of contracts or shares offered at the ask price. For US stocks, the number displayed is divided by 100.
    ASK_PRICE = 86  # The lowest-priced offer on the contract.
    VOLUME = 87  # Volume for the day, formatted with ‘K’ for thousands or ‘M’ for millions. For higher precision volume refer to field 7762.
    BID_SIZE = 88  # The number of contracts or shares bid for at the bid price. For US stocks, the number displayed is divided by 100.
    EXCHANGE = 6004
    CONID = 6008  # Contract identifier from IBKR’s database.
    SECTYPE = 6070  # The asset class of the instrument.
    MONTHS = 6072
    REGULAR_EXPIRY = 6073
    MARKER_FOR_MARKET_DATA_DELIVERY_METHOD_SIMILAR_TO_REQUEST_ID = 6119
    UNDERLYING_CONID_USE__TRSRV_SECDEF_TO_GET_MORE_INFORMATION_ABOUT_THE_SECURITY = 6457
    SERVICE_PARAMS = 6508
    MARKET_DATA_AVAILABILITY = 6509  # Data is relayed back in real time without delay, market data subscription(s) are required. Delayed – Data is relayed back 15-20 min delayed. Frozen – Last recorded data at market close, relayed back in real time. Frozen Delayed – Last recorded data at market close, relayed back delayed. Not Subscribed – User does not have the required market data subscription(s) to relay back either real time or delayed data. Snapshot – Snapshot request is available for contract. Consolidated – Market data is aggregated across multiple exchanges or venues. Book – Top of the book data is available for contract.
    COMPANY_NAME = 7051
    ASK_EXCH = 7057  # Displays the exchange(s) offering the SMART price. A=AMEX, C=CBOE, I=ISE, X=PHLX, N=PSE, B=BOX, Q=NASDAQOM, Z=BATS, W=CBOE2, T=NASDAQBX, M=MIAX, H=GEMINI, E=EDGX, J=MERCURY
    LAST_EXCH = 7058  # Displays the exchange(s) offering the SMART price. A=AMEX, C=CBOE, I=ISE, X=PHLX, N=PSE, B=BOX, Q=NASDAQOM, Z=BATS, W=CBOE2, T=NASDAQBX, M=MIAX, H=GEMINI, E=EDGX, J=MERCURY
    LAST_SIZE = 7059  # The number of unites traded at the last price
    BID_EXCH = 7068  # Displays the exchange(s) offering the SMART price. A=AMEX, C=CBOE, I=ISE, X=PHLX, N=PSE, B=BOX, Q=NASDAQOM, Z=BATS, W=CBOE2, T=NASDAQBX, M=MIAX, H=GEMINI, E=EDGX, J=MERCURY
    IMPLIED_VOL_HIST_VOL_PRCT = 7084  # The ratio of the implied volatility over the historical volatility, expressed as a percentage.
    PUT_CALL_INTEREST = 7085  # Put option open interest/call option open interest for the trading day.
    PUT_CALL_VOLUME = 7086  # Put option volume/call option volume for the trading day.
    HIST_VOL_PRCT = 7087  # 30-day real-time historical volatility.
    HIST_VOL_CLOSE_PRCT = 7088  # Shows the historical volatility based on previous close price.
    OPT_VOLUME = 7089  # Option Volume
    CONID_AND_EXCHANGE = 7094
    CANBETRADED = 7184  # If contract is a trade-able instrument. Returns 1(true) or 0(false).
    CONTRACT_DESCRIPTION_1 = 7219
    CONTRACT_DESCRIPTION_2 = 7220
    LISTING_EXCHANGE = 7221
    INDUSTRY = 7280  # Displays the type of industry under which the underlying company can be categorized.
    CATEGORY = 7281  # Displays a more detailed level of description within the industry under which the underlying company can be categorized.
    AVERAGE_VOLUME = 7282  # The average daily trading volume over 90 days.
    OPTION_IMPLIED_VOL_PRCT = 7283  # A prediction of how volatile an underlying will be in the future.At the market volatility estimated for a maturity thirty calendar days forward of the current trading day, and based on option prices from two consecutive expiration months. To query the Implied Vol. % of a specific strike refer to field 7633.
    HISTORICAL_VOLATILITY_PRCT = 7284  # Deprecated, see field 7087
    PUT_CALL_RATIO = 7285
    DIVIDEND_AMOUNT = 7286  # Displays the amount of the next dividend.
    DIVIDEND_YIELD_PRCT = 7287  # This value is the toal of the expected dividend payments over the next twelve months per share divided by the Current Price and is expressed as a percentage. For derivatives, this displays the total of the expected dividend payments over the expiry date
    EX_DATE_OF_THE_DIVIDEND = 7288
    MARKET_CAP = 7289
    P_E = 7290
    EPS = 7291
    COST_BASIS = 7292  # Your current position in this security multiplied by the average price and multiplier.
    WEEK_52_HIGH = 7293  # The highest price for the past 52 weeks.
    WEEK_52_LOW = 7294  # The lowest price for the past 52 weeks.
    OPEN = 7295  # Today’s opening price.
    CLOSE = 7296  # Today’s closing price.
    DELTA = 7308  # The ratio of the change in the price of the option to the corresponding change in the price of the underlying.
    GAMMA = 7309  # The rate of change for the delta with respect to the underlying asset’s price.
    THETA = 7310  # A measure of the rate of decline the value of an option due to the passage of time.
    VEGA = 7311  # The amount that the price of an option changes compared to a 1% change in the volatility.
    OPT_VOLUME_CHANGE_PRCT = 7607  # Today’s option volume as a percentage of the average option volume.
    IMPLIED_VOL_PRCT = 7633  # The implied volatility for the specific strike of the option in percentage. To query the Option Implied Vol. % from the underlying refer to field 7283.
    MARK = 7635  # The mark price is, the ask price if ask is less than last price, the bid price if bid is more than the last price, otherwise it’s equal to last price.
    SHORTABLE_SHARES = 7636  # Number of shares available for shorting.
    FEE_RATE = 7637  # Interest rate charged on borrowed shares.
    OPTION_OPEN_INTEREST = 7638
    PRCT_OF_MARK_VALUE = 7639  # Displays the market value of the contract as a percentage of the total market value of the account. Mark Value is calculated with real time market data (even when not subscribed to market data).
    SHORTABLE = 7644  # Describes the level of difficulty with which the security can be sold short.
    MORNINGSTAR_RATING = 7655  # Displays Morningstar Rating provided value. Requires Morningstar subscription.
    DIVIDENDS = 7671  # This value is the total of the expected dividend payments over the next twelve months per share.
    DIVIDENDS_TTM = 7672  # This value is the total of the expected dividend payments over the last twelve months per share.
    EMA200 = 7674  # Exponential moving average (N=200).
    EMA100 = 7675  # Exponential moving average (N=100).
    EMA50 = 7676  # Exponential moving average (N=50).
    EMA20 = 7677  # Exponential moving average (N=20).
    PRICE_EMA200 = 7678  # Price to Exponential moving average (N=200) ratio -1, displayed in percents.
    PRICE_EMA100 = 7679  # Price to Exponential moving average (N=100) ratio -1, displayed in percents.
    PRICE_EMA50 = 7724  # Price to Exponential moving average (N=50) ratio -1, displayed in percents.
    PRICE_EMA20 = 7681  # Price to Exponential moving average (N=20) ratio -1, displayed in percents.
    CHANGE_SINCE_OPEN = 7682  # The difference between the last price and the open price.
    UPCOMING_EVENT = 7683  # Shows the next major company event. Requires Wall Street Horizon subscription.
    UPCOMING_EVENT_DATE = 7684  # The date of the next major company event. Requires Wall Street Horizon subscription.
    UPCOMING_ANALYST_MEETING = 7685  # The date and time of the next scheduled analyst meeting. Requires Wall Street Horizon subscription.
    UPCOMING_EARNINGS = 7686  # The date and time of the next scheduled earnings/earnings call event. Requires Wall Street Horizon subscription.
    UPCOMING_MISC_EVENT = 7687  # The date and time of the next shareholder meeting, presentation or other event. Requires Wall Street Horizon subscription.
    RECENT_ANALYST_MEETING = 7688  # The date and time of the most recent analyst meeting. Requires Wall Street Horizon subscription.
    RECENT_EARNINGS = 7689  # The date and time of the most recent earnings/earning call event. Requires Wall Street Horizon subscription.
    RECENT_MISC_EVENT = 7690  # The date and time of the most recent shareholder meeting, presentation or other event. Requires Wall Street Horizon subscription.
    PROBABILITY_OF_MAX_RETURN_1 = 7694  # Customer implied probability of maximum potential gain.
    BREAK_EVEN = 7695  # Break even points
    SPX_DELTA = 7696  # Beta Weighted Delta is calculated using the formula; Delta x dollar adjusted beta, where adjusted beta is adjusted by the ratio of the close price.
    FUTURES_OPEN_INTEREST = 7697  # Total number of outstanding futures contracts
    LAST_YIELD = 7698  # Implied yield of the bond if it is purchased at the current last price. Last yield is calculated using the Last price on all possible call dates. It is assumed that prepayment occurs if the bond has call or put provisions and the issuer can offer a lower coupon rate based on current market rates. The yield to worst will be the lowest of the yield to maturity or yield to call (if the bond has prepayment provisions). Yield to worse may be the same as yield to maturity but never higher.
    BID_YIELD = 7699  # Implied yield of the bond if it is purchased at the current bid price. Bid yield is calculated using the Ask on all possible call dates. It is assumed that prepayment occurs if the bond has call or put provisions and the issuer can offer a lower coupon rate based on current market rates. The yield to worst will be the lowest of the yield to maturity or yield to call (if the bond has prepayment provisions). Yield to worse may be the same as yield to maturity but never higher.
    PROBABILITY_OF_MAX_RETURN_2 = 7700  # Customer implied probability of maximum potential gain.
    PROBABILITY_OF_MAX_LOSS = 7702  # Customer implied probability of maximum potential loss.
    PROFIT_PROBABILITY = 7703  # Customer implied probability of any gain.
    ORGANIZATION_TYPE = 7704
    DEBT_CLASS = 7705
    RATINGS = 7706  # Ratings issued for bond contract.
    BOND_STATE_CODE = 7707
    BOND_TYPE = 7708
    LAST_TRADING_DATE = 7714
    ISSUE_DATE = 7715
    BETA = 7718  # Beta is against standard index.
    ASK_YIELD = 7720  # Implied yield of the bond if it is purchased at the current offer. Ask yield is calculated using the Bid on all possible call dates. It is assumed that prepayment occurs if the bond has call or put provisions and the issuer can offer a lower coupon rate based on current market rates. The yield to worst will be the lowest of the yield to maturity or yield to call (if the bond has prepayment provisions). Yield to worse may be the same as yield to maturity but never higher.
    PRIOR_CLOSE = 7741  # Yesterday’s closing price
    VOLUME_LONG = 7762  # High precision volume for the day. For formatted volume refer to field 87.
    HASTRADINGPERMISSIONS = 7768  # if user has trading permissions for specified contract. Returns 1(true) or 0(false).
    DAILY_PNL_RAW = 7920  # Your profit or loss of the day since prior close. Daily PnL is calculated with real-time market data (even when not subscribed to market data).
    COST_BASIS_RAW = 7921  # Your current position in this security multiplied by the average price and and multiplier.

