from collections import defaultdict, deque
from app.domain.models import Candle


class MarketState:
    def __init__(self, max_candles: int = 100):
        self.storage: dict[str, deque[Candle]] = defaultdict(
            lambda: deque(maxlen=max_candles)
        )

    def add_candle(self, candle: Candle):
        self.storage[candle.pair].append(candle)

    def get_closes(self, pair: str) -> list[float]:
        return [c.close for c in self.storage[pair]]

    def get_candles(self, pair: str) -> list[Candle]:
        return list(self.storage[pair])
