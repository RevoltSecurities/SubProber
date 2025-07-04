from alive_progress import alive_bar

class ProgressBar:
    def __init__(self, total, title="Progress"):
        self.total = total
        self.title = title
        self._bar = alive_bar(total, title=title, enrich_print=False)
        self._update = None

    def start(self):
        self._update = self._bar.__enter__()

    def update(self,):
        if self._update:
            self._update()

    def close(self):
        if self._bar:
            self._bar.__exit__(None, None, None)
