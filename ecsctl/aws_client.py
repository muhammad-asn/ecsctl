"""AWS authentication and session management."""

import os
from dotenv import load_dotenv
import boto3
from typing import Optional
from .exceptions import AuthenticationError

class AWSClient:
    """Interface for authenticating with Amazon Web Services (AWS).
    
    Handles AWS authentication and session management with support for role assumption.
    
    Attributes:
        profile_name (Optional[str]): AWS profile name for authentication
        region (str): AWS region for API calls
    
    Example:
        >>> client = AWSClient(profile_name="dev")
        >>> session = client.authenticate("arn:aws:iam::123456789012:role/MyRole")
    """

    def __init__(self, profile_name: Optional[str] = None) -> None:
        """Initialize AWS client.
        
        Args:
            profile_name: AWS profile name to use for authentication. If None,
                         uses AWS_PROFILE environment variable.
        """
        # Load environment variables from .env file
        load_dotenv()
        
        self.profile_name = profile_name or os.getenv('AWS_PROFILE')
        self.region = os.getenv('AWS_REGION', 'ap-southeast-1')

    def authenticate(self, role_arn: str, session_name: Optional[str] = "AssumeRoleSession"):
        """
        Authenticate with AWS and assume the specified role
        Args:
            role_arn (str): ARN of the role to assume
            session_name (str): Name for the assumed role session
        Returns:
            boto3.Session: Authenticated AWS session with assumed role credentials
        """
        try:
            # Create base session using either profile or environment credentials
            if self.profile_name:
                session = boto3.Session(profile_name=self.profile_name)
            else:
                session = boto3.Session(region_name=self.region)

            # Assume role using STS
            sts_client = session.client('sts')
            assumed_role = sts_client.assume_role(
                RoleArn=role_arn,
                RoleSessionName=session_name
            )

            # Return new session with temporary credentials
            return boto3.Session(
                aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
                aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
                aws_session_token=assumed_role['Credentials']['SessionToken'],
                region_name=self.region
            )
        except Exception as e:
            raise AuthenticationError(f"Failed to authenticate with AWS: {str(e)}", e)

    def get_client(self, service_name: str):
        """Get a boto3 client for the specified service."""
        return boto3.client(service_name)