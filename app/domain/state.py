from collections import defaultdict


class CandleState:
    def __init__(self):
        self.last_timestamp = {}
        self.candles_1m = defaultdict(list)

    def update(self, candle: dict):
        pair = candle["pair"]
        ts = candle["timestamp"]

        # если новая свеча (закрылась предыдущая)
        if pair in self.last_timestamp and self.last_timestamp[pair] != ts:
            self.candles_1m[pair].append(candle)
            if len(self.candles_1m[pair]) % 50 == 0:
                print(f"ACCUMULATING: {pair} | candles={len(self.candles_1m[pair])}")
            # ограничим память
            if len(self.candles_1m[pair]) > 200:
                self.candles_1m[pair].pop(0)

        self.last_timestamp[pair] = ts

    def get_1m(self, pair):
        return self.candles_1m[pair]

    def get_last(self, pair):
        if not self.candles_1m[pair]:
            return None
        return self.candles_1m[pair][-1]
