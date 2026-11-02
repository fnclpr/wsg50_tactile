#!/bin/bash
set -e

# Source the ROS2 underlay.
source /opt/ros/jazzy/setup.bash

# Source the workspace overlay, if it has been colcon-built yet
# (it won't exist until Step 3+, when we create actual ROS2 packages).
if [ -f /workspace/install/setup.bash ]; then
    source /workspace/install/setup.bash
fi

# tactile_core is bind-mounted, not baked into the image (see Dockerfile
# header comment), so install it in editable mode every container start.
# This is idempotent and takes ~1-2s; it guarantees the package is
# always importable and always reflects the current source on disk,
# even after `git pull` or manual edits on the host.
if [ -f /workspace/src/tactile_core/pyproject.toml ]; then
    pip install --no-cache-dir --break-system-packages -q -e "/workspace/src/tactile_core[dev]"
fi

exec "$@"
