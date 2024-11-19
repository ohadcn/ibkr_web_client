"""Enum definitions for IBKR API Client."""

from enum import Enum


class SortingOrder(Enum):
    """Sorting order for API requests."""
    ASCENDING = "a"
    DESCENDING = "d"


class Period(Enum):
    """Time period for performance and historical data requests."""
    ONE_DAY = "1D"
    ONE_WEEK = "7D"
    MONTH_TO_DATE = "MTD"
    ONE_MONTH = "1M"
    YEAR_TO_DATE = "YTD"
    ONE_YEAR = "1Y" 


class IBKRRealms(Enum):
    TEST = "test_realm"
    LIMITED_POA = "limited_poa"
