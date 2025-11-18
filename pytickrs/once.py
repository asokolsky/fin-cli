import yfinance as yf
from tabulate import tabulate

from .log import eprint, setup_logging
from .tickers import analyze_ticker, headers

log = setup_logging(__name__)


epilog = """Examples:
    $ fin-cli min-max --help
"""


def process_tickers(tickers: set[str]) -> None:
    """
    Process tickers
    """
    tkrs = yf.Tickers(list(tickers))
    tkrs.history(period='1d', repair=True, progress=False)

    # Define the headers for the table

    table_data = []
    for ticker in tkrs.tickers.values():
        info = ticker.info
        # print(info)
        table_data.append(
            [
                ticker.ticker,
                info.get('fiftyTwoWeekLow'),
                info.get('dayLow'),
                # the highest price a buyer is ready to pay
                info.get('bid'),
                info.get('currentPrice'),
                # the lowest price a seller is ready to accept
                info.get('ask'),
                info.get('dayHigh'),
                info.get('fiftyTwoWeekHigh'),
                info.get('regularMarketChange'),
                info.get('regularMarketChangePercent'),
                '; '.join(analyze_ticker(ticker)),
            ]
        )

    # sort by ticker
    sorted_data = sorted(table_data, key=lambda x: x[0])
    print(tabulate(sorted_data, headers=headers, tablefmt='simple'))
    return


def run_once(log_level: int, tickers: set[str]) -> int:
    """
    Main entry point
    """
    log.setLevel(log_level)

    try:
        process_tickers(tickers)
        return 0

    except KeyboardInterrupt:
        eprint('Caught KeyboardInterrupt')

    return 1
