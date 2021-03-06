import argparse

from dripper import Dripper

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--group", 
                        default="champions",
                        choices=['champions', 'contenders', 'challengers'],
                        required=True,
                        help="List champions(>25y), contenders(>10y) or challengers(<10y) of consequent dividend increase")
    parser.add_argument("-d", "--min-dividend", type=float, default=3)
    parser.add_argument("-r", "--min-grow", type=float, default=5)
    parser.add_argument("-z", "--zacks-rank", action="store_true", help="Fetch zachs rank")
    parser.add_argument("-c", "--max-coverage", type=int, default=75)
    parser.add_argument("-b", "--best-only", action="store_true", help="Show the best of the bests only")
    args = parser.parse_args()

    print("Downloading Excel file...")
    dripper = Dripper(args.group.capitalize())
    print("Analyzing...")
    dripper.filter_out_summary()
    dripper.filter_by_dividend(args.min_dividend)
    dripper.filter_by_dgr(args.min_grow)
    print("Fetching Financial Data...")
    dripper.add_cash_flow(args.max_coverage)
    print("Fetching Dividend Data...")
    dripper.add_dividends(args.best_only)
    if args.zacks_rank:
        print("Fetching Zacks Rank...")
        dripper.add_zacks_rank()
    dripper.format_columns()
    print(dripper.get_table())

