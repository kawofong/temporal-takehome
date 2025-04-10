"""
Modules for defining types
"""

from dataclasses import dataclass

from constants import CustomerRewardLevel


@dataclass
class CustomerRewardAccountInput:
    user_id: str


@dataclass
class UserInfo:
    id: str
    name: str


@dataclass
class CustomerRewardAccountStatus:
    level: CustomerRewardLevel
    points: int
    is_active: bool
