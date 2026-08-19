from datetime import date

from legado_agent.application.destination_path_builder import build_destination_path


def test_destination_uses_safe_windows_segments_and_date() -> None:
    destination = build_destination_path(
        'Cliente: "Aurora"', "CON", date(2026, 8, 19), "captura.mov"
    )

    assert destination == "Cliente_ _Aurora_\\_CON\\2026\\08\\19\\captura.mov"


def test_destination_uses_unidentified_date_folder() -> None:
    destination = build_destination_path("Cliente", "Projeto", None, "captura.bin")

    assert destination == "Cliente\\Projeto\\DATA_NAO_IDENTIFICADA\\captura.bin"
