from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest
from sqlalchemy.sql.elements import TextClause

from api.routes.health import health_check


@pytest.mark.unit
@pytest.mark.asyncio
async def test_health_check_uses_text_clause_for_database_probe():
    db = AsyncMock()

    redis_client = Mock()
    redis_client.ping.return_value = True

    settings = SimpleNamespace(
        redis_host="localhost",
        redis_port=6379,
        vector_db_url="http://localhost:8001",
    )

    with (
        patch("redis.Redis", return_value=redis_client),
        patch("core.config.settings", settings),
    ):
        result = await health_check(db)

    db.execute.assert_awaited_once()

    statement = db.execute.await_args.args[0]

    assert isinstance(statement, TextClause)
    assert str(statement) == "SELECT 1"
    assert result["dependencies"]["postgres"] == "healthy"
