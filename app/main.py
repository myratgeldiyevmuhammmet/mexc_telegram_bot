import asyncio
from app.runtime.pipeline import Pipeline
from app.exchange.mexc_stream import MexcStream

pipeline = Pipeline()


def handle_message(data):
    print("CANDLE:", data)


async def main():
    pairs = ["BTC_USDT", "ETH_USDT"]

    stream = MexcStream(pairs, handle_message)

    await stream.start()


if __name__ == "__main__":
    asyncio.run(main())
