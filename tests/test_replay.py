"""
Test module to run replay test to prevent workflow non-determinism.
"""

import json
from uuid import uuid4

import pytest
from temporalio.client import WorkflowHistory
from temporalio.worker import Replayer

from workflows import CustomerRewardAccount


@pytest.mark.asyncio
async def test_customer_reward_account_workflow_replay():
    """
    Verify determinism of the customer reward account workflow
    """
    with open("tests/full_events.json", encoding="utf-8") as f:
        data = json.load(f)
    event_history = WorkflowHistory.from_json(
        workflow_id=str(uuid4()),
        history=data,
    )
    replayer = Replayer(workflows=[CustomerRewardAccount])
    result = await replayer.replay_workflow(
        history=event_history, raise_on_replay_failure=True
    )
    assert result.replay_failure is None
