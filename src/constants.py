"""
Module for defining constants.
"""

from enum import StrEnum

TASK_QUEUE_NAME = "hello-task-queue"


class CustomerRewardLevel(StrEnum):
    BASIC = "BASIC"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"
