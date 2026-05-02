import asyncio

from app.runtime.pipeline import Pipeline
from app.exchange.mexc_stream import MexcStream
from app.domain.state import CandleState
from app.domain.models import Candle

state = CandleState()
pipeline = Pipeline()

last_ts = {}


def handle_message(candle):
    pair = candle["pair"]

    before_len = len(state.get_1m(pair))

    state.update(candle)

    after_len = len(state.get_1m(pair))

    if after_len > before_len:
        closed = state.get_last(pair)
        if not closed:
            return

        print(f"CLOSED 1m: {pair}")
        print("CANDLE:", closed)

        candle_obj = Candle(**closed)

        signal = pipeline.process_candle(candle_obj)

        if signal:
            print("SIGNAL:", signal)


async def main():
    pairs = ["BTC_USDT", "ETH_USDT"]

    stream = MexcStream(pairs, handle_message)

    await stream.start()


if __name__ == "__main__":
    asyncio.run(main())
