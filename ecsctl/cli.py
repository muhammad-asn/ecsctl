import click
from ecsctl.ecs_controller import ECSController
from ecsctl.exceptions import ECSCommandError
from rich.table import Table
import subprocess
import sys
from typing import Optional
from ecsctl.utils import ignore_user_entered_signals
from ecsctl import __version__

@click.group()
@click.version_option(version=__version__, prog_name="ecsctl")
def cli():
    """ECS command line tool that mimics kubectl."""
    pass

@cli.command('use-cluster')
@click.argument('cluster_name')
def use_cluster(cluster_name: str):
    """Select ECS cluster to use."""
    try:
        ecs = ECSController()
        clusters = ecs.get_clusters()
        
        if cluster_name not in clusters:
            click.echo(f"Error: Cluster '{cluster_name}' not found. Available clusters:", err=True)
            for cluster in clusters:
                click.echo(f"  - {cluster}")
            sys.exit(1)
            
        ecs.config.set_current_cluster(cluster_name)
        click.echo(f"Switched to cluster '{cluster_name}'")
    except ECSCommandError as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command('get-clusters')
def get_clusters():
    """List available ECS clusters."""
    try:
        ecs = ECSController()
        clusters = ecs.get_clusters()
        current = ecs.config.get_current_cluster()
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Cluster Name")
        table.add_column("Current")
        
        for cluster in clusters:
            table.add_row(
                cluster,
                "*" if cluster == current else ""
            )
        
        ecs.console.print(table)
    except ECSCommandError as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.group()
def get():
    """Get ECS resources."""
    pass

@get.command('ec2')
def get_ec2():
    """Get EC2 instances in current cluster."""
    try:
        ecs = ECSController()
        current_cluster = ecs.config.get_current_cluster()
        
        if not current_cluster:
            click.echo("Error: No cluster selected. Use 'ecsctl use-cluster' first.", err=True)
            sys.exit(1)
            
        instances = ecs.get_ec2_instances(current_cluster)
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Instance ID")
        table.add_column("Type")
        table.add_column("State")
        table.add_column("Status")
        table.add_column("Running Tasks")
        
        for instance in instances:
            table.add_row(
                instance['InstanceId'],
                instance['InstanceType'],
                instance['State'],
                instance['Status'],
                str(instance['RunningTasks'])
            )
        
        ecs.console.print(table)
    except ECSCommandError as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@get.command('services')
def get_services():
    """Get services in current cluster, including EC2 instance IDs."""
    try:
        ecs = ECSController()
        current_cluster = ecs.config.get_current_cluster()
        
        if not current_cluster:
            click.echo("Error: No cluster selected. Use 'ecsctl use-cluster' first.", err=True)
            sys.exit(1)
            
        services = ecs.get_services(current_cluster)
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Name")
        table.add_column("Status")
        table.add_column("Task Definition")
        table.add_column("Desired")
        table.add_column("Running")
        table.add_column("Pending")
        table.add_column("EC2 Instances", no_wrap=False)
        
        for service in services:
            ec2_instances = (
                '\n'.join(instance.strip() for instance in service['EC2Instances'].split(','))
                if service['EC2Instances']
                else '-'
            )
            
            table.add_row(
                service['ServiceName'],
                service['Status'],
                service['TaskDefinition'].split('/')[-1],
                str(service['DesiredCount']),
                str(service['RunningCount']),
                str(service['PendingCount']),
                ec2_instances
            )
        
        ecs.console.print(table)
    except ECSCommandError as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@get.command('task-definitions')
@click.option('--family', help='Filter by task definition family')
def get_task_definitions(family: Optional[str]):
    """Get task definitions."""
    try:
        ecs = ECSController()
        task_definitions = ecs.get_task_definitions(family)
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Family")
        table.add_column("Revision")
        table.add_column("Status")
        table.add_column("CPU")
        table.add_column("Memory")
        table.add_column("Last Updated")
        
        for td in task_definitions:
            table.add_row(
                td['Family'],
                str(td['Revision']),
                td['Status'],
                td['Cpu'],
                td['Memory'],
                td['LastUpdated']
            )
        
        ecs.console.print(table)
    except ECSCommandError as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command('exec')
@click.argument('instance_id')
def exec_instance(instance_id: str):
    """Execute interactive shell on EC2 instance using SSM."""
    try:
        ecs = ECSController()
        current_cluster = ecs.config.get_current_cluster()
        
        if not current_cluster:
            click.echo("Error: No cluster selected. Use 'ecsctl use-cluster' first.", err=True)
            sys.exit(1)

        # Verify instance exists in cluster
        instance = ecs.get_instance_details(current_cluster, instance_id)
        if not instance:
            click.echo(f"Error: Instance '{instance_id}' not found in cluster '{current_cluster}'", err=True)
            sys.exit(1)

        # Check SSM availability
        if not ecs.check_ssm_status(instance_id):
            click.echo(f"Error: SSM is not available on instance '{instance_id}'", err=True)
            sys.exit(1)

        # Start SSM session with profile and region
        click.echo(f"Starting session with instance '{instance_id}'...")
        cmd = ['aws', 'ssm', 'start-session', '--target', instance_id]
        
        # Add profile if available
        if ecs.aws_client.profile_name:
            cmd.extend(['--profile', ecs.aws_client.profile_name])
        
        # Add region
        cmd.extend(['--region', ecs.aws_client.region])
        
        # Check if bash is available and use it if possible
        if subprocess.run(['which', 'bash'], capture_output=True).returncode == 0:
            cmd.extend(['--document-name', 'AWS-StartInteractiveCommand', '--parameters', 'command=bash'])
        
        # Use the context manager for signal handling during subprocess execution
        with ignore_user_entered_signals():
            subprocess.run(cmd)

    except ECSCommandError as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

@cli.command('get-context')
def get_context():
    """Get current context (cluster)."""
    try:
        ecs = ECSController()
        current_cluster = ecs.config.get_current_cluster()
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Context")
        table.add_column("Value")
        
        table.add_row("Current Cluster", current_cluster or "Not set")
        
        ecs.console.print(table)
    except ECSCommandError as e:
        click.echo(f"Error: {str(e)}", err=True)
        sys.exit(1)

if __name__ == '__main__':
    cli()