#!/usr/bin/env python
"""Simple demo that uses v2ex_tx2json package."""
from src.v2ex_tx2json import TX2JSON
from dotenv import load_dotenv
import os


def main():
    load_dotenv()
    base_url = os.getenv("BASE_URL", "https://v2ex.com")
    cookie = os.getenv("COOKIE")
    tx = ""

    client = TX2JSON(base_url, cookie=cookie)
    info = client.parse(tx) if tx else None
    print(info)


if __name__ == '__main__':
    main()