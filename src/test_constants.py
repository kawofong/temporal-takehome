"""
Module for defining test-related constants.
"""

from models import CustomerRewardAccountInput

MOCK_USER = CustomerRewardAccountInput(user_id="test-user-id")
TEST_TASK_QUEUE = "test-translation-workflow"
