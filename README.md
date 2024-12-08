<div align="center">
  <img src="assets/trisula-ecsctl.jpg" alt="ECSCTL - Powered by Trisula" width="400"/>
  
  # ECSCTL
  ### Command the Seas of Containers
</div>

## Overview

ECSCTL is a Python-based tool for managing Amazon ECS clusters, offering kubectl-like commands via Boto3.

## Features

- **Cluster Management**: List and switch between ECS clusters.
- **EC2 Fleet Vision**: View and monitor EC2 instances.
- **Container Insight**: Track container statuses and details.
- **Instance Access**: Secure SSH access via AWS SSM.

## Prerequisites

- [Python 3.11+](https://www.python.org/downloads/)
- [AWS CLI >= 2.19.x](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

## Installation

### Via pip (Recommended)

```bash
$ pip install ecsctl
```

### From Source

```bash
$ git clone https://github.com/username/ecsctl.git
$ cd ecsctl
$ pip install -e .
```

## Quick Start

```bash
$ ecsctl --help
Usage: ecsctl [OPTIONS] COMMAND [ARGS]...

  ECS command line tool that mimics kubectl.

Options:
  --help  Show this message and exit.

Commands:
  exec          Execute interactive shell on EC2 instance using SSM.
  get           Get ECS resources.
  get-clusters  List available ECS clusters.
  get-context   Get current context (cluster).
  use-cluster   Select ECS cluster to use.
```

## Configuration

ECSCTL uses AWS credentials from environment variables or profiles, with optional role assumption via `AWS_ROLE_ARN`.

## Contributing

We welcome contributions! Here's how you can help:

### Development Setup
1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/ecsctl.git
   cd ecsctl
   ```
3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
4. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### Contributing Guidelines
- Follow PEP 8 style guidelines
- Write tests for new features
- Update documentation as needed
- Submit pull requests against the `main` branch

### Running Tests

```bash
pytest tests/
```
