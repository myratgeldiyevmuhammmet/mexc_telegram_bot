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

        closes = self.state.get_closes(candle.pair)

        if len(closes) < 20:
            return None

        # RSI 15m (используем те же данные пока)
        rsi_15m = calculate_rsi(closes)

        # RSI 1h (пока заглушка, позже сделаем нормально)
        rsi_1h = calculate_rsi(closes)

        # движение за последние N свечей
        move_percent = self._calculate_move(closes)

        signal = self.engine.process(
            pair=candle.pair,
            price=candle.close,
            move_percent=move_percent,
            rsi_15m=rsi_15m,
            rsi_1h=rsi_1h,
        )

        return signal

    def _calculate_move(self, closes: list[float]) -> float:
        if len(closes) < 2:
            return 0

        start = closes[-15]
        end = closes[-1]

        return ((end - start) / start) * 100
