class CliError(Exception):
    """An expected command-line or input error with an exit status."""

    def __init__(self, message: str, code: int = 2) -> None:
        super().__init__(message)
        self.message: str = message
        self.code: int = code
