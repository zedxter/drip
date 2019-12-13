import argparse
import sqlite3
import pandas as pd

from dripper import Dripper

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--add", type=str)
    parser.add_argument("-d", "--delete", type=str)
    parser.add_argument("-l", "--list", action="store_true")
    args = parser.parse_args()

    conn = sqlite3.connect('data.db')
    df = pd.read_sql_query("select * from portfolio;", conn)

    if args.add or args.delete or args.list:
        c = conn.cursor()
        if args.list:
            print(df)
        elif args.add and df[df['symbol'] == args.add].empty:
            c.execute(f"insert into portfolio values('{args.add}')")
            conn.commit()
        elif args.delete:
            c.execute(f"delete from portfolio where symbol = '{args.delete}'")
            conn.commit()
    else:
        print("Downloading Excel file...")
        dripper = Dripper('All CCC')
        dripper.filter_by_symbols(df['symbol'].tolist())
        print("Fetching Financial Data...")
        dripper.add_cash_flow()
        print("Fetching Dividend Data...")
        dripper.add_dividends()
        print("Fetching Zacks Rank...")
        dripper.add_zacks_rank()
        dripper.format_columns()
        print(dripper.get_table())


    conn.close()
