from app.core.config import settings


def is_move_valid(move_percent: float) -> bool:
    return abs(move_percent) >= settings.MIN_MOVE_PERCENT


def is_rsi_valid(rsi: float) -> bool:
    return rsi >= settings.RSI_OVERBOUGHT or rsi <= settings.RSI_OVERSOLD


def should_emit_signal(
    move_percent: float,
    rsi_15m: float,
    rsi_1h: float,
) -> bool:
    return (
        is_move_valid(move_percent) and is_rsi_valid(rsi_15m) and is_rsi_valid(rsi_1h)
    )
