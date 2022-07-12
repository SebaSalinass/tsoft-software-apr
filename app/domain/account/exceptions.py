class ReadingInsertionError(Exception):
    """Reading Exception"""

    def __init__(self, title: str, message: str = ""):
        self.title = title
        self.message = message
        super().__init__(self.message)
