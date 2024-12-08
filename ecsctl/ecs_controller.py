import boto3
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from ecsctl.aws_client import AWSClient
from ecsctl.config import ClusterConfig
from ecsctl.exceptions import ECSCommandError
from rich.console import Console
import logging



class ECSController:
    """Controller for ECS operations.
    
    Manages interactions with ECS clusters, instances, and containers.
    Handles authentication and provides methods for common ECS operations.
    
    Raises:
        ECSCommandError: If AWS client initialization fails
    """
    
    def __init__(self) -> None:
        """Initialize AWS clients and configuration.
        
        Raises:
            ECSCommandError: If AWS client initialization fails
        """
        try:
            self._initialize_aws_clients()
        except Exception as e:
            raise ECSCommandError(f"Failed to initialize AWS clients: {str(e)}")
        self.logger = logging.getLogger(__name__)

    def _initialize_aws_clients(self) -> None:
        """Set up AWS client connections.
        
        Creates authenticated sessions and initializes service clients.
        Uses role assumption if AWS_ROLE_ARN is set.
        """
        self.aws_client = AWSClient()
        role_arn = os.getenv('AWS_ROLE_ARN')
        
        session = (
            self.aws_client.authenticate(role_arn) if role_arn
            else boto3.Session(
                profile_name=self.aws_client.profile_name,
                region_name=self.aws_client.region
            )
        )
        
        self.ecs_client = session.client('ecs')
        self.ec2_client = session.client('ec2')
        self.ssm_client = session.client('ssm')
        self.console = Console()
        self.config = ClusterConfig()

    def get_clusters(self) -> List[str]:
        """Get list of all ECS clusters."""
        try:
            clusters = self.ecs_client.list_clusters()['clusterArns']
            return [cluster.split('/')[-1] for cluster in clusters]
        except Exception as e:
            raise ECSCommandError(f"Failed to get clusters: {str(e)}")

    def get_ec2_instances(self, cluster_name: str) -> List[Dict[Any, Any]]:
        """Get EC2 instances for specified cluster."""
        try:
            container_instances = self.ecs_client.list_container_instances(
                cluster=cluster_name
            )['containerInstanceArns']
            
            instances = []
            if container_instances:
                response = self.ecs_client.describe_container_instances(
                    cluster=cluster_name,
                    containerInstances=container_instances
                )
                
                for instance in response['containerInstances']:
                    ec2_response = self.ec2_client.describe_instances(
                        InstanceIds=[instance['ec2InstanceId']]
                    )
                    
                    instance_info = {
                        'InstanceId': instance['ec2InstanceId'],
                        'InstanceType': ec2_response['Reservations'][0]['Instances'][0]['InstanceType'],
                        'State': ec2_response['Reservations'][0]['Instances'][0]['State']['Name'],
                        'Status': instance['status'],
                        'RunningTasks': instance['runningTasksCount']
                    }
                    instances.append(instance_info)
            
            return instances
        except Exception as e:
            raise ECSCommandError(f"Failed to get EC2 instances: {str(e)}")

    def get_containers(self, cluster_name: str) -> List[Dict[Any, Any]]:
        """Get containers for specified cluster with EC2 instance mapping."""
        try:
            tasks = self.ecs_client.list_tasks(cluster=cluster_name)['taskArns']
            containers = []
            
            if tasks:
                response = self.ecs_client.describe_tasks(
                    cluster=cluster_name,
                    tasks=tasks
                )
                
                for task in response['tasks']:
                    # Get EC2 instance ID for the task
                    container_instance_arn = task.get('containerInstanceArn')
                    ec2_instance_id = 'N/A'
                    
                    if container_instance_arn:
                        container_instance = self.ecs_client.describe_container_instances(
                            cluster=cluster_name,
                            containerInstances=[container_instance_arn]
                        )['containerInstances'][0]
                        ec2_instance_id = container_instance['ec2InstanceId']
                    
                    for container in task['containers']:
                        container_info = {
                            'Name': container['name'],
                            'Status': container['lastStatus'],
                            'TaskId': task['taskArn'].split('/')[-1],
                            'CPU': container.get('cpu', 'N/A'),
                            'Memory': container.get('memory', 'N/A'),
                            'EC2Instance': ec2_instance_id,
                            'Created': datetime.fromtimestamp(
                                task['createdAt'].timestamp()
                            ).strftime('%Y-%m-%d %H:%M:%S')
                        }
                        containers.append(container_info)
            
            return containers
        except Exception as e:
            raise ECSCommandError(f"Failed to get containers: {str(e)}")

    def get_instance_details(self, cluster_name: str, instance_id: str) -> Optional[Dict[str, Any]]:
        """Get details for a specific EC2 instance in the cluster."""
        try:
            instances = self.get_ec2_instances(cluster_name)
            return next((instance for instance in instances if instance['InstanceId'] == instance_id), None)
        except Exception as e:
            raise ECSCommandError(f"Failed to get instance details: {str(e)}")

    def get_services(self, cluster_name: str) -> List[Dict[str, Any]]:
        """
        Get services for specified cluster, including EC2 instance IDs.

        Args:
            cluster_name: Name of the ECS cluster

        Returns:
            List of service details with EC2 instance IDs

        Raises:
            ECSCommandError: If service retrieval fails
        """
        try:
            services_list = self.ecs_client.list_services(cluster=cluster_name)['serviceArns']
            services = []
            
            if services_list:
                # AWS API has a limit of 10 services per describe_services call
                for i in range(0, len(services_list), 10):
                    batch = services_list[i:i + 10]
                    response = self.ecs_client.describe_services(
                        cluster=cluster_name,
                        services=batch
                    )
                    
                    for service in response['services']:
                        # Get tasks for the service
                        task_arns = self.ecs_client.list_tasks(
                            cluster=cluster_name,
                            serviceName=service['serviceName']
                        )['taskArns']
                        
                        ec2_instance_ids = set()
                        if task_arns:
                            tasks = self.ecs_client.describe_tasks(
                                cluster=cluster_name,
                                tasks=task_arns
                            )['tasks']
                            
                            for task in tasks:
                                container_instance_arn = task.get('containerInstanceArn')
                                if container_instance_arn:
                                    container_instance = self.ecs_client.describe_container_instances(
                                        cluster=cluster_name,
                                        containerInstances=[container_instance_arn]
                                    )['containerInstances'][0]
                                    ec2_instance_ids.add(container_instance['ec2InstanceId'])
                        
                        service_info = {
                            'ServiceName': service['serviceName'],
                            'Status': service['status'],
                            'TaskDefinition': service['taskDefinition'],
                            'DesiredCount': service['desiredCount'],
                            'RunningCount': service['runningCount'],
                            'PendingCount': service['pendingCount'],
                            'EC2Instances': ', '.join(ec2_instance_ids)
                        }
                        services.append(service_info)
            
            return services
        except Exception as e:
            raise ECSCommandError(f"Failed to get services: {str(e)}")

    def get_task_definitions(self, family: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get task definitions with optional family filter.

        Args:
            family: Optional task definition family filter

        Returns:
            List of task definition details

        Raises:
            ECSCommandError: If task definition retrieval fails
        """
        try:
            kwargs = {'familyPrefix': family} if family else {}
            task_def_arns = self.ecs_client.list_task_definitions(**kwargs)['taskDefinitionArns']
            task_definitions = []
            
            for arn in task_def_arns:
                response = self.ecs_client.describe_task_definition(taskDefinition=arn)
                td = response['taskDefinition']
                
                # Calculate total CPU and memory
                cpu = td.get('cpu', 'N/A')
                memory = td.get('memory', 'N/A')
                
                task_def_info = {
                    'Family': td['family'],
                    'Revision': td['revision'],
                    'Status': td['status'],
                    'Cpu': cpu,
                    'Memory': memory,
                    'LastUpdated': datetime.fromtimestamp(
                        td['registeredAt'].timestamp()
                    ).strftime('%Y-%m-%d %H:%M:%S')
                }
                task_definitions.append(task_def_info)
            
            return task_definitions
        except Exception as e:
            raise ECSCommandError(f"Failed to get task definitions: {str(e)}")

    def check_ssm_status(self, instance_id: str) -> bool:
        """
        Check if SSM is available on the specified EC2 instance.

        Args:
            instance_id (str): The ID of the EC2 instance to check

        Returns:
            bool: True if SSM is available, False otherwise
        """
        try:
            response = self.ssm_client.describe_instance_information(
                Filters=[{
                    'Key': 'InstanceIds',
                    'Values': [instance_id]
                }]
            )
            
            # If we find the instance in SSM and it's online, return True
            return len(response['InstanceInformationList']) > 0 and \
                   response['InstanceInformationList'][0]['PingStatus'] == 'Online'
        except Exception as e:
            self.logger.warning(f"Failed to check SSM status for instance {instance_id}: {str(e)}")
            return False