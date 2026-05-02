import requests


class TelegramSender:
    def __init__(self, token: str, chat_id: int):
        self.token = token
        self.chat_id = chat_id

    def send(self, text: str):
        url = f"https://api.telegram.org/bot{self.token}/sendMessage"

        payload = {
            "chat_id": self.chat_id,
            "text": text,
        }

        try:
            requests.post(url, json=payload)
        except Exception as e:
            print("TELEGRAM ERROR:", e)
