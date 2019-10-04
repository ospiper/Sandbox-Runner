class RunnerException(Exception):
    def __init__(self, message=''):
        super().__init__()
        self.message = message


class ArgumentError(RunnerException):
    def __str__(self):
        return 'ArgumentError: %s' % self.message
