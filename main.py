import logging
import sys
import typing

import yfinance as yf
from rich.text import Text
from textual.app import App, ComposeResult
from textual.widgets import DataTable, Footer, Header
from textual.events import Idle, Timer

from tickers import analyze_ticker, header2ticker_info, headers, load_tickers

logging.basicConfig(
    filename='main.log',
    encoding='utf-8',
    filemode='a',
    format='{asctime} {levelname} {message}',
    style='{',
    datefmt='%Y-%m-%d %H:%M',
)
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')


class TheApp(App):
    """
    A simple Textual app using yfinance to retrieve and display stock data.
    1. Load tickers from a file
    2. Display tickers in a table
    3. Update ticker data on user command
    4. Sort table by column on header click
    5. Increase/decrease font size on user command
    6. Quit app on user command
    7. Log actions to a file
    8. Use yfinance to fetch ticker data
    """

    TITLE = 'Ticker Analyzer'
    SUB_TITLE = 'The most important app you will ever need'

    #CSS = """
    #Screen {
    #    align: center middle;
    #}
    #"""

    BINDINGS: typing.ClassVar = [
        ('q', 'quit_app', 'Quit'),
        ('u', 'update', 'Update'),
        ('ctrl+plus', 'increase_font_size', 'Increase Font Size'),
        ('ctrl+minus', 'decrease_font_size', 'Decrease Font Size'),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        logger.debug('compose %s', self)
        yield Header()
        yield DataTable(cursor_type='row', zebra_stripes=True)
        yield Footer()
        return

    def on_mount(self) -> None:
        logger.debug('on_mount %s', self)

        def fill_table(table: DataTable, headers, tickers: list[str]) -> None:
            # add columns and set column key
            for h in headers:
                table.add_column(h, key=h)

            # add rows with ticker only and set row key
            for ticker in tickers:
                row = [ticker if h == headers[0] else '.' for h in headers]
                table.add_row(*row, key=ticker)  # label=ticker
            return

        self.column_index_selected = 0
        self.column_sort_reverse = False
        self.tickers = load_tickers('tickers.txt')
        self.table = self.query_one(DataTable)
        self.footer = self.query_one(Footer)
        fill_table(self.table, headers, sorted(self.tickers))
        return

    def on_data_table_header_selected(self, message: DataTable.HeaderSelected) -> None:
        """Handles a click on a column header."""
        logger.debug('on_data_table_header_selected %s', message)

        if self.column_index_selected != message.column_index:
            self.column_sort_reverse = False
            self.column_index_selected = message.column_index
        else:
            self.column_sort_reverse = not self.column_sort_reverse

        try:
            self.table.sort(message.column_key, reverse=self.column_sort_reverse)
        except Exception as exc:
            logger.error('Error sorting table: %s', exc)
        return

    def on_timer(self, message: Timer) -> None:
        """Handles a Timer event."""
        logger.debug('on_timer %s', message)
        return

    def on_idle(self, message: Idle) -> None:
        """Handles an Idle event."""
        # logger.debug('on_idle %s', message)
        return

    def action_quit_app(self) -> None:
        """An action to quit the application."""
        logger.debug('action_quit_app %s', self)
        self.exit()

    def action_update(self) -> None:
        """
        Update the values for tickers
        """
        logger.debug('action_update %s', self)
        tkrs = yf.Tickers(list(self.tickers))
        tkrs.history(period='1d', repair=True, progress=False)

        def update_table(table: DataTable, tkrs) -> None:
            for ticker in tkrs.tickers.values():
                info = ticker.info
                for k, v in header2ticker_info.items():
                    assert table.get_cell(ticker.ticker, k) is not None
                    table.update_cell(ticker.ticker, k, info.get(v))
            return

        update_table(self.table, tkrs)
        logger.debug('action_update - DONE')
        return

    def action_increase_font_size(self) -> None:
        logger.debug('action_increase_font_size %s', self)
        # current_font_size = float(self.css_vars['font_size'].replace('em', ''))
        # new_font_size = min(current_font_size + 0.1, 2.0)  # Limit max size
        # self.set_css_vars(font_size=f'{new_font_size}em')
        return

    def action_decrease_font_size(self) -> None:
        logger.debug('action_decrease_font_size %s', self)
        # current_font_size = float(self.css_vars['font_size'].replace('em', ''))
        # new_font_size = max(current_font_size - 0.1, 0.5)  # Limit min size
        # self.set_css_vars(font_size=f'{new_font_size}em')
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
