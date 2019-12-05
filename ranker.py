import argparse
import re
import requests

from lxml import html
from concurrent.futures import ThreadPoolExecutor, as_completed


ZACKS_URL = "https://www.zacks.com/stock/quote"
XPATH = '//*[@id="premium_research"]/div/table/tbody/tr[1]/td/span/text()'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36'
}


class ZacksRanker:

    def get_for_symbol(self, symbol):
        try:
            response = requests.get(f"{ZACKS_URL}/{symbol}", headers=HEADERS)
        except Exception as e:
            print(e)
            return {symbol: -1}

        tree = html.fromstring(response.content)
        rank = tree.xpath(XPATH)
        return {symbol: int(rank[0]) if len(rank) else 0}

    def get_for_list(self, symbols):
        processes = list()
        result = dict()

        with ThreadPoolExecutor() as executor:
            for symbol in symbols:
                processes.append(executor.submit(self.get_for_symbol, symbol))

        for task in as_completed(processes):
            result.update(task.result())

        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("symbol", help="Stock symbol/ticker, f.e. QCOM")
    args = parser.parse_args()
    ranker = ZacksRanker()
    print(f'Parsing Zacks Rank for symbol "{args.symbol}"...')
    print(ranker.get_for_symbol(args.symbol))
