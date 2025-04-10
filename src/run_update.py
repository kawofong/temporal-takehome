"""
Module to run workflow queries.
"""

import asyncio

from temporalio.client import Client, WorkflowHandle

from models import AddPointInput, CustomerRewardAccountStatus
from test_constants import MOCK_USER
from workflows import CustomerRewardAccount


async def add_points_bulk(
    handle: WorkflowHandle[CustomerRewardAccount, CustomerRewardAccountStatus],
    points: int,
    iterations: int,
) -> None:
    """
    Adds points to the reward account for `iterations` times
    """
    futures = []
    print("Adding points for %s times", iterations)
    for _ in range(iterations):
        futures.append(
            handle.execute_update(
                CustomerRewardAccount.add_points, AddPointInput(points=points)
            )
        )

    return await asyncio.gather(*futures)


async def main():
    # TODO(kawo): externalize connection string
    client = await Client.connect("localhost:7233", namespace="default")

    handle = client.get_workflow_handle_for(
        CustomerRewardAccount.run, MOCK_USER.user_id
    )
    # result = await handle.execute_update(CustomerRewardAccount.cancel)
    result = await add_points_bulk(handle=handle, points=1, iterations=4)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
