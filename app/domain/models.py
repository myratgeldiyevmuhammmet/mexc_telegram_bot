from dataclasses import dataclass


@dataclass
class Candle:
    pair: str
    timeframe: str  # "1m", "15m", "1h"
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: int


@dataclass
class Signal:
    pair: str

    price: float
    move_percent: float

    rsi_15m: float
    rsi_1h: float

    timestamp: int

    timeframe: str  # "15m"
    direction: str  # "LONG" or "SHORT"
