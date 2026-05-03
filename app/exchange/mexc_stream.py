import asyncio
from typing import List, Callable
import json
import websockets


class MexcStream:
    def __init__(self, pairs: List[str], on_message: Callable):
        self.pairs = pairs
        self.on_message = on_message

    async def start(self):
        batches = self._split_batches(self.pairs, batch_size=20)

        tasks = []
        for batch in batches:
            tasks.append(asyncio.create_task(self._run_batch(batch)))

        await asyncio.gather(*tasks)

    async def _ping(self, ws):
        while True:
            try:
                await ws.send('{"method":"ping"}')
                await asyncio.sleep(30)
            except Exception as e:
                print("PING ERROR:", e)
                break

    async def _run_batch(self, pairs: list[str]):
        while True:
            try:
                await self._connect_and_run(pairs)
            except Exception as e:
                print("RECONNECT:", pairs, e)
                await asyncio.sleep(5)

    async def _connect_and_run(self, pairs: list[str]):
        url = "wss://contract.mexc.com/edge"

        async with websockets.connect(url, ping_timeout=20, close_timeout=10) as ws:
            # подписка
            for pair in pairs:
                sub_msg = {
                    "method": "sub.kline",
                    "param": {"symbol": pair, "interval": "Min1"},
                }
                await ws.send(json.dumps(sub_msg))

            print("SUBSCRIBED:", pairs)

            asyncio.create_task(self._ping(ws))

            while True:
                msg = await asyncio.wait_for(ws.recv(), timeout=30)
                data = json.loads(msg)

                # ❌ УБРАЛИ RAW (очень важно)

                if data.get("channel") == "push.kline":
                    k = data["data"]

                    candle = {
                        "pair": k["symbol"],
                        "timeframe": k["interval"],
                        "timestamp": k["t"],
                        "open": float(k["o"]),
                        "high": float(k["h"]),
                        "low": float(k["l"]),
                        "close": float(k["c"]),
                        "volume": float(k["a"]),
                    }

                    await self.on_message(candle)

    def _split_batches(self, items: List[str], batch_size: int):
        for i in range(0, len(items), batch_size):
            yield items[i : i + batch_size]
