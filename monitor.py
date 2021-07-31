import requests

class Product:
    def __init__(self, id: int, title: str, handle: str):
        self.id = id
        self.title = title
        self.url = "https://kith.com/products/" + handle


header = {
    "accept-encoding": "gzip, deflate",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36",
}

url = "https://kith.com/products.json"

r = requests.get(url, verify=True, headers=header).json()
products = next(iter(r["products"]))

latest_product = Product(products["id"], products["title"], products["handle"])