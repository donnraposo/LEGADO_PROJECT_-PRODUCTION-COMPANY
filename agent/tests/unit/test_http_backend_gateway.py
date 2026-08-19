from uuid import uuid4

import httpx

from legado_agent.infrastructure.http.http_backend_gateway import HttpBackendGateway


def test_gateway_uses_company_context_and_command_version() -> None:
    company_id = uuid4()
    machine_id = uuid4()
    command_id = uuid4()
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/heartbeat"):
            return httpx.Response(200, json={"id": str(machine_id)})
        if request.method == "GET":
            return httpx.Response(200, json={"items": [_command_json(command_id, machine_id)]})
        return httpx.Response(
            200,
            json=_command_json(command_id, machine_id, status="ACKNOWLEDGED", version=2),
        )

    gateway = HttpBackendGateway(
        "http://backend.local", "memory-only", transport=httpx.MockTransport(handler)
    )
    try:
        assert gateway.heartbeat(company_id, uuid4(), "station", "WINDOWS", "0.1.0") == machine_id
        command = gateway.list_commands(company_id, machine_id, 0)[0]
        updated = gateway.update_command(company_id, command, "ACKNOWLEDGED")
    finally:
        gateway.close()

    assert updated.status == "ACKNOWLEDGED"
    assert updated.version == 2
    assert all(request.headers["x-company-id"] == str(company_id) for request in requests)
    assert all(request.headers["authorization"] == "Bearer memory-only" for request in requests)
    assert requests[1].url.params["after_sequence"] == "0"
    assert b'"expected_version":1' in requests[2].content


def test_gateway_lists_clients_and_projects_in_company_context() -> None:
    company_id = uuid4()
    client_id = uuid4()
    project_id = uuid4()
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path.endswith("/clients"):
            return httpx.Response(
                200, json={"items": [{"id": str(client_id), "name": "Cliente"}]}
            )
        return httpx.Response(
            200,
            json={
                "items": [
                    {
                        "id": str(project_id),
                        "client_id": str(client_id),
                        "name": "Projeto",
                    }
                ]
            },
        )

    gateway = HttpBackendGateway(
        "http://backend.local", "memory-only", transport=httpx.MockTransport(handler)
    )
    try:
        assert gateway.list_clients(company_id)[0]["name"] == "Cliente"
        assert gateway.list_projects(company_id)[0]["name"] == "Projeto"
    finally:
        gateway.close()

    assert [request.url.path for request in requests] == [
        "/api/v1/clients",
        "/api/v1/projects",
    ]
    assert all(request.headers["x-company-id"] == str(company_id) for request in requests)


def test_gateway_ingests_only_catalog_metadata() -> None:
    company_id = uuid4()
    project_id = uuid4()
    machine_id = uuid4()
    ingestion_id = uuid4()
    media_file_id = uuid4()
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(201, json={"id": str(media_file_id)})

    gateway = HttpBackendGateway(
        "http://backend.local", "memory-only", transport=httpx.MockTransport(handler)
    )
    try:
        result = gateway.ingest_media_file(
            company_id,
            project_id,
            machine_id,
            ingestion_id,
            "clip.mov",
            "video/quicktime",
            100,
            "a" * 64,
        )
    finally:
        gateway.close()

    request = captured[0]
    assert result == media_file_id
    assert request.url.path == "/api/v1/agent/media-files"
    assert request.headers["x-company-id"] == str(company_id)
    assert b"source_path" not in request.content
    assert b"destination_path" not in request.content


def _command_json(command_id, machine_id, status="PENDING", version=1):
    return {
        "id": str(command_id),
        "machine_id": str(machine_id),
        "command_type": "PING",
        "resource_type": "machine",
        "resource_id": None,
        "payload": {},
        "sequence": 1,
        "status": status,
        "progress_percent": 0,
        "version": version,
    }
