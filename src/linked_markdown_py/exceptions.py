LMD_MISSING_ID = "LMD_MISSING_ID"
LMD_MISSING_TYPE = "LMD_MISSING_TYPE"


class LmdError(Exception):
    def __init__(self, message: str, code: str) -> None:
        super().__init__(message)
        self.code = code


class MissingIdError(LmdError):
    def __init__(self) -> None:
        super().__init__(
            "Document is missing required @id or id field",
            LMD_MISSING_ID,
        )


class MissingTypeError(LmdError):
    def __init__(self) -> None:
        super().__init__(
            "Document is missing required @type or type field",
            LMD_MISSING_TYPE,
        )
