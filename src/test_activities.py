"""
Module for testing temporal activities.
"""

import pytest
from temporalio.testing import ActivityEnvironment

from activities import get_user
from models import UserInfo


@pytest.mark.asyncio
async def test_get_user():
    env = ActivityEnvironment()
    result = await env.run(get_user, "test-user-id")
    assert isinstance(result, UserInfo)
    assert result.id == "test-user-id"
    assert result.name == "John Doe"
