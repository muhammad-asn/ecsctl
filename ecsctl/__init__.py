"""
ecsctl - A kubectl-like CLI tool for Amazon ECS
"""

import os
import tomli
from pathlib import Path
from typing import Optional

def get_version() -> str:
    """
    Get the current version from pyproject.toml.
    
    Returns:
        str: Version string in the format "x.y.z" or "x.y.z-dev-hash"
    
    Raises:
        FileNotFoundError: If pyproject.toml cannot be found
        KeyError: If version information is missing from pyproject.toml
    """
    try:
        pyproject_path = Path(__file__).parent.parent / "pyproject.toml"
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomli.load(f)
        return pyproject_data["tool"]["poetry"]["version"]
    except (FileNotFoundError, KeyError) as e:
        # Fallback version for when running from compiled binary
        return "0.1.0"

__version__ = get_version()
