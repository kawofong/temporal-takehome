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
    from models import (
        AddPointInput,
        CustomerRewardAccountInput,
        CustomerRewardAccountStatus,
        UserInfo,
    )

MAX_UPDATE_OPERATION_COUNT = 5000


@workflow.defn
class CustomerRewardAccount:
    """
    Customer reward account workflow."""

    def __init__(self):
        self._level: CustomerRewardLevel = CustomerRewardLevel.BASIC
        self._points: int = 0
        self._is_active: bool = True
        self._user_id: str | None = None
        self._create_time: datetime | None = None
        self._cancel_time: datetime | None = None
        self._update_count: int = 0

    @workflow.run
    async def run(self, inp: CustomerRewardAccountInput) -> CustomerRewardAccountStatus:
        workflow.logger.info("Creating reward account for %s", inp.user_id)
        self._create_time = workflow.now()
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
        workflow.logger.info(
            "Reward account for %s created at %s", self._user_id, self._create_time
        )

        while True:
            await workflow.wait_condition(
                lambda: not self._is_active
                or self._update_count >= MAX_UPDATE_OPERATION_COUNT
            )

            # If account is inactive, then return and complete the workflow
            if not self._is_active:
                workflow.logger.info(
                    "Terminating reward account for %s at %s",
                    self._user_id,
                    self._cancel_time,
                )
                await workflow.wait_condition(workflow.all_handlers_finished)
                return CustomerRewardAccountStatus(
                    level=self._level,
                    points=self._points,
                    is_active=self._is_active,
                )

            # When number of update operations exceeds 5,000, continue-as-new the workflow.
            # 5,000 update operations roughly equals to 25,000 events in history.
            if self._update_count >= MAX_UPDATE_OPERATION_COUNT:
                workflow.logger.info(
                    "Continuing as new because update count [%i] exceeds %i.",
                    self._update_count,
                    MAX_UPDATE_OPERATION_COUNT,
                )
                await workflow.wait_condition(workflow.all_handlers_finished)
                workflow.continue_as_new(
                    CustomerRewardAccountInput(
                        user_id=self._user_id,
                        starting_points=self._points,
                        starting_level=self._level,
                    )
                )

    @workflow.query
    def query_reward_status(self) -> CustomerRewardAccountStatus:
        """
        Returns the current status of the reward account.
        """
        return CustomerRewardAccountStatus(
            level=self._level,
            points=self._points,
            is_active=self._is_active,
        )

    @workflow.update
    async def cancel(self) -> CustomerRewardAccountStatus:
        """
        Terminates the reward account.
        """
        self._is_active = False
        self._cancel_time = workflow.now()
        return CustomerRewardAccountStatus(
            level=self._level,
            points=self._points,
            is_active=self._is_active,
        )

    @workflow.update
    async def add_points(self, inp: AddPointInput) -> CustomerRewardAccountStatus:
        """
        Adds points to the reward account.
        """
        workflow.logger.info("Adding points for %s by %i", self._user_id, inp.points)
        self._update_count += 1
        self._points += inp.points
        self._points = max(self._points, 0)  # prevent negative points
        if 500 <= self._points < 1000:
            self._level = CustomerRewardLevel.GOLD
        elif self._points >= 1000:
            self._level = CustomerRewardLevel.PLATINUM
        else:
            self._level = CustomerRewardLevel.BASIC
        return CustomerRewardAccountStatus(
            level=self._level,
            points=self._points,
            is_active=self._is_active,
        )

    @add_points.validator
    def validate_add_point(self, inp: AddPointInput) -> None:
        """
        Validate input point to be an integer. Reject otherwise.
        """
        if not isinstance(inp.points, int):
            raise ValueError("Points must be an integer.")
