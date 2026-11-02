#!/usr/bin/env python3
"""
Fake tactile sensor hardware emulator.

Creates a pseudo-terminal (PTY) pair and, on the "device" side, speaks
exactly the protocol read_tactile_serial_node.cpp expects:

  - wait for a single request byte ('a', 0x61)
  - respond with `rows*cols*2` bytes: for each taxel i, two bytes
    (lo, hi) such that the node's conversion formula

        voltage[i] = (lo[i] + (hi[i] & 0b00001111) * 256) * 3.3 / 4096.0

    reproduces a KNOWN, predictable raw ADC value per taxel, so a test
    subscriber can assert exact expected voltages.

Print the PTY device path on startup -- that path is what you pass as
the `serial_port` parameter to `read_tactile_serial`.

This does not require the real sensor, the `serial` C++ library to be
built, or any hardware at all. It exists purely to let us validate the
ROS2 node's behavior (parameter handling, byte-to-voltage conversion,
message publishing) in isolation before ever touching real hardware.

Usage:
    python3 tools/fake_tactile_sensor.py [--rows 5] [--cols 5]

Then, in another terminal (same container):
    ros2 run uclv_tactile_driver read_tactile_serial --ros-args \\
        -p serial_port:=<PTY_PATH_PRINTED_ABOVE> \\
        -p baud_rate:=115200 \\
        -p rows:=5 -p cols:=5

Baud rate note: PTYs don't enforce real UART timing, but some serial
libraries still validate the requested speed via termios. 115200 is
used here (rather than the hardware default of 500000/1000000) because
it's a "boring", universally-supported standard rate less likely to
trip up termios on a pseudo-terminal. This has no effect on real
hardware, which always uses its own launch-file default.
"""
from __future__ import annotations

import argparse
import os
import pty
import sys
import tty


REQUEST_BYTE = b"a"  # matches CHAR_TO_SEND in read_tactile_serial_node.cpp


def raw12_to_bytes(raw: int) -> bytes:
    """Pack a 12-bit raw ADC value into (lo, hi) exactly as the real
    sensor firmware does, per the node's inverse formula:
        value = lo + (hi & 0x0F) * 256
    """
    raw = max(0, min(4095, int(raw)))
    lo = raw & 0xFF
    hi = (raw >> 8) & 0x0F
    return bytes([lo, hi])


def raw12_to_expected_voltage(raw: int) -> float:
    """Exactly mirrors the node's conversion formula, so tests can
    compute the expected published value directly from the same raw
    integers used to build the fake payload (no independent rounding)."""
    raw = max(0, min(4095, int(raw)))
    return raw * 3.3 / 4096.0


def build_payload(num_taxels: int) -> tuple[bytes, list[float]]:
    """Deterministic, distinct-per-taxel raw values: 0, 100, 200, ...
    capped at 4095, so every taxel gets a different expected voltage
    and a bug that mixes up taxel ordering is easy to catch.
    """
    raws = [min(i * 100, 4095) for i in range(num_taxels)]
    payload = b"".join(raw12_to_bytes(r) for r in raws)
    expected_voltages = [raw12_to_expected_voltage(r) for r in raws]
    return payload, expected_voltages


def write_all(fd: int, data: bytes) -> None:
    """os.write() is permitted to write fewer bytes than requested (this
    is standard POSIX behavior, not specific to PTYs) -- loop until the
    full buffer is sent."""
    sent = 0
    while sent < len(data):
        sent += os.write(fd, data[sent:])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--rows", type=int, default=5)
    parser.add_argument("--cols", type=int, default=5)
    args = parser.parse_args()

    num_taxels = args.rows * args.cols
    payload, expected_voltages = build_payload(num_taxels)

    master_fd, slave_fd = pty.openpty()
    slave_name = os.ttyname(slave_fd)

    # CRITICAL: pty.openpty() defaults to canonical mode + echo, i.e. it
    # behaves like an interactive terminal (line-buffered, control
    # characters interpreted, everything echoed back). Our binary ADC
    # payload is not text and must never be line-buffered or echoed --
    # put both ends into raw mode, exactly what `socat ...,raw,echo=0`
    # does for the same reason. Without this, reads on the client side
    # return short/garbled data (discovered empirically while building
    # this test harness).
    tty.setraw(master_fd)
    tty.setraw(slave_fd)

    print("=" * 70)
    print(f"FAKE TACTILE SENSOR — PTY device: {slave_name}")
    print(f"  rows={args.rows} cols={args.cols} ({num_taxels} taxels)")
    print("  Point read_tactile_serial's serial_port parameter at this path.")
    print("  Expected voltages (taxel index -> volts), for verify_tactile_stream.py:")
    print(" ", [round(v, 6) for v in expected_voltages])
    print("=" * 70)
    sys.stdout.flush()

    try:
        while True:
            # Block until the node sends its 1-byte request.
            chunk = os.read(master_fd, 1)
            if chunk == REQUEST_BYTE:
                write_all(master_fd, payload)
            elif chunk:
                # Unexpected byte -- still respond, so the node doesn't
                # hang forever during manual debugging, but flag it.
                print(f"WARNING: expected {REQUEST_BYTE!r}, got {chunk!r}", file=sys.stderr)
                write_all(master_fd, payload)
    except KeyboardInterrupt:
        print("\nFake sensor stopped.")
    finally:
        os.close(master_fd)
        os.close(slave_fd)


if __name__ == "__main__":
    main()
