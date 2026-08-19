import hashlib

from legado_agent.infrastructure.filesystem.streaming_sha256 import StreamingSha256


def test_checksum_reads_file_without_modifying_it(tmp_path) -> None:
    path = tmp_path / "large.mov"
    content = b"0123456789" * 1000
    path.write_bytes(content)
    before = path.stat()

    checksum = StreamingSha256(chunk_size=17).calculate(path)

    after = path.stat()
    assert checksum == hashlib.sha256(content).hexdigest()
    assert after.st_size == before.st_size
    assert after.st_mtime_ns == before.st_mtime_ns
