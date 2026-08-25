class GoogleOAuthNotConfiguredError(RuntimeError):
    pass


class InvalidOAuthStateError(ValueError):
    pass


class GoogleOAuthExchangeError(RuntimeError):
    pass
