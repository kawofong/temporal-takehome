"""
Module to run the worker.
"""

import asyncio
import logging

from temporalio.client import Client
from temporalio.worker import Worker

from activities import get_user
from constants import TASK_QUEUE_NAME
from workflows import CustomerRewardAccount


async def main():
    """
    Main function to start the worker.
    """
    logging.basicConfig(level=logging.INFO)
    # TODO(kawo): externalize connection string
    client = await Client.connect("localhost:7233", namespace="default")
    worker = Worker(
        client,
        task_queue=TASK_QUEUE_NAME,
        workflows=[CustomerRewardAccount],
        activities=[get_user],
    )
    print("\nWorker started, ctrl+c to exit\n")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
