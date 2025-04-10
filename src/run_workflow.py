"""
Module to run the workflow.
"""

import asyncio

from temporalio.client import Client

from constants import TASK_QUEUE_NAME
from models import CustomerRewardAccountInput
from workflows import CustomerRewardAccount


async def main():
    # TODO(kawo): externalize connection string
    client = await Client.connect("localhost:7233", namespace="default")

    mock_user = CustomerRewardAccountInput(user_id="test-user-id")

    # Execute a workflow
    result = await client.execute_workflow(
        CustomerRewardAccount.run,
        mock_user,
        id=mock_user.user_id,
        task_queue=TASK_QUEUE_NAME,
    )

    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
