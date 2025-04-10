"""
Module for defining temporal activities.
"""

import asyncio

from temporalio import activity

from models import UserInfo


@activity.defn
async def get_user(user_id: str) -> UserInfo:
    activity.logger.info("Getting user info for %s", user_id)
    asyncio.sleep(1)  # simulate some work
    return UserInfo(id=user_id, name="John Doe")
