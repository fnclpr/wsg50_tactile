# Tactile sensor / WSG50 development container.
#
# This is a DEVELOPMENT image: it does not COPY the source tree in.
# docker-compose.yml bind-mounts the host's tactile_ws/ into /workspace
# at runtime, so edits made on the host are immediately visible inside
# the container without rebuilding the image. Only rebuild this image
# when you change SYSTEM/PYTHON DEPENDENCIES (this file or
# requirements.txt), not when you change your own code.

FROM ros:jazzy-ros-base

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

# --- System packages ---------------------------------------------------
# build-essential/git/cmake: building C++ ROS2 packages later (Steps 4/5/12)
# ros-dev-tools + python3-colcon-common-extensions: colcon build for ROS2 pkgs
# python3-vcstool: `vcs import` for external deps listed in tactile_ws.repos (Step 4+)
# setserial: required by read_tactile_serial_node.cpp's low-latency setup
# usbutils: `lsusb` for debugging device enumeration
# libgl1/libegl1/libxkbcommon0/libdbus-1-3/libxcb*: PySide6/Qt runtime libs
#   under X11 forwarding (headless Qt still needs these to *load*)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    python3-pip \
    python3-dev \
    ros-dev-tools \
    python3-colcon-common-extensions \
    python3-vcstool \
    setserial \
    usbutils \
    udev \
    libgl1 \
    libegl1 \
    libxkbcommon0 \
    libdbus-1-3 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xinerama0 \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# --- Python dependencies -------------------------------------------------
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --break-system-packages -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

# --- Workspace -------------------------------------------------------
WORKDIR /workspace

# Non-root user matching the host UID/GID would go here in a later,
# hardened iteration; kept as root for now to avoid permission friction
# during early development (ENGINEERING DECISION -- revisit before any
# shared/production use).

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
