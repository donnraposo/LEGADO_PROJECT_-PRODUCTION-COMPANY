import unicodedata
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class NormalizedName:
    value: str
    normalized: str = ""

    def __post_init__(self) -> None:
        value = " ".join(self.value.split())
        if not value:
            raise ValueError("Nome é obrigatório.")
        if len(value) > 160:
            raise ValueError("Nome deve possuir no máximo 160 caracteres.")
        normalized = unicodedata.normalize("NFKC", value).casefold()
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "normalized", normalized)
