from typing import ClassVar

import yfinance as yf
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import DataTable, Footer, Header, Label, Static
from textual.worker import Worker


from .log import setup_logging
from .tickers import analyze_ticker, header2ticker_info, headers
from .split_pane import SplitContainer

log = setup_logging(__name__)

CSS = """
Horizontal#footer-outer {
    height: 1;
    dock: bottom;
}
Horizonal#footer-inner {
    width: 66%;
    dock: right;
}
Label#status {
    width: 33%;
    text-align: left;
    dock: left;
}
"""


class TaskCompleteMessage(Message):
    """
    A message indicating the background task is complete.
    """


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

    TITLE = 'Stock Analyzer'
    SUB_TITLE = 'The most important app you will ever need'
    CSS = CSS

    BINDINGS: ClassVar = [
        ('q', 'quit_app', 'Quit'),
        ('u', 'update', 'Update'),
        ('ctrl+plus', 'increase_font_size', 'Increase Font Size'),
        ('ctrl+minus', 'decrease_font_size', 'Decrease Font Size'),
    ]

    def __init__(self, tickers: set[str]) -> None:
        super().__init__()
        self.column_index_selected = 0
        self.column_sort_reverse = False
        self.tickers = tickers
        assert self.tickers
        return

    def compose(self) -> ComposeResult:
        """
        Create child widgets for the app.
        """
        log.debug('compose %s', self)
        self.tkrs: yf.Tickers | None = None
        yield Header()
        yield SplitContainer(
            before=DataTable(cursor_type='row', zebra_stripes=True, id='tickers'),
            after=DataTable(cursor_type='row', zebra_stripes=True, id='details'),
        )
        with Horizontal(id='footer-outer'):
            yield Label('This is the left side label', id='status')
            with Horizontal(id='footer-inner'):
                yield Footer(id='footer')
        return

    def on_mount(self) -> None:
        log.debug('on_mount %s', self)


        def fill_table(
            table: DataTable, headers: list[str], tickers: list[str]
        ) -> None:
            # add columns and set column key
            for h in headers:
                table.add_column(h, key=h)

            # add rows and set row key
            for row in rows:
                r = [row if h == headers[0] else '.' for h in headers]
                table.add_row(*r, key=row)
            return

        self.tickers_table = self.query_one('#tickers', DataTable)
        self.details_table = self.query_one('#details', DataTable)
        self.status = self.query_one('#status')
        self.footer_inner = self.query_one('#footer-inner')
        self.footer = self.query_one('#footer')
        fill_table(self.tickers_table, headers, sorted(self.tickers))
        details_headers = ['Param', 'Value']
        fill_table(self.details_table, details_headers, ['foo', 'bar'])

        # adjust footer status styles
        self.status.styles.background = self.footer.styles.background
        self.status.styles.color = self.footer.styles.color
        return

    def on_data_table_header_selected(self, message: DataTable.HeaderSelected) -> None:
        """
        Handles a click on a column header.
        """
        log.debug('on_data_table_header_selected %s', message)

        if self.column_index_selected != message.column_index:
            self.column_sort_reverse = False
            self.column_index_selected = message.column_index
        else:
            self.column_sort_reverse = not self.column_sort_reverse

        try:
            self.table.sort(message.column_key, reverse=self.column_sort_reverse)
        except Exception:
            log.exception('Error sorting table:')
        return

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        """
        Row in the DataTable is highlighted.
        """
        row_key = event.row_key
        log.debug('Row highlighted: %s %s', row_key.value, event.data_table.id)
        if self.tkrs is not None:
            ticker = self.tkrs.tickers.get(row_key.value)
            if ticker is not None:
                log.debug('Ticker: %s', ticker)
                self.set_status(ticker.info['longName'])
                return
        if row_key.value:
            self.set_status(row_key.value)
        return

    # def on_timer(self, message: Timer) -> None:
    #    """Handles a Timer event."""
    #    log.debug('on_timer %s', message)
    #    return

    # def on_idle(self, message: Idle) -> None:
    #    """Handles an Idle event."""
    #    # log.debug('on_idle %s', message)
    #    return

    def action_quit_app(self) -> None:
        """An action to quit the application."""
        log.debug('action_quit_app %s', self)
        self.exit()

    def action_update(self) -> None:
        """
        Update the values for tickers
        """
        log.debug('action_update %s', self)
        self.set_status('Updating...')
        self.run_long_task()
        return

    @work(group='yfinance', exclusive=True, thread=True)
    def run_long_task(self) -> None:
        """
        Download ticker info in the background.
        group: A short string to identify a group of workers.
        exclusive: Cancel all workers in the same group.
        thread: Mark the method as a thread worker.
        """
        self.tkrs = yf.Tickers(list(self.tickers))
        self.tkrs.history(period='1d', repair=True, progress=False)
        self.post_message(TaskCompleteMessage())
        return

    def on_task_complete_message(self, message: TaskCompleteMessage) -> None:
        """
        Called when the background task is complete.
        """
        self.notify('Background task finished!')

        def update_table(table: DataTable, tkrs: yf.Tickers) -> None:
            for ticker in tkrs.tickers.values():
                info = ticker.info
                for k, v in header2ticker_info.items():
                    if table.get_cell(ticker.ticker, k) is None:
                        continue
                    if info.get(v) is None:
                        continue
                    table.update_cell(ticker.ticker, k, info.get(v))
                table.update_cell(
                    ticker.ticker,
                    headers[-1],
                    '; '.join(analyze_ticker(ticker)),
                    update_width=True,
                )

            return

        update_table(self.tickers_table, self.tkrs)
        self.set_status('Updated')
        # self.status.styles.width = '25%'
        # self.footer_inner.styles.width = '75%'
        log.debug('action_update DONE')
        return

    def on_worker_state_changed(self, event: Worker.StateChanged) -> None:
        """Called when the worker state changes."""
        log.debug('on_worker_state_changed %s', event)
        return

    def set_status(self, text: str) -> None:
        """Set the status label text."""
        log.debug('set_status %s', text)
        # self.status.styles.width = '75%'
        # self.footer_inner.styles.width = '25%'
        self.status.update(text)
        return

    def action_increase_font_size(self) -> None:
        log.debug('action_increase_font_size %s', self)
        # current_font_size = float(self.css_vars['font_size'].replace('em', ''))
        # new_font_size = min(current_font_size + 0.1, 2.0)  # Limit max size
        # self.set_css_vars(font_size=f'{new_font_size}em')
        return

    def action_decrease_font_size(self) -> None:
        log.debug('action_decrease_font_size %s', self)
        # current_font_size = float(self.css_vars['font_size'].replace('em', ''))
        # new_font_size = max(current_font_size - 0.1, 0.5)  # Limit min size
        # self.set_css_vars(font_size=f'{new_font_size}em')
        return


def run_tui(log_level: int, tickers: set[str]) -> int:
    """
    Main TUI entry point
    """
    log.setLevel(log_level)
    app = TheApp(tickers)
    app.run()
    return 0
