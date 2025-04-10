"""
Module for defining temporal workflows.
"""

from datetime import timedelta

from temporalio import workflow

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from activities import say_hello
    from constants import CustomerRewardLevel


@workflow.defn
class CustomerRewardAccount:
    def __init__(self):
        self.level: CustomerRewardLevel = CustomerRewardLevel.BASIC
        self.points: int = 0
        self.active: bool = True

    @workflow.run
    async def run(self, name: str) -> str:
        # TODO(kawo): call some external APIs to confirm user exists

        # TODO(kawo): while account is active, keep track of points

        # TODO(kawo): create a handler to add points

        # TODO(kawo): promote level based on points

        # TODO(kawo): create a handler to leave program and complete workflow

        return await workflow.execute_activity(
            say_hello, name, start_to_close_timeout=timedelta(seconds=5)
        )
