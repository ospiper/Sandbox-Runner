class JudgerException(Exception):
    def __init__(self, message):
        super().__init__()
        self.message = message


class JudgerError(JudgerException):
    pass


class CompileError(JudgerException):
    pass


class TokenVerificationFailed(JudgerException):
    pass


class JudgeClientError(JudgerException):
    pass


class JudgeServiceError(JudgerException):
    pass
