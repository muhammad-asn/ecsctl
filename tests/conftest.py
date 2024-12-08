"""Pytest configuration and shared fixtures."""

import pytest
import os
from unittest.mock import patch

@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for testing."""
    with patch.dict(os.environ, {
        'AWS_REGION': 'ap-southeast-1',
        'AWS_PROFILE': 'test-profile'
    }):
        yield

@pytest.fixture(autouse=True)
def mock_aws_credentials():
    """Mock AWS credentials for testing."""
    with patch.dict(os.environ, {
        'AWS_ACCESS_KEY_ID': 'testing',
        'AWS_SECRET_ACCESS_KEY': 'testing',
        'AWS_SECURITY_TOKEN': 'testing',
        'AWS_SESSION_TOKEN': 'testing'
    }):
        yield 