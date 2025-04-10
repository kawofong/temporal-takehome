"""
Module to run workflow queries.
"""

import asyncio

from temporalio.client import Client

from test_constants import MOCK_USER
from workflows import CustomerRewardAccount


async def main():
    # TODO(kawo): externalize connection string
    client = await Client.connect("localhost:7233", namespace="default")

    handle = client.get_workflow_handle_for(
        CustomerRewardAccount.run, MOCK_USER.user_id
    )
    account_status = await handle.execute_update(CustomerRewardAccount.terminate)
    print(account_status)


if __name__ == "__main__":
    asyncio.run(main())
