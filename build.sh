#!/bin/bash

# Default to AMD64 if not specified
arch=$(uname -m)
if [ "$arch" = "x86_64" ]; then
    arch="amd64"
elif [ "$arch" = "arm64" ] || [ "$arch" = "aarch64" ]; then
    arch="arm64"
fi

# Use environment variable if provided, otherwise construct default name
if [ -n "$output_name" ]; then
    final_output_name="$output_name"
else
    # Default output name based on platform and architecture
    case "$(uname -s)" in
        Linux*)     final_output_name="ecsctl-linux-${arch}";;
        Darwin*)    final_output_name="ecsctl-macos-${arch}";;
        *)          final_output_name="ecsctl-${arch}";;
    esac
fi

echo "Building for architecture: ${arch}"
echo "Output name: ${final_output_name}"

# Build executable with Nuitka
python -m nuitka \
    --follow-imports \
    --standalone \
    --onefile \
    ecsctl/cli.py \
    -o "$final_output_name"
