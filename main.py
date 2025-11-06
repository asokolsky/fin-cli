import logging
import sys
import typing

import yfinance as yf
from rich.text import Text
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer, Header

from tickers import analyze_ticker, header2ticker_info, headers, load_tickers

logger = logging.getLogger(__name__)


class TheApp(App):
    """A simple Textual app that displays 'Hello, World!'"""

    CSS = """
    Screen {
        --font-size: 1em;
    }

    #the_table {
        font-size: var(--font-size);
        padding: 1;
    }
    """

    TITLE = 'Ticker Analyzer'

    BINDINGS: typing.ClassVar = [
        ('q', 'quit_app', 'Quit'),
        ('u', 'update', 'Update'),
        ('ctrl+plus', 'increase_font_size', 'Increase Font Size'),
        ('ctrl+minus', 'decrease_font_size', 'Decrease Font Size'),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield DataTable(cursor_type='row', zebra_stripes=True, id="the_table")
        yield Footer()
        return

    def on_mount(self) -> None:
        self.table = self.query_one(DataTable)

        # add columns and set column key
        for h in headers:
            self.table.add_column(h, key=h)

        self.tickers = load_tickers('tickers.txt')
        # add rows with ticker only and set row key
        for ticker in sorted(self.tickers):
            row = [ticker if h == headers[0] else '.' for h in headers]
            self.table.add_row(*row, key=ticker, label=ticker)
        return

    def action_quit_app(self) -> None:
        """An action to quit the application."""
        self.exit()

    def action_update(self) -> None:
        """
        Update the values for tickers
        """
        tkrs = yf.Tickers(list(self.tickers))
        tkrs.history(period='1d', repair=True, progress=False)
        for ticker in tkrs.tickers.values():
            info = ticker.info
            for k, v in header2ticker_info.items():
                assert self.table.get_cell(ticker.ticker, k) is not None

                self.table.update_cell(
                    ticker.ticker, k, Text(str(info.get(v)))
                )  # , *, update_width=False)

        # sort by ticker
        # sorted_data = sorted(table_data, key=lambda x: x[0])
        # print(tabulate(sorted_data, headers=headers, tablefmt='simple'))
        return

    def action_increase_font_size(self) -> None:
        current_font_size = float(self.css_vars['font_size'].replace('em', ''))
        new_font_size = min(current_font_size + 0.1, 2.0)  # Limit max size
        self.set_css_vars(font_size=f'{new_font_size}em')
        return

    def action_decrease_font_size(self) -> None:
        current_font_size = float(self.css_vars['font_size'].replace('em', ''))
        new_font_size = max(current_font_size - 0.1, 0.5)  # Limit min size
        self.set_css_vars(font_size=f'{new_font_size}em')
        return


def main() -> int:
    """
    Main entry point
    """
    app = TheApp()
    app.run()
    return 0


if __name__ == '__main__':
    sys.exit(main())
