"""Unit tests for AWS client authentication and session management."""

import pytest
import boto3
from unittest.mock import patch, MagicMock
from ecsctl.aws_client import AWSClient
from ecsctl.exceptions import AuthenticationError

@pytest.fixture
def aws_client():
    """Create AWSClient instance for testing."""
    with patch('ecsctl.aws_client.load_dotenv'):
        return AWSClient(profile_name='test-profile')

def test_init_with_profile():
    """Test initialization with profile name."""
    with patch('ecsctl.aws_client.load_dotenv'):
        client = AWSClient(profile_name='test-profile')
        assert client.profile_name == 'test-profile'
        assert client.region == 'ap-southeast-1'

def test_authenticate_success(aws_client):
    """Test successful role assumption."""
    mock_session = MagicMock()
    mock_sts = MagicMock()
    mock_sts.assume_role.return_value = {
        'Credentials': {
            'AccessKeyId': 'test-key',
            'SecretAccessKey': 'test-secret',
            'SessionToken': 'test-token'
        }
    }
    mock_session.client.return_value = mock_sts

    with patch('boto3.Session', return_value=mock_session):
        session = aws_client.authenticate('arn:aws:iam::123456789012:role/TestRole')
        assert isinstance(session.__dict__, dict)
        mock_sts.assume_role.assert_called_once()

def test_authenticate_failure(aws_client):
    """Test authentication failure."""
    mock_session = MagicMock()
    mock_sts = MagicMock()
    mock_sts.assume_role.side_effect = Exception('Auth failed')
    mock_session.client.return_value = mock_sts

    with patch('boto3.Session', return_value=mock_session):
        with pytest.raises(AuthenticationError):
            aws_client.authenticate('arn:aws:iam::123456789012:role/TestRole') 