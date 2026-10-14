import pytest


@pytest.mark.asyncio
async def test_request_id_and_security_headers(client):
    res = await client.get("/health")
    assert res.status_code == 200
    assert "x-request-id" in res.headers
    assert "x-process-time-ms" in res.headers
    assert res.headers["x-content-type-options"] == "nosniff"
    assert res.headers["x-frame-options"] == "DENY"
