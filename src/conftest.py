import asyncio
import os
import sys
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from temporalio.client import Client
from temporalio.testing import WorkflowEnvironment


def pytest_addoption(parser):
    parser.addoption(
        "-E",
        "--workflow-environment",
        default="time-skipping",
        help="Which workflow environment to use ('local', 'time-skipping', or ip:port for existing server)",
    )


@pytest.fixture(scope="session")
def env_type(request: pytest.FixtureRequest) -> str:
    return request.config.getoption("--workflow-environment")


@pytest_asyncio.fixture(scope="session")
async def env(env_type: str) -> AsyncGenerator[WorkflowEnvironment, None]:
    if env_type == "local":
        env = await WorkflowEnvironment.start_local(
            dev_server_extra_args=[
                "--dynamic-config-value",
                "system.forceSearchAttributesCacheRefreshOnRead=true",
                "--dynamic-config-value",
                "system.enableEagerWorkflowStart=true",
                "--dynamic-config-value",
                "frontend.enableExecuteMultiOperation=true",
            ],
        )
    elif env_type == "time-skipping":
        env = await WorkflowEnvironment.start_time_skipping()
    else:
        env = WorkflowEnvironment.from_client(await Client.connect(env_type))
    yield env
    await env.shutdown()


@pytest_asyncio.fixture
async def client(env: WorkflowEnvironment) -> Client:
    return env.client
