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

### From Binary
Download the latest release for your platform:
- [Latest Releases](https://github.com/muhammad-asn/ecsctl/releases)

```bash
# Linux/MacOS
chmod +x ecsctl
sudo mv ecsctl /usr/local/bin/

# Or install to user directory
mkdir -p ~/.local/bin
mv ecsctl ~/.local/bin/
```

### From Source
```bash
# Clone the repository
git clone https://github.com/muhammad-asn/ecsctl.git
cd ecsctl

# Install in editable mode with all dependencies
pip install -e .
```

## Quick Start

```bash
$ ecsctl --help   
Usage: ecsctl [OPTIONS] COMMAND [ARGS]...

  ECS command line tool that mimics kubectl.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  exec          Execute interactive shell on EC2 instance using SSM.
  get           Get ECS resources.
  get-clusters  List available ECS clusters.
  get-context   Get current context (cluster).
  use-cluster   Select ECS cluster to use.
```

## Configuration   
1. Set AWS credentials (./aws/config)
  ```
  [profile root-profile]
  region = us-east-1
  output = json

  [profile profile-1]
  role_arn = arn:aws:iam::<account-id>:role/<role-name>
  region = us-east-1
  output = json
  source_profile = root-profile
  ```     

2. Export environment variables
  ```
  export AWS_ACCESS_KEY_ID=
  export AWS_SECRET_ACCESS_KEY=
  export AWS_REGION=ap-southeast-1
  export AWS_PROFILE= <profile-name>
  ```

## Contributing

We welcome contributions! Here's how you can help:

### Development Setup
1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/muhammad-asn/ecsctl.git
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
