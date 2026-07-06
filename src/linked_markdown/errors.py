class LinkedMarkdownError(Exception):
    def __init__(self, code: str, message: str | None = None, cause: Exception | None = None):
        self.code = code
        self.cause = cause
        super().__init__(message or code)

    def __str__(self) -> str:
        msg = super().__str__()
        return f"[{self.code}] {msg}"


LMD_NO_FRONTMATTER = "LMD_NO_FRONTMATTER"
LMD_INVALID_FRONTMATTER = "LMD_INVALID_FRONTMATTER"
