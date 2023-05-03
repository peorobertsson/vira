from jira import JIRAError

class VIRAError(Exception):
    """Exception raised for generic VIRA errors.

    Attributes:
        message -- The error message
        status_code -- The error status code. Can be None
        jira_exception -- The underlying JIRA error (JIRAError). Can be None
    """

    def __init__(
        self, message: str, *, status_code: int = None, jira_error: JIRAError = None
    ):
        self.message = message
        self.status_code = status_code
        self.jira_error = jira_error
        super().__init__(self.message)
