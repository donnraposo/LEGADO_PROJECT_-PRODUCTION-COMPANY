from django.db import migrations

CREATE_PROTECTION_SQL = """
CREATE OR REPLACE FUNCTION prevent_audit_event_mutation()
RETURNS trigger AS $$
BEGIN
    RAISE EXCEPTION 'audit_events is immutable';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS audit_events_immutable ON audit_events;
CREATE TRIGGER audit_events_immutable
BEFORE UPDATE OR DELETE ON audit_events
FOR EACH ROW EXECUTE FUNCTION prevent_audit_event_mutation();
"""

DROP_PROTECTION_SQL = """
DROP TRIGGER IF EXISTS audit_events_immutable ON audit_events;
DROP FUNCTION IF EXISTS prevent_audit_event_mutation();
"""


def create_protection(apps, schema_editor) -> None:
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(CREATE_PROTECTION_SQL)


def drop_protection(apps, schema_editor) -> None:
    if schema_editor.connection.vendor == "postgresql":
        schema_editor.execute(DROP_PROTECTION_SQL)


class Migration(migrations.Migration):
    dependencies = [("audit", "0002_audit_event_details")]
    operations = [migrations.RunPython(create_protection, drop_protection)]
