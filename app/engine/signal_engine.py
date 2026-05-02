import time
from app.domain.models import Signal
from app.engine.filter import should_emit_signal
from app.core.config import settings


class SignalEngine:
    def __init__(self, cooldown_seconds: int = 900):
        self.last_signal_time: dict[str, float] = {}
        self.cooldown = cooldown_seconds

    def _is_on_cooldown(self, pair: str) -> bool:
        last_time = self.last_signal_time.get(pair)
        if not last_time:
            return False
        return (time.time() - last_time) < self.cooldown

    def _get_direction(self, rsi_15m: float, rsi_1h: float) -> str:
        if rsi_15m > settings.RSI_OVERBOUGHT and rsi_1h > settings.RSI_OVERBOUGHT:
            return "SHORT"
        if rsi_15m < settings.RSI_OVERSOLD and rsi_1h < settings.RSI_OVERSOLD:
            return "LONG"
        return "UNKNOWN"

    def process(
        self,
        pair: str,
        price: float,
        move_percent: float,
        rsi_15m: float,
        rsi_1h: float,
    ) -> Signal | None:

        if not should_emit_signal(move_percent, rsi_15m, rsi_1h):
            return None

        if self._is_on_cooldown(pair):
            return None

        direction = self._get_direction(rsi_15m, rsi_1h)

        signal = Signal(
            pair=pair,
            price=price,
            move_percent=move_percent,
            rsi_15m=rsi_15m,
            rsi_1h=rsi_1h,
            timestamp=int(time.time()),
            timeframe="15m",
            direction=direction,
        )

        self.last_signal_time[pair] = time.time()

        return signal
