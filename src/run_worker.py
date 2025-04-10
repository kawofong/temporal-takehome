"""
Module to run the worker.
"""

import asyncio

from temporalio.client import Client
from temporalio.worker import Worker

from activities import say_hello
from constants import TASK_QUEUE_NAME
from workflows import SayHello


async def main():
    """
    Main function to start the worker.
    """
    # TODO(kawo): externalize connection string
    client = await Client.connect("localhost:7233", namespace="default")

    worker = Worker(
        client,
        task_queue=TASK_QUEUE_NAME,
        workflows=[SayHello],
        activities=[say_hello],
    )
    print("\nWorker started, ctrl+c to exit\n")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
