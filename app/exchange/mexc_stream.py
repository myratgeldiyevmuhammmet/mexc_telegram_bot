import asyncio
from typing import List, Callable


class MexcStream:
    def __init__(self, pairs: List[str], on_message: Callable):
        self.pairs = pairs
        self.on_message = on_message

    async def start(self):
        batches = self._split_batches(self.pairs, batch_size=50)

        tasks = []
        for batch in batches:
            tasks.append(asyncio.create_task(self._run_batch(batch)))

        await asyncio.gather(*tasks)

    async def _run_batch(self, pairs: List[str]):
        while True:
            # тут позже будет websocket
            await asyncio.sleep(1)

    def _split_batches(self, items: List[str], batch_size: int):
        for i in range(0, len(items), batch_size):
            yield items[i : i + batch_size]
