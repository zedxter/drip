import argparse
import pandas

from ranker import ZacksRanker
from balance import CashFlowParser, DivParser

SOURCE = "https://bitly.com/USDividendChampions"
COLUMNS = [0, 1, 3, 4, 8, 9, 10, 17, 18, 19, 20, 21]


def filter_out_summary(df):
    condition = df['Industry'].notnull()
    return df[condition]

def filter_by_dividend(df, min_dividend):
    condition = df['Yield'] > min_dividend
    return df[condition]

def filter_by_dgr(df, r):
    condition = df['Yield'] + df['5-yr'] > 12
    average = (df['Inc.'] > r) & (df['1-yr'] > r) & (df['3-yr'] > r) & (df['5-yr'] > r) & (df['10-yr'] > r)
    return df[condition & average]

def format_columns(df):
    pandas.options.display.float_format = ' {:,.2f}'.format
    df['Yrs'] = df['Yrs'].map('{:,.0f}'.format)
    df['Price'] = df['Price'].map('${:,.2f}'.format)
    df['Dividend'] = df['Dividend'].map('${:,.2f}'.format)
    df['Yield'] = df['Yield'].map('{:,.2f}%'.format)
    df['Inc.'] = df['Inc.'].map('{:,.2f}%'.format)
    df['Cover'] = df['Cover'].map('{:,.2f}%'.format)
    df['Industry'] = df['Industry'].map(lambda x: x[:18])
    df['Name'] = df['Name'].map(lambda x: x[:18])

def add_zacks_rank(df, max_rank):
    symbols = df['Symbol']
    ranks = ZacksRanker().get_for_list(symbols)
    df['Z'] = [ranks.get(symbol) for symbol in symbols]
    condition = (df['Z'] <= max_rank) & (df['Z'] > 0)
    return df[condition]

def add_cash_flow(df):
    symbols = df['Symbol']
    parser = CashFlowParser()
    data = dict()
    for symbol in symbols:
        data.update(parser.get_for_symbol(symbol))
    df['D.Paid'] = [data.get(symbol).get('dividend_paid') for symbol in symbols]
    df['Free CF'] = [data.get(symbol).get('free_cash_flow') for symbol in symbols]
    df['Cover'] = [data.get(symbol).get('cash_flow_ratio') for symbol in symbols]
    condition = df['Cover'] < 75 # dividend coverage percentage
    return df[condition]

def add_dividends(df):
    symbols = df['Symbol']
    parser = DivParser()
    data = dict()
    for symbol in symbols:
        data.update(parser.get_for_symbol(symbol))
    df['5avg'] = [data.get(symbol).get('average5') for symbol in symbols]
    df['CurD'] = [data.get(symbol).get('yield') for symbol in symbols]
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--group", 
                        default="champions",
                        choices=['champions', 'contenders', 'challengers'],
                        required=True,
                        help="List champions(>25y), contenders(>10y) or challengers(<10y) of consequent dividend increase")
    parser.add_argument("-d", "--min-dividend", type=float, default=3)
    parser.add_argument("-r", "--min-grow", type=float, default=5)
    parser.add_argument("-z", "--max-zacks", type=int, default=5)
    args = parser.parse_args()

    print("Downloading Excel file...")
    df = pandas.read_excel(SOURCE, sheet_name=args.group.capitalize(), skiprows=5, usecols=COLUMNS)
    print("Analyzing...")
    df = filter_out_summary(df)
    df = filter_by_dividend(df, args.min_dividend)
    df = filter_by_dgr(df, args.min_grow)
    print("Fetching Financial Data...")
    df = add_cash_flow(df)
    print("Fetching Dividend Data...")
    df = add_dividends(df)
    print("Fetching Zacks Rank...")
    df = add_zacks_rank(df, args.max_zacks)
    format_columns(df)
    print(df)

