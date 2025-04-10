"""
Module for defining temporal workflows.
"""

import pytest
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from activities import get_user
from constants import CustomerRewardLevel
from test_constants import MOCK_USER, TEST_TASK_QUEUE
from workflows import CustomerRewardAccount


@pytest.mark.asyncio
async def test_new_user_join_reward_program():
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client,
            task_queue=TEST_TASK_QUEUE,
            workflows=[CustomerRewardAccount],
            activities=[get_user],
        ):
            handle = await env.client.start_workflow(
                CustomerRewardAccount.run,
                MOCK_USER,
                id=MOCK_USER.user_id,
                task_queue=TEST_TASK_QUEUE,
            )
            result = await handle.query(CustomerRewardAccount.query_reward_status)
            assert result.level == CustomerRewardLevel.BASIC
            assert result.points == 0
            assert result.is_active
