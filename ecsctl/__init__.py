"""
ecsctl - A kubectl-like CLI tool for Amazon ECS
"""

import os
from typing import Optional

def get_version() -> str:
    """
    Get the current version from environment variables (set by CI/CD)
    or fallback to a default version.
    
    Environment Variables:
        ECSCTL_VERSION: Version string to use (typically set by CI/CD)
    
    Returns:
        str: Version string in the format "x.y.z" or "x.y.z-dev-hash"
    """
    return os.environ.get('ECSCTL_VERSION', '0.1.0')

__version__ = get_version()
