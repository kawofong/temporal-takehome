"""
Module for defining temporal activities.
"""

from temporalio import activity

from models import UserInfo


@activity.defn
async def get_user(user_id: str) -> UserInfo:
    activity.logger.info("Getting user info for %s", user_id)
    return UserInfo(id=user_id, name="John Doe")
