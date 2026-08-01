from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EmailAddress:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().casefold()
        if not normalized or "@" not in normalized:
            raise ValueError("E-mail autenticado inválido.")
        object.__setattr__(self, "value", normalized)
