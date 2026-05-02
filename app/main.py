import asyncio

from app.runtime.pipeline import Pipeline
from app.exchange.mexc_stream import MexcStream
from app.domain.state import CandleState
from app.domain.models import Candle
from app.infrastructure.telegram.sender import TelegramSender
from app.core.config import settings
from app.exchange.mexc_pairs import get_usdt_pairs

state = CandleState()
pipeline = Pipeline()

telegram = TelegramSender(
    token=settings.TELEGRAM_TOKEN,
    chat_id=settings.CHAT_ID,
)


async def run_worker(pairs_chunk):
    stream = MexcStream(pairs_chunk, handle_message)
    await stream.start()


def handle_message(candle):
    pair = candle["pair"]

    before_len = len(state.get_1m(pair))
    state.update(candle)
    after_len = len(state.get_1m(pair))

    if after_len > before_len:
        closed = state.get_last(pair)
        if not closed:
            return

        candle_obj = Candle(**closed)
        result = pipeline.process_candle(candle_obj)

        if isinstance(result, tuple):
            signal, rsi_15m, rsi_1h, move_percent = result
        else:
            signal = result
            rsi_15m = rsi_1h = move_percent = None

        if rsi_15m is not None:
            print(
                f"[{pair}] RSI_15m={rsi_15m:.1f} RSI_1h={rsi_1h:.1f} "
                f"move={move_percent:.2f}%"
            )

        if signal:
            print(
                f">>> SIGNAL FIRED: {signal.pair} {signal.direction} @ {signal.price}"
            )
            msg = (
                f"🚀 SIGNAL\n"
                f"Pair: {signal.pair}\n"
                f"Type: {signal.direction}\n"
                f"Price: {signal.price}\n"
                f"Move: {signal.move_percent:.2f}%\n"
                f"RSI 15m: {signal.rsi_15m:.1f}\n"
                f"RSI 1h: {signal.rsi_1h:.1f}\n"
            )
            telegram.send(msg)


async def main():
    pairs = get_usdt_pairs()
    print(f"TOTAL PAIRS: {len(pairs)}")

    chunks = [
        pairs[i : i + settings.BATCH_SIZE]
        for i in range(0, len(pairs), settings.BATCH_SIZE)
    ]

    print(f"WORKERS: {len(chunks)}, BATCH_SIZE: {settings.BATCH_SIZE}")

    await asyncio.gather(*[asyncio.create_task(run_worker(chunk)) for chunk in chunks])


if __name__ == "__main__":
    asyncio.run(main())
