"""
tactile_core
============

Hardware-independent, ROS-independent core math library for the
Vanvitelli force/tactile sensor.

Every function in `tactile_core.processing` is a direct, documented port
of a specific MATLAB function from `matlab_calibration_gui/gui_lib/`.
See each module's docstring for the exact source file and equation
number in Costanzo et al., "Design and Calibration of a Force/Tactile
Sensor for Dexterous Manipulation", Sensors 2019, 19, 966.

This package intentionally has zero ROS2 and zero hardware dependency,
so it can be developed and unit-tested before any hardware or Docker
setup exists (Step 1 of the project roadmap).
"""

__version__ = "0.1.0"
