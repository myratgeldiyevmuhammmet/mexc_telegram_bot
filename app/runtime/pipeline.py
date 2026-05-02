from app.runtime.state import MarketState
from app.domain.models import Candle
from app.domain.indicators import calculate_rsi
from app.engine.signal_engine import SignalEngine


class Pipeline:
    def __init__(self):
        self.state = MarketState()
        self.engine = SignalEngine()

    def process_candle(self, candle: Candle):
        self.state.add_candle(candle)

        closes_15m = self.state.get_closes_15m(candle.pair)
        closes_1h = self.state.get_closes_1h(candle.pair)

        if len(closes_15m) < 15 or len(closes_1h) < 15:
            return None

        rsi_15m = calculate_rsi(closes_15m)
        rsi_1h = calculate_rsi(closes_1h)

        move_percent = self._calculate_move_15m(closes_15m)

        signal = self.engine.process(
            pair=candle.pair,
            price=candle.close,
            move_percent=move_percent,
            rsi_15m=rsi_15m,
            rsi_1h=rsi_1h,
        )

        return signal

    def _calculate_move_15m(self, closes: list[float]) -> float:
        if len(closes) < 2:
            return 0
        start = closes[-15] if len(closes) >= 15 else closes[0]
        end = closes[-1]
        return ((end - start) / start) * 100
