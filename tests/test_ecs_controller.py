"""Unit tests for ECS controller functionality."""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from ecsctl.ecs_controller import ECSController
from ecsctl.exceptions import ECSCommandError

@pytest.fixture
def ecs_controller():
    """Create ECSController instance for testing."""
    with patch('ecsctl.ecs_controller.AWSClient'), \
         patch('boto3.Session'), \
         patch('ecsctl.ecs_controller.ClusterConfig'):
        return ECSController()

def test_get_clusters(ecs_controller):
    """Test retrieving ECS clusters."""
    mock_response = {
        'clusterArns': [
            'arn:aws:ecs:region:account:cluster/cluster1',
            'arn:aws:ecs:region:account:cluster/cluster2'
        ]
    }
    ecs_controller.ecs_client.list_clusters = MagicMock(return_value=mock_response)

    clusters = ecs_controller.get_clusters()
    assert clusters == ['cluster1', 'cluster2']
    ecs_controller.ecs_client.list_clusters.assert_called_once()

def test_get_ec2_instances(ecs_controller):
    """Test retrieving EC2 instances in cluster."""
    mock_container_instances = {
        'containerInstanceArns': ['arn:aws:ecs:region:account:container-instance/id']
    }
    mock_describe_instances = {
        'containerInstances': [{
            'ec2InstanceId': 'i-1234567890',
            'status': 'ACTIVE',
            'runningTasksCount': 5
        }]
    }
    mock_ec2_response = {
        'Reservations': [{
            'Instances': [{
                'InstanceType': 't3.micro',
                'State': {'Name': 'running'}
            }]
        }]
    }

    ecs_controller.ecs_client.list_container_instances = MagicMock(
        return_value=mock_container_instances
    )
    ecs_controller.ecs_client.describe_container_instances = MagicMock(
        return_value=mock_describe_instances
    )
    ecs_controller.ec2_client.describe_instances = MagicMock(
        return_value=mock_ec2_response
    )

    instances = ecs_controller.get_ec2_instances('test-cluster')
    assert len(instances) == 1
    assert instances[0]['InstanceId'] == 'i-1234567890'
    assert instances[0]['InstanceType'] == 't3.micro' 