import argparse
import sys

def main():
    parser = argparse.ArgumentParser(
        prog="omega-parse",
        description="Omega Parse — The last parser you'll ever need."
    )

    parser.add_argument(
        "--version",
        action="store_true",
        help="Show the Omega Parse version and exit"
    )

    args = parser.parse_args()

    if args.version:
        print("omega-parse v0.1.0")
        sys.exit(0)

    parser.print_help()
