from enum import Enum
from typing import List
import datetime


class LogicBind(Enum):
    AND = "a"
    OR = "o"
    END = "n"


class Operator(Enum):
    GREATER_THAN = ">="
    LESS_THAN = "<="


class ConditionType(Enum):
    PRICE = 1
    TIME = 3
    MARGIN = 4
    TRADE = 5
    VOLUME = 6
    MTA_MARKET = 7
    MTA_POSITION = 8
    MTA_ACCOUNT_DAILY_PNL = 9


class TimeInForceType(Enum):
    # Good Til Canceled
    GTC = "GTC"
    # Good Til Date
    GTD = "GTD"


class TIFAlert:

    def __init__(self, tif: TimeInForceType, expireTime: datetime.datetime):
        self.tif = tif.value
        self.expireTime = expireTime.strftime("%Y%m%d-%H:%M:%S") if expireTime else None


class GTCAlert(TIFAlert):
    def __init__(self):
        super().__init__(TimeInForceType.GTC, None)


class GTDAlert(TIFAlert):
    def __init__(self, expireTime: datetime.datetime):
        super().__init__(TimeInForceType.GTD, expireTime)


class Condition:
    DEFAULT_VALUE = "*"
    DEFAULT_TIMEZONE = None

    # TODO: add type for timezone
    def __init__(self, condition_type: ConditionType, value, timezone: str = None) -> None:
        self.type = condition_type.value
        self.value = value or self.DEFAULT_VALUE
        self.timezone = timezone or self.DEFAULT_TIMEZONE


class PriceCondition(Condition):
    def __init__(self, value: float = None) -> None:
        super().__init__(ConditionType.PRICE, str(value) if value else value)


# class TimeCondition(Condition):
#     def __init__(self) -> None:
#         super().__init__(ConditionType.TIME, None)


class MarginCondition(Condition):
    def __init__(self, value: float = None) -> None:
        super().__init__(ConditionType.MARGIN, str(value) if value else value)


class TradeCondition(Condition):
    def __init__(self) -> None:
        super().__init__(ConditionType.TRADE, None)


# class VolumeCondition(Condition):
#     pass


# class MtaMarketCondition(Condition):
#     def __init__(self, timezone: str, value: float = None) -> None:
#         super().__init__(ConditionType.MTA_MARKET, str(value) if value else value, timezone)


# class MtaPositionCondition(Condition):
#     def __init__(self, timezone: str, value: float = None) -> None:
#         super().__init__(ConditionType.MTA_POSITION, str(value) if value else value, timezone)


# class MtaAccountDailyPnlCondition(Condition):
#     def __init__(self, timezone: str, value: float = None) -> None:
#         super().__init__(ConditionType.MTA_ACCOUNT_DAILY_PNL, str(value) if value else value, timezone)


class AlertCondition:
    def __init__(
        self,
        contract_id: int,
        exchange: str,
        logic_bind: LogicBind,
        operator: Operator,
        # triggerMethod: str,
        condition: Condition,
    ):
        self.conidex = f"{contract_id}@{exchange}"
        self.logic_bind = logic_bind.value
        self.operator = operator.value
        self.trigger_method = "0"
        self.type = condition.type
        self.value = condition.value
        self.timezone = condition.timezone

    def __dict__(self):
        d = {
            "conidex": self.conidex,
            "logicBind": self.logic_bind,
            "operator": self.operator,
            "triggerMethod": self.trigger_method,
            "type": self.type,
            "value": self.value,
        }
        if self.timezone:
            d["timeZone"] = self.timezone
        return d


class Alert:
    def __init__(
        self,
        alert_name: str,
        alert_message: str,
        alert_repeatable: bool,
        outside_rth: bool,
        send_message: bool,
        email: str,
        tif_alert: TIFAlert,
        conditions: List[AlertCondition],
        iTWS_orders_only: bool = False,
        show_popup: bool = False,
    ):
        self.alert_name = alert_name
        self.alert_message = alert_message
        self.alert_repeatable = int(alert_repeatable)
        self.outside_rth = int(outside_rth)
        self.send_message = int(send_message)
        self.email = email
        self.tif = tif_alert.tif
        self.expire_time = tif_alert.expireTime
        self.iTWS_orders_only = int(iTWS_orders_only)
        self.show_popup = int(show_popup)
        self.conditions = conditions

    def __dict__(self):
        return {
            "alertMessage": self.alert_message,
            "alertName": self.alert_name,
            "expireTime": self.expire_time,
            "alertRepeatable": self.alert_repeatable,
            "outsideRth": self.outside_rth,
            "sendMessage": self.send_message,
            "email": self.email,
            "iTWSOrdersOnly": self.iTWS_orders_only,
            "showPopup": self.show_popup,
            "tif": self.tif,
            "conditions": [condition.__dict__() for condition in self.conditions],
        }
