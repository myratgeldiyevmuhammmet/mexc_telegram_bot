from collections import defaultdict, deque
from app.domain.models import Candle


class MarketState:
    def __init__(self, max_candles: int = 300):
        self.storage_1m: dict[str, deque[Candle]] = defaultdict(
            lambda: deque(maxlen=max_candles)
        )

    def add_candle(self, candle: Candle):
        self.storage_1m[candle.pair].append(candle)

    def get_closes(self, pair: str) -> list[float]:
        return [c.close for c in self.storage_1m[pair]]

    def get_closes_15m(self, pair: str) -> list[float]:
        candles = list(self.storage_1m[pair])
        closes = []
        for i in range(14, len(candles), 15):
            closes.append(candles[i].close)
        return closes

    def get_closes_1h(self, pair: str) -> list[float]:
        candles = list(self.storage_1m[pair])
        closes = []
        for i in range(59, len(candles), 60):
            closes.append(candles[i].close)
        return closes
