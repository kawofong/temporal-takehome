"""
Module for defining temporal activities.
"""

import asyncio

from temporalio import activity

from models import UserInfo


@activity.defn
async def get_user(user_id: str) -> UserInfo:
    activity.logger.info("Getting user info for %s", user_id)
    await asyncio.sleep(0.5)
    return UserInfo(id=user_id, name="John Doe")
