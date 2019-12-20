import pandas

from ranker import ZacksRanker
from balance import CashFlowParser, DivParser

SOURCE = "https://bitly.com/USDividendChampions"
COLUMNS = [0, 1, 3, 4, 8, 9, 17, 18, 19, 20, 21]


class Dripper:

    def __init__(self, group):
        self.df = pandas.read_excel(SOURCE, sheet_name=group, skiprows=5, usecols=COLUMNS)

    def filter_by_symbols(self, symbols):
        self.df = self.df[self.df['Symbol'].isin(symbols)]

    def filter_out_summary(self):
        condition = self.df['Industry'].notnull()
        self.df = self.df[condition]

    def filter_by_dividend(self, min_dividend):
        condition = self.df['Yield'] > min_dividend
        self.df = self.df[condition]

    def filter_by_dgr(self, r):
        condition = self.df['Yield'] + self.df['5-yr'] > 12
        average = (self.df['Inc.'] > r) & (self.df['1-yr'] > r) \
            & (self.df['3-yr'] > r) & (self.df['5-yr'] > r) & (self.df['10-yr'] > r)
        self.df = self.df[condition & average]

    def format_columns(self):
        pandas.options.display.float_format = ' {:,.2f}'.format
        self.df['Yrs'] = self.df['Yrs'].map('{:,.0f}'.format)
        self.df['Price'] = self.df['Price'].map('${:,.2f}'.format)
        self.df['Yield'] = self.df['Yield'].map('{:,.2f}%'.format)
        self.df['Inc.'] = self.df['Inc.'].map('{:,.2f}%'.format)
        self.df['Cover'] = self.df['Cover'].map('{:,.2f}%'.format)
        self.df['Industry'] = self.df['Industry'].map(lambda x: x[:15])
        self.df['Name'] = self.df['Name'].map(lambda x: x[:15])

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
            condition = self.df['CurD'].str.rstrip('%').astype('float') > self.df['5avg'].astype('float')
            self.df = self.df[condition]

    def add_check_mark(self):
        self.df.loc[self.df['Cover'] > 75, 'C'] = ""
        self.df.loc[self.df['Cover'] <= 75, 'C'] = "\u2713"
        self.df.loc[self.df['CurD'].str.rstrip('%').astype('float') < self.df['5avg'].astype('float'), 'T'] = ""
        self.df.loc[self.df['CurD'].str.rstrip('%').astype('float') >= self.df['5avg'].astype('float'), 'T'] = "\u2713"

    def get_table(self):
        return self.df
