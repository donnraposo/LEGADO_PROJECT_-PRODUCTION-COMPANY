from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CompanyName:
    value: str

    def __post_init__(self) -> None:
        normalized_whitespace = " ".join(self.value.split())
        if not normalized_whitespace:
            raise ValueError("Nome da empresa é obrigatório.")
        if len(normalized_whitespace) > 160:
            raise ValueError("Nome da empresa deve possuir no máximo 160 caracteres.")
        object.__setattr__(self, "value", normalized_whitespace)
