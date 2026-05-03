import asyncio
import json
from typing import List, Callable
import websockets


class MexcStream:
    def __init__(self, pairs: List[str], on_message: Callable):
        self.pairs = pairs
        self.on_message = on_message

    async def start(self):
        while True:
            try:
                await self._connect_and_run()
            except Exception as e:
                print(f"RECONNECT: {e}")
                await asyncio.sleep(5)

    async def _ping(self, ws):
        while True:
            try:
                await ws.send('{"method":"ping"}')
                await asyncio.sleep(20)
            except Exception as e:
                print(f"PING ERROR: {e}")
                break

    async def _connect_and_run(self):
        url = "wss://contract.mexc.com/edge"

        async with websockets.connect(
            url,
            ping_timeout=None,
            close_timeout=10,
            max_size=10_000_000,
        ) as ws:
            for pair in self.pairs:
                sub_msg = {
                    "method": "sub.kline",
                    "param": {"symbol": pair, "interval": "Min1"},
                }
                await ws.send(json.dumps(sub_msg))
                await asyncio.sleep(0.05)

            print(f"SUBSCRIBED ALL: {len(self.pairs)} pairs")

            asyncio.create_task(self._ping(ws))

            while True:
                try:
                    msg = await asyncio.wait_for(ws.recv(), timeout=60)
                except asyncio.TimeoutError:
                    print("TIMEOUT: no data for 60s, reconnecting")
                    break

                data = json.loads(msg)

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
