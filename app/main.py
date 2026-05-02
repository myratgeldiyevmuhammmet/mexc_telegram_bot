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
        signal = pipeline.process_candle(candle_obj)

        if signal:
            msg = (
                f"🚀 SIGNAL\n"
                f"Pair: {signal.pair}\n"
                f"Type: {signal.direction}\n"
                f"Price: {signal.price}\n"
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
