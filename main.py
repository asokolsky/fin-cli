import logging
import sys
from pathlib import Path
from typing import Any

import yfinance as yf
from rich.text import Text
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer, Header, Label

from tickers import analyze_ticker, headers, load_tickers

logger = logging.getLogger(__name__)

ROWS = [
    ('lane', 'swimmer', 'country', 'time'),
    (4, 'Joseph Schooling', 'Singapore', 50.39),
    (2, 'Michael Phelps', 'United States', 51.14),
    (5, 'Chad le Clos', 'South Africa', 51.14),
    (6, 'László Cseh', 'Hungary', 51.14),
    (3, 'Li Zhuhao', 'China', 51.26),
    (8, 'Mehdy Metella', 'France', 51.58),
    (7, 'Tom Shields', 'United States', 51.73),
    (1, 'Aleksandr Sadovnikov', 'Russia', 51.84),
    (10, 'Darren Burns', 'Scotland', 51.84),
]


class TheApp(App):
    """A simple Textual app that displays 'Hello, World!'"""

    BINDINGS = [
        ('q', 'quit_app', 'Quit'),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        self.table = self.query_one(DataTable)
        self.table.add_columns(*headers)
        self.tickers = load_tickers('tickers.txt')
        self.process_tickers()
        # for row in ROWS[1:]:
        #    styled_row = [
        #        Text(str(cell), justify="right") # style="italic #03AC13",
        #        for cell in row
        #    ]
        #    table.add_row(*styled_row)

    def action_quit_app(self) -> None:
        """An action to quit the application."""
        self.exit()

    def process_tickers(self) -> None:
        """
        Process tickers
        """
        tkrs = yf.Tickers(list(self.tickers))
        tkrs.history(period='1d', repair=True, progress=False)
        for ticker in tkrs.tickers.values():
            info = ticker.info
            styled_row = [
                Text(str(ticker.ticker)),
                Text(str(info.get('fiftyTwoWeekLow'))),
                Text(str(info.get('dayLow'))),
                # the highest price a buyer is ready to pay
                Text(str(info.get('bid'))),
                Text(str(info.get('currentPrice'))),
                # the lowest price a seller is ready to accept
                Text(str(info.get('ask'))),
                Text(str(info.get('dayHigh'))),
                Text(str(info.get('fiftyTwoWeekHigh'))),
                Text(str(info.get('regularMarketChange'))),
                Text(str(info.get('regularMarketChangePercent'))),
                Text('; '.join(analyze_ticker(ticker))),
            ]
            self.table.add_row(*styled_row)

        # sort by ticker
        # sorted_data = sorted(table_data, key=lambda x: x[0])
        # print(tabulate(sorted_data, headers=headers, tablefmt='simple'))
        return


def main() -> int:
    """
    Main entry point
    """
    app = TheApp()
    app.run()


if __name__ == '__main__':
    sys.exit(main())
