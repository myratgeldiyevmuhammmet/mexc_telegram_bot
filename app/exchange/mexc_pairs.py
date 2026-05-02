import requests


def get_usdt_pairs():
    url = "https://contract.mexc.com/api/v1/contract/detail"
    data = requests.get(url).json()

    return [item["symbol"] for item in data["data"] if item["symbol"].endswith("_USDT")]
