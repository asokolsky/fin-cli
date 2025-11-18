"""
Run pytickrs
    python -m pytickrs --version
"""

import logging
import sys
from argparse import ArgumentParser, FileType, RawTextHelpFormatter

from . import __version__
from .once import run_once
from .tui import run_tui

epilog = """Examples:
    python -m pytickrs --version
    python -m pytickrs --once
    python -m pytickrs
"""


def comma_separated_list(arg: str) -> list[str]:
    return arg.strip().split(',')


def load_tickers(f) -> set[str]:
    tickers: set[str] = set()
    for line1 in f:
        line = line1.strip()
        if line and not line.startswith('#'):
            tickers.add(line.upper())
    return tickers


def main() -> int:
    """
    Get the tickers info and act on it
    """
    ap = ArgumentParser(
        prog='pytickrs',
        description='pytickrs cli v' + __version__,
        formatter_class=RawTextHelpFormatter,
        epilog=epilog,
    )
    ap.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        default=False,
        help='Tell more about what is going on',
    )
    ap.add_argument(
        '--once',
        action='store_true',
        default=False,
        help='One-time tickers info and recommendations',
    )
    ap.add_argument(
        '--version',
        action='store_true',
        help='Display module version and exit.',
    )
    #
    # '--tickers' and '--tickers-from' are mutually exclusive
    #
    group = ap.add_mutually_exclusive_group()
    group.add_argument(
        '--tickers', type=comma_separated_list, help='A comma-separated list of tickers'
    )
    group.add_argument(
        '--tickers-from',
        type=FileType('r'),
        default='tickers.txt',
        help='Path to a file with tickers (one per line)',
    )

    args = ap.parse_args()
    if args.version:
        print(__version__)
        return 0

    level = logging.DEBUG if args.verbose else logging.INFO
    tickers = args.tickers if args.tickers else load_tickers(args.tickers_from)
    if args.once:
        return run_once(level, tickers)

    return run_tui(level, tickers)


if __name__ == '__main__':
    sys.exit(main())
