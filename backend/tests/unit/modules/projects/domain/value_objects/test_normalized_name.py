import pytest

from modules.projects.domain.value_objects.normalized_name import NormalizedName


def test_name_normalizes_whitespace_case_and_unicode() -> None:
    name = NormalizedName("  Vídeo   Institucional  ")

    assert name.value == "Vídeo Institucional"
    assert name.normalized == "vídeo institucional"


def test_empty_name_is_rejected() -> None:
    with pytest.raises(ValueError):
        NormalizedName("   ")
