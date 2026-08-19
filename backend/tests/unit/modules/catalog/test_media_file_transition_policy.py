import pytest

from modules.catalog.application.exceptions import InvalidMediaFileTransitionError
from modules.catalog.application.media_file_transition_policy import MediaFileTransitionPolicy


def test_accepts_forward_transition() -> None:
    MediaFileTransitionPolicy.validate("DESCOBERTO", "ANALISADO")


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("DESCOBERTO", "SINCRONIZADO"),
        ("SINCRONIZADO", "ENVIANDO"),
        ("CANCELADO", "DESCOBERTO"),
        ("DESCONHECIDO", "ANALISADO"),
    ],
)
def test_rejects_invalid_or_regressive_transition(current: str, target: str) -> None:
    with pytest.raises(InvalidMediaFileTransitionError):
        MediaFileTransitionPolicy.validate(current, target)
