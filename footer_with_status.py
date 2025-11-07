from textual.app import ComposeResult
from textual.widgets import Footer, Label


class MyFooter(Footer):
    """
    Footer which also can display a right-aligned label.
    """

    DEFAULT_CSS = """
  MyFooter {

    .right-label {
        text-align: right;
    }
  }
  """

    def compose(self) -> ComposeResult:
        for widget in super().compose():
            yield widget
        yield Label('This is the right side label', id='right-label')
