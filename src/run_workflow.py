"""
Module to run the workflow.
"""

import asyncio

from temporalio.client import Client

from constants import TASK_QUEUE_NAME
from models import CustomerRewardAccountInput
from test_constants import MOCK_USER
from workflows import CustomerRewardAccount


async def main():
    # TODO(kawo): externalize connection string
    client = await Client.connect("localhost:7233", namespace="default")

    # Execute a workflow
    result = await client.execute_workflow(
        CustomerRewardAccount.run,
        MOCK_USER,
        id=MOCK_USER.user_id,
        task_queue=TASK_QUEUE_NAME,
    )

    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
