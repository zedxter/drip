import pandas
import requests

from io import BytesIO
from ranker import ZacksRanker
from balance import CashFlowParser, DivParser

SOURCE = "https://bitly.com/USDividendChampions"
COLUMNS = [0, 1, 3, 4, 5, 6, 8, 16, 17, 18, 19]


class Dripper:

    def __init__(self, group):
        content = requests.get(SOURCE, allow_redirects=True).content
        self.df = pandas.read_excel(BytesIO(content), sheet_name=group, skiprows=2, usecols=COLUMNS)

    def filter_by_symbols(self, symbols):
        self.df = self.df[self.df['Symbol'].isin(symbols)]

    def filter_out_summary(self):
        condition = self.df['Sector'].notnull()
        self.df = self.df[condition]

    def filter_by_dividend(self, min_dividend):
        condition = self.df['Div Yield'] > min_dividend
        self.df = self.df[condition]

    def filter_by_dgr(self, r):
        condition = self.df['Div Yield'] + self.df['DGR 5Y'] > 12
        average = (self.df['DGR 1Y'] > r) & (self.df['DGR 3Y'] > r) \
            & (self.df['DGR 5Y'] > r) & (self.df['DGR 10Y'] > r)
        self.df = self.df[condition & average]

    def format_columns(self):
        pandas.options.display.float_format = ' {:,.2f}'.format
        self.df['No Years'] = self.df['No Years'].map('{:,.0f}'.format)
        self.df['Price'] = self.df['Price'].map('${:,.2f}'.format)
        self.df['Div Yield'] = self.df['Div Yield'].map('{:,.2f}%'.format)
        self.df['Cover'] = self.df['Cover'].map('{:,.2f}%'.format)
        self.df['Sector'] = self.df['Sector'].map(lambda x: x[:15])
        self.df['Company'] = self.df['Company'].map(lambda x: x[:15])
        self.df['D.Paid'] = (self.df['D.Paid'].fillna(0) / 1000000).map('{:,.2f}'.format)
        self.df['Free CF'] = (self.df['Free CF'].fillna(0) / 1000000).map('{:,.2f}'.format)

    def add_zacks_rank(self, max_rank=5):
        symbols = self.df['Symbol']
        ranks = ZacksRanker().get_for_list(symbols)
        self.df['Z'] = [ranks.get(symbol) for symbol in symbols]
        condition = (self.df['Z'] <= max_rank) & (self.df['Z'] > 0)
        self.df = self.df[condition]

    def add_cash_flow(self, coverage=None):
        symbols = self.df['Symbol']
        parser = CashFlowParser()
        data = dict()
        for symbol in symbols:
            data.update(parser.get_for_symbol(symbol))
        self.df['D.Paid'] = [data.get(symbol).get('dividend_paid') for symbol in symbols]
        self.df['Free CF'] = [data.get(symbol).get('free_cash_flow') for symbol in symbols]
        self.df['Cover'] = [data.get(symbol).get('cash_flow_ratio') for symbol in symbols]
        if coverage:
            condition = self.df['Cover'] < coverage
            self.df = self.df[condition]

    def add_dividends(self, best_only=False):
        symbols = self.df['Symbol']
        parser = DivParser()
        data = dict()
        for symbol in symbols:
            data.update(parser.get_for_symbol(symbol))
        self.df['5avg'] = [data.get(symbol).get('average5') for symbol in symbols]
        self.df['CurD'] = [data.get(symbol).get('yield') for symbol in symbols]
        if best_only:
            condition = self.df['CurD'].astype('float') > self.df['5avg'].astype('float')
            self.df = self.df[condition]

    def add_check_mark(self):
        self.df.loc[self.df['Cover'] > 75, 'C'] = ""
        self.df.loc[self.df['Cover'] <= 75, 'C'] = "\u2713"
        self.df.loc[self.df['CurD'].astype('float') < self.df['5avg'].astype('float'), 'T'] = ""
        self.df.loc[self.df['CurD'].astype('float') >= self.df['5avg'].astype('float'), 'T'] = "\u2713"

    def get_table(self):
        return self.df.reset_index(drop=True)
