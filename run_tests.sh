#!/usr/bin/env bash
set -e

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BUILD_DIR="${SCRIPT_DIR}/build"

echo "=== Building Voyager Sim C++ Project ==="
mkdir -p "${BUILD_DIR}"
cd "${BUILD_DIR}"

cmake "${SCRIPT_DIR}/modules/voyager-sim"
make

echo ""
echo "=== Running Physics Engine Tests ==="
./test_rigidbody
