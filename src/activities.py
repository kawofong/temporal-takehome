"""
Module for defining temporal activities.
"""

from temporalio import activity


@activity.defn
async def say_hello(name: str) -> str:
    return f"Hello, {name}!"
