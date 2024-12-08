#!/bin/bash

# Default output name based on platform
case "$(uname -s)" in
    Linux*)     output_name=ecsctl-linux;;
    Darwin*)    output_name=ecsctl-macos;;
    *)          output_name=ecsctl;;
esac

# Build executable with Nuitka
python -m nuitka --follow-imports --standalone --onefile ecsctl/cli.py -o "$output_name"