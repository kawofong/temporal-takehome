"""
Module for testing temporal workflows.
"""

from uuid import uuid4

import pytest
from temporalio.client import Client
from temporalio.exceptions import WorkflowAlreadyStartedError
from temporalio.service import RPCError
from temporalio.worker import Worker

from activities import get_user
from constants import CustomerRewardLevel
from models import AddPointInput, CustomerRewardAccountInput
from test_constants import TEST_TASK_QUEUE
from workflows import CustomerRewardAccount


def random_user():
    """Generate a random user."""
    return CustomerRewardAccountInput(user_id=str(uuid4()))


@pytest.mark.asyncio
async def test_new_user_join_reward_program(client: Client):
    """
    Given user has not enrolled in the reward program,
    When an user joins the reward program,
    Then they have basic level and 0 point.
    """
    async with Worker(
        client,
        task_queue=TEST_TASK_QUEUE,
        workflows=[CustomerRewardAccount],
        activities=[get_user],
    ):
        user = random_user()
        handle = await client.start_workflow(
            CustomerRewardAccount.run,
            user,
            id=user.user_id,
            task_queue=TEST_TASK_QUEUE,
        )
        result = await handle.query(CustomerRewardAccount.query_reward_status)
        assert result.level == CustomerRewardLevel.BASIC
        assert result.points == 0
        assert result.is_active


@pytest.mark.parametrize(
    "starting_points, points_earned, expected_level",
    [
        (0, 1, CustomerRewardLevel.BASIC),
        (499, 1, CustomerRewardLevel.GOLD),
        (999, 1, CustomerRewardLevel.PLATINUM),
        (0, 1000, CustomerRewardLevel.PLATINUM),
        (0, 0, CustomerRewardLevel.BASIC),
        (499, 0, CustomerRewardLevel.BASIC),
        (500, 0, CustomerRewardLevel.GOLD),
        (501, 0, CustomerRewardLevel.GOLD),
        (999, 0, CustomerRewardLevel.GOLD),
        (1000, 0, CustomerRewardLevel.PLATINUM),
        (1001, 0, CustomerRewardLevel.PLATINUM),
        (2_147_483_647, 0, CustomerRewardLevel.PLATINUM),
    ],
)
@pytest.mark.asyncio
async def test_user_earn_points(
    starting_points: int,
    points_earned: int,
    expected_level: CustomerRewardLevel,
    client: Client,
):
    """
    Given user has X points,
    When an user make a $Y purchase,
    Then they should have X+Y points and are promoted to appropriate level.
    """
    async with Worker(
        client,
        task_queue=TEST_TASK_QUEUE,
        workflows=[CustomerRewardAccount],
        activities=[get_user],
    ):
        user = random_user()
        handle = await client.start_workflow(
            CustomerRewardAccount.run,
            user,
            id=user.user_id,
            task_queue=TEST_TASK_QUEUE,
        )
        await handle.execute_update(
            CustomerRewardAccount.add_points, AddPointInput(points=starting_points)
        )
        result = await handle.execute_update(
            CustomerRewardAccount.add_points, AddPointInput(points=points_earned)
        )
        assert result.level == expected_level
        assert result.points == (starting_points + points_earned)
        assert result.is_active


@pytest.mark.asyncio
async def test_user_cancel_reward_account(
    client: Client,
):
    """
    Given user has enrolled in the reward program,
    When the user requests to leave the program,
    Then their reward program becomes inactive.
    """
    async with Worker(
        client,
        task_queue=TEST_TASK_QUEUE,
        workflows=[CustomerRewardAccount],
        activities=[get_user],
    ):
        user = random_user()
        handle = await client.start_workflow(
            CustomerRewardAccount.run,
            user,
            id=user.user_id,
            task_queue=TEST_TASK_QUEUE,
        )
        result = await handle.execute_update(CustomerRewardAccount.cancel)
        assert result.level == CustomerRewardLevel.BASIC
        assert result.points == 0
        assert not result.is_active


@pytest.mark.asyncio
async def test_existing_user_join_reward_program(
    client: Client,
):
    """
    Given user has enrolled in the reward program,
    When an user joins the reward program,
    Then the operation should fail.
    """
    async with Worker(
        client,
        task_queue=TEST_TASK_QUEUE,
        workflows=[CustomerRewardAccount],
        activities=[get_user],
    ):
        user = random_user()
        await client.start_workflow(
            CustomerRewardAccount.run,
            user,
            id=user.user_id,
            task_queue=TEST_TASK_QUEUE,
        )

        with pytest.raises(WorkflowAlreadyStartedError):
            await client.start_workflow(
                CustomerRewardAccount.run,
                user,
                id=user.user_id,
                task_queue=TEST_TASK_QUEUE,
            )


@pytest.mark.asyncio
async def test_query_non_existing_reward_program(
    client: Client,
):
    """
    Given user has not enrolled in the reward program,
    When a client queries the user account,
    Then the operation should fail.
    """
    async with Worker(
        client,
        task_queue=TEST_TASK_QUEUE,
        workflows=[CustomerRewardAccount],
        activities=[get_user],
    ):
        user = random_user()
        with pytest.raises(RPCError) as exc_info:
            handle = client.get_workflow_handle_for(
                CustomerRewardAccount.run, user.user_id
            )
            await handle.query(CustomerRewardAccount.query_reward_status)

        assert str(exc_info.value).startswith("Execution not found")


@pytest.mark.asyncio
async def test_cancel_non_existing_reward_program(
    client: Client,
):
    """
    Given user has not enrolled in the reward program,
    When the user requests to leave the program,
    Then the operation should fail.
    """
    async with Worker(
        client,
        task_queue=TEST_TASK_QUEUE,
        workflows=[CustomerRewardAccount],
        activities=[get_user],
    ):
        user = random_user()
        with pytest.raises(RPCError) as exc_info:
            handle = client.get_workflow_handle_for(
                CustomerRewardAccount.run, user.user_id
            )
            await handle.execute_update(CustomerRewardAccount.cancel)

        assert str(exc_info.value).startswith("Execution not found")
