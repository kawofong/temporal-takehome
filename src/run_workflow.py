"""
Module to run the workflow.
"""

import asyncio

from temporalio.client import Client

from constants import TASK_QUEUE_NAME
from workflows import SayHello


async def main():
    # TODO(kawo): externalize connection string
    client = await Client.connect("localhost:7233", namespace="default")

    # Execute a workflow
    result = await client.execute_workflow(
        SayHello.run, "Temporal", id="hello-workflow", task_queue=TASK_QUEUE_NAME
    )

    print(f"Result: {result}")


if __name__ == "__main__":
    asyncio.run(main())
