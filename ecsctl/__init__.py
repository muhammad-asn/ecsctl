"""
ecsctl - A kubectl-like CLI tool for Amazon ECS
"""

import os
from typing import Optional

# Default version - this will be used when building with Nuitka
VERSION = "0.1.0"

def get_version() -> str:
    """
    Get the current version, with priority:
    1. Hardcoded VERSION constant
    
    Returns:
        str: Version string in the format "x.y.z" or "x.y.z-dev-hash"
    """
    return VERSION

__version__ = get_version()
