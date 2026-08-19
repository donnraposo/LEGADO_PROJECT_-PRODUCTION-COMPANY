class SensitiveDataPolicy:
    _FORBIDDEN_KEYS = {
        "access_token",
        "authorization",
        "credential",
        "local_path",
        "password",
        "refresh_token",
        "secret",
        "token",
    }

    @classmethod
    def contains_forbidden_key(cls, value: object) -> bool:
        if isinstance(value, dict):
            return any(
                str(key).casefold() in cls._FORBIDDEN_KEYS
                or cls.contains_forbidden_key(item)
                for key, item in value.items()
            )
        if isinstance(value, list):
            return any(cls.contains_forbidden_key(item) for item in value)
        return False
