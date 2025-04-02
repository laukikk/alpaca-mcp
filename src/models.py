from pydantic import BaseModel, Field
from typing import Optional, List, Union
from uuid import UUID
from datetime import datetime
from enum import Enum

from alpaca.data.timeframe import TimeFrame

# Enums
class AlpacaOrderStatus(str, Enum):
    OPEN = 'open'
    CLOSED = 'closed'
    ALL = 'all'
    NEW = 'new'
    ACCEPTED = 'accepted'
    FILLED = 'filled'
    EXPIRED = 'expired'
    CANCELED = 'canceled'
    REPLACED = 'replaced'

class AlpacaOrderSide(str, Enum):
    BUY = 'buy'
    SELL = 'sell'

class AlpacaOrderType(str, Enum):
    MARKET = 'market'
    LIMIT = 'limit'
    STOP = 'stop'
    STOP_LIMIT = 'stop_limit'
    TRAILING_STOP = 'trailing_stop'

class AlpacaPositionSide(str, Enum):
    LONG = 'long'
    SHORT = 'short'

class AlpacaTimeInForce(str, Enum):
    DAY = 'day'
    GTC = 'gtc'
    OPG = 'opg'
    CLS = 'cls'
    IOC = 'ioc'
    FOK = 'fok'
    
class AlpacaTimeFrame(str, Enum):
    MINUTE = 'Min'
    HOUR = 'Hour'
    DAY = 'Day'
    WEEK = 'Week'
    MONTH = 'Month'
    
    def to_timeframe(self) -> TimeFrame:
        mapping = {
            'Min': TimeFrame.Minute,
            'Hour': TimeFrame.Hour,
            'Day': TimeFrame.Day,
            'Week': TimeFrame.Week,
            'Month': TimeFrame.Month,
        }
        return mapping[self.value]

class AssetClass(str, Enum):
    US_EQUITY = "us_equity"
    CRYPTO = "crypto"
    US_OPTION = "us_option"

class AssetExchange(str, Enum):
    OTC = "OTC"
    NYSE = "NYSE"
    NASDAQ = "NASDAQ"
    EMPTY = ""
    CRYPTO = "CRYPTO"
    AMEX = "AMEX"
    ARCA = "ARCA"
    BATS = "BATS"
    UNKNOWN = "UNKNOWN"
    
    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN
    

class AssetStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

# Pydantic Models
class AlpacaOrderRequest(BaseModel):
    symbol: str
    qty: Union[int, float]
    side: AlpacaOrderSide
    type: AlpacaOrderType
    time_in_force: AlpacaTimeInForce
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    client_order_id: Optional[str] = None
    extended_hours: Optional[bool] = False

class AlpacaOrder(BaseModel):
    id: UUID
    client_order_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    submitted_at: Optional[datetime]
    filled_at: Optional[datetime]
    expired_at: Optional[datetime]
    canceled_at: Optional[datetime]
    symbol: str
    qty: Union[int, float]
    filled_qty: Union[int, float]
    type: AlpacaOrderType
    side: AlpacaOrderSide
    status: AlpacaOrderStatus
    time_in_force: AlpacaTimeInForce
    limit_price: Optional[float]
    stop_price: Optional[float]
    filled_avg_price: Optional[float]

class AlpacaPosition(BaseModel):
    symbol: str
    qty: Union[int, float]
    avg_entry_price: float
    market_value: float
    cost_basis: float
    unrealized_pl: float
    unrealized_plpc: float
    current_price: float
    lastday_price: float
    change_today: float
    side: AlpacaPositionSide

class AlpacaAccount(BaseModel):
    id: UUID
    account_number: str
    status: str
    currency: str
    buying_power: float
    regt_buying_power: float
    daytrading_buying_power: float
    non_marginable_buying_power: float
    cash: float
    portfolio_value: float
    pattern_day_trader: bool
    trading_blocked: bool
    transfers_blocked: bool
    trade_suspended_by_user: bool
    maintenance_margin: float
    last_maintenance_margin: float
    initial_margin: float
    last_equity: float
    equity: float
    daytrade_count: int
    multiplier: float
    sma: float

    class Config:
        extra = "ignore"

class AlpacaAsset(BaseModel):
    id: UUID
    symbol: str
    name: str
    exchange: AssetExchange
    asset_class: AssetClass
    easy_to_borrow: bool
    fractionable: bool
    marginable: bool
    shortable: bool
    tradable: bool
    status: AssetStatus
    attributes: List[str] = []
    maintenance_margin_requirement: Optional[float] = None
    min_order_size: Optional[Union[int, float]] = None
    min_trade_increment: Optional[Union[int, float]] = None
    price_increment: Optional[float] = None
    
    class Config:
        extra = "ignore"

class AlpacaMarketCalendar(BaseModel):
    date: str
    open: str
    close: str
    session_open: str
    session_close: str

class AlpacaQuote(BaseModel):
    symbol: str
    bid_exchange: str
    bid_price: float
    bid_size: int
    ask_price: float
    ask_size: int
    conditions: List[str]
    tape: str
    timestamp: datetime

class AlpacaBar(BaseModel):
    symbol: str
    open: float
    high: float
    low: float
    close: float
    volume: int
    timestamp: datetime