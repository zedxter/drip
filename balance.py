import json
import re
import requests

from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_URL = "https://finance.yahoo.com/quote/{}/cash-flow"


class CashFlowParser:

    def _fetch_data(self, symbol):
        response = requests.get(BASE_URL.format(symbol))
        lines = response.text.split("\n")
        line = [l for l in lines if l.startswith('root.App.main')][0]
        line = re.sub(r'^root.App.main =', '', line).strip()
        line = re.sub(r';$', '', line)
        return json.loads(line)

    def _get_value(self, series, val, raw=True):
        try:
            return series[val][0]['reportedValue']['raw' if raw else 'fmt']
        except:
            return -1

    def _get_ratio(self, series):
        dividends = self._get_value(series, 'trailingCashDividendsPaid')
        free_cash = self._get_value(series, 'trailingFreeCashFlow')
        return abs(float(dividends) / free_cash) * 100

    def get_for_symbol(self, symbol):
        try:
            data = self._fetch_data(symbol)
            series = data['context']['dispatcher']['stores']['QuoteTimeSeriesStore']['timeSeries']
            return {
                symbol: {
                    'dividend_paid': self._get_value(series, 'trailingCashDividendsPaid', False),
                    'free_cash_flow': self._get_value(series, 'trailingFreeCashFlow', False),
                    'cash_flow_ratio': self._get_ratio(series)
                }
            }
        except:
            return {symbol: {}}

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
    parser = CashFlowParser()
    data = parser.get_for_list(["O", "LNT", "QCOM"])
    print(data)
