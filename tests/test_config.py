"""Unit tests for cluster configuration management."""

import pytest
import json
from pathlib import Path
from unittest.mock import patch, mock_open
from ecsctl.config import ClusterConfig

@pytest.fixture
def cluster_config():
    """Create ClusterConfig instance for testing."""
    with patch('pathlib.Path.mkdir'), \
         patch('pathlib.Path.exists', return_value=True):
        return ClusterConfig()

def test_get_current_cluster(cluster_config):
    """Test getting current cluster configuration."""
    mock_config = {'current-cluster': 'test-cluster'}
    mock_file = mock_open(read_data=json.dumps(mock_config))

    with patch('builtins.open', mock_file):
        current_cluster = cluster_config.get_current_cluster()
        assert current_cluster == 'test-cluster'

