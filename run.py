import argparse
import pandas

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
    return df[condition]

def filter_by_last_increase(df, min_grow):
    condition = df['Inc.'] > min_grow
    return df[condition]

def format_columns(df):
    df['Yrs'] = df['Yrs'].map('{:,.0f}'.format)
    df['Price'] = df['Price'].map('${:,.2f}'.format)
    df['Dividend'] = df['Dividend'].map('${:,.2f}'.format)
    df['Yield'] = df['Yield'].map('{:,.2f}%'.format)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--group", 
                        default="champions",
                        choices=['champions', 'contenders'],
                        required=True,
                        help="List champions(>25y) or contenders(>10y) of consequent dividend increase")
    parser.add_argument("-d", "--min-dividend", type=float, default=2.5)
    parser.add_argument("-r", "--min-grow", type=float, default=7.0)
    args = parser.parse_args()
    if args.group == 'champions':
        SHEET_NAME = "Champions"
    elif args.group == 'contenders':
        SHEET_NAME = "Contenders"

    pandas.options.display.float_format = ' {:,.2f}'.format 
    df = pandas.read_excel(SOURCE, sheet_name=SHEET_NAME, skiprows=5, usecols=COLUMNS)
    df = filter_out_summary(df)
    df = filter_by_dividend(df, args.min_dividend)
    df = filter_by_dgr(df, args.min_grow)
    df = filter_by_last_increase(df, args.min_grow)
    format_columns(df)
    print(df)
