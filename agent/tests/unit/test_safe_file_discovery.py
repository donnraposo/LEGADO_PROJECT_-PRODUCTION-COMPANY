from legado_agent.infrastructure.filesystem.safe_file_discovery import SafeFileDiscovery


def test_discovery_ignores_technical_and_duplicate_selections(tmp_path) -> None:
    media = tmp_path / "media"
    media.mkdir()
    expected = media / "clip.mov"
    expected.write_bytes(b"video")
    (media / "transfer.tmp").write_bytes(b"temporary")
    (media / "Thumbs.db").write_bytes(b"technical")
    recycle_bin = media / "$RECYCLE.BIN"
    recycle_bin.mkdir()
    (recycle_bin / "deleted.mov").write_bytes(b"ignored")

    discovered = SafeFileDiscovery().discover([media, expected, recycle_bin / "deleted.mov"])

    assert discovered == [expected]
