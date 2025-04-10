"""
Module for defining temporal workflows.
"""

from datetime import timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from activities import get_user
    from constants import CustomerRewardLevel
    from models import CustomerRewardAccountInput


@workflow.defn
class CustomerRewardAccount:
    def __init__(self):
        self.level: CustomerRewardLevel = CustomerRewardLevel.BASIC
        self.points: int = 0
        self.active: bool = True

    @workflow.run
    async def run(self, inp: CustomerRewardAccountInput) -> dict:
        return await workflow.execute_activity(
            get_user,
            inp.user_id,
            start_to_close_timeout=timedelta(seconds=1),
            retry_policy=RetryPolicy(
                backoff_coefficient=2.0,
                maximum_attempts=3,
                initial_interval=timedelta(seconds=1),
                maximum_interval=timedelta(seconds=4),
            ),
        )
        # TODO(kawo): while account is active, keep track of points

        # TODO(kawo): create a handler to add points

        # TODO(kawo): promote level based on points

        # TODO(kawo): create a handler to leave program and complete workflow
