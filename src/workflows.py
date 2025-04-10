"""
Module for defining temporal workflows.
"""

from datetime import datetime, timedelta

from temporalio import workflow
from temporalio.common import RetryPolicy

# Import activity, passing it through the sandbox without reloading the module
with workflow.unsafe.imports_passed_through():
    from activities import get_user
    from constants import CustomerRewardLevel
    from models import CustomerRewardAccountInput, CustomerRewardAccountStatus, UserInfo


@workflow.defn
class CustomerRewardAccount:
    def __init__(self):
        self._level: CustomerRewardLevel = CustomerRewardLevel.BASIC
        self._points: int = 0
        self._is_active: bool = True
        self._user_id: str | None = None
        self._create_time: datetime | None = None
        self._terminate_time: datetime | None = None

    @workflow.run
    async def run(self, inp: CustomerRewardAccountInput) -> CustomerRewardAccountStatus:
        workflow.logger.info("Creating reward account for %s", inp.user_id)
        user: UserInfo = await workflow.execute_activity(
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
        self._user_id = user.id
        self._create_time = workflow.now()
        workflow.logger.info(
            "Reward account for %s created at %s", self._user_id, self._create_time
        )

        while True:
            await workflow.wait_condition(lambda: not self._is_active)
            # If account is inactive, then return and complete the workflow
            if not self._is_active:
                workflow.logger.info(
                    "Terminating reward account for %s at %s",
                    self._user_id,
                    self._terminate_time,
                )
                return CustomerRewardAccountStatus(
                    level=self._level,
                    points=self._points,
                    is_active=self._is_active,
                )

        # TODO(kawo): create a handler to add points

        # TODO(kawo): promote level based on points

    @workflow.query
    def query_reward_status(self) -> CustomerRewardAccountStatus:
        return CustomerRewardAccountStatus(
            level=self._level,
            points=self._points,
            is_active=self._is_active,
        )

    @workflow.update
    def terminate(self) -> CustomerRewardAccountStatus:
        self._is_active = False
        self._terminate_time = workflow.now()
        return CustomerRewardAccountStatus(
            level=self._level,
            points=self._points,
            is_active=self._is_active,
        )
