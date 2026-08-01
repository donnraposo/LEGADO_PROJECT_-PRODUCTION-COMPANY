from modules.audit.infrastructure.persistence.audit_recorder import AuditRecorder


def test_changes_contains_only_modified_fields() -> None:
    changes = AuditRecorder._changes(
        {"role": "ADMINISTRATOR", "status": "ACTIVE", "name": "Ana"},
        {"role": "OWNER", "status": "ACTIVE", "name": "Ana"},
    )

    assert changes == {
        "role": {"old": "ADMINISTRATOR", "new": "OWNER"},
    }


def test_changes_represents_added_and_removed_fields() -> None:
    changes = AuditRecorder._changes(
        {"removed": "value"},
        {"added": "value"},
    )

    assert changes == {
        "added": {"old": None, "new": "value"},
        "removed": {"old": "value", "new": None},
    }
