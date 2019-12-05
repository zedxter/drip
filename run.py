import argparse
import pandas

from ranker import ZacksRanker

SOURCE = "https://bitly.com/USDividendChampions"
COLUMNS = [0, 1, 3, 4, 8, 9, 10, 17, 18, 19, 20, 21]


def filter_out_summary(df):
    condition = df['Industry'].notnull()
    return df[condition]

def filter_by_dividend(df, min_dividend):
    condition = df['Yield'] > min_dividend
    return df[condition]

def filter_by_dgr(df, min_grow):
    condition = sum([df['1-yr'], df['3-yr'], df['5-yr'], df['10-yr']]) / 4 > min_grow
    increase_only = (df['1-yr'] > 0) & (df['3-yr'] > 0) & (df['5-yr'] > 0) & (df['10-yr'] > 0)
    return df[condition & increase_only]

def filter_by_last_increase(df, min_grow):
    condition = df['Inc.'] > min_grow
    return df[condition]

def format_columns(df):
    pandas.options.display.float_format = ' {:,.2f}'.format
    df['Yrs'] = df['Yrs'].map('{:,.0f}'.format)
    df['Price'] = df['Price'].map('${:,.2f}'.format)
    df['Dividend'] = df['Dividend'].map('${:,.2f}'.format)
    df['Yield'] = df['Yield'].map('{:,.2f}%'.format)
    df['Inc.'] = df['Inc.'].map('{:,.2f}%'.format)
    df['Industry'] = df['Industry'].map(lambda x: x[:20])

def add_zacks_rank(df, max_rank):
    symbols = df['Symbol']
    ranks = ZacksRanker().get_for_list(symbols)
    df['Zacks'] = [ranks.get(symbol) for symbol in symbols]
    condition = (df['Zacks'] <= max_rank) & (df['Zacks'] > 0)
    return df[condition]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--group", 
                        default="champions",
                        choices=['champions', 'contenders', 'challengers'],
                        required=True,
                        help="List champions(>25y), contenders(>10y) or challengers(<10y) of consequent dividend increase")
    parser.add_argument("-d", "--min-dividend", type=float, default=2.5)
    parser.add_argument("-r", "--min-grow", type=float, default=7.0)
    parser.add_argument("-z", "--max-zacks", type=int, default=5)
    args = parser.parse_args()

    print("Downloading Excel file...")
    df = pandas.read_excel(SOURCE, sheet_name=args.group.capitalize(), skiprows=5, usecols=COLUMNS)
    print("Analyzing...")
    df = filter_out_summary(df)
    df = filter_by_dividend(df, args.min_dividend)
    df = filter_by_dgr(df, args.min_grow)
    df = filter_by_last_increase(df, args.min_grow)
    format_columns(df)
    print("Fetching Zacks Rank...")
    df = add_zacks_rank(df, args.max_zacks)
    print(df)

