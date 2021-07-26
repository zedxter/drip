import yfinance

from concurrent.futures import ThreadPoolExecutor, as_completed



class CashFlowParser():

    def _get_ratio(self, series):
        dividends = self._get_value(series, 'trailingCashDividendsPaid')
        free_cash = self._get_value(series, 'trailingFreeCashFlow')
        return abs(float(dividends) / free_cash) * 100

    def get_for_symbol(self, symbol):
        try:
            ticker = yfinance.Ticker(symbol)
            info = ticker.info
            dividends = info.get('trailingAnnualDividendRate', 0) * info.get('floatShares', 0)
            free_cash = info.get('freeCashflow', 0)
            return {
                symbol: {
                    'dividend_paid': dividends,
                    'free_cash_flow': free_cash,
                    'cash_flow_ratio': abs(float(dividends) / free_cash) * 100
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


class DivParser():

    def get_for_symbol(self, symbol):
        try:
            ticker = yfinance.Ticker(symbol)
            info = ticker.info
            return {
                symbol: {
                    'yield': info.get('trailingAnnualDividendRate', 0),
                    'average5': info.get('fiveYearAvgDividendYield', 0)
                }
            }
        except:
            return {symbol: {}}


if __name__ == "__main__":
    parser = CashFlowParser()
    div_parser = DivParser()
    data = parser.get_for_symbol("TROW")
    print(data)
    div_data = div_parser.get_for_symbol("TROW")
    print(div_data)

