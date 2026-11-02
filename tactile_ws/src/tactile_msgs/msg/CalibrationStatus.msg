# Overall calibration status for one tactile sensor/finger.
# Published (latched/on-change) by the calibration pipeline, consumed
# by both the calibration GUI and the monitor GUI, and checked by the
# force controller before allowing force-control activation (Section
# 17 of the project plan -- control must never auto-activate on an
# uncalibrated or invalidated sensor).

string sensor_id

bool calibrated

# Path to the loaded/exported calibration file, empty string if none.
string calibration_file

builtin_interfaces/Time calibration_timestamp

# Validation metrics from the held-out test set (Section 25 of the
# project plan). NaN (not a fixed sentinel) if not yet computed --
# check `calibrated` and `status_text` first.
float64 rmse
float64 mae
float64 r2
float64 max_error

# Human-readable state machine value. One of:
#   "NOT_CALIBRATED", "BIAS_REQUIRED", "TRAINING", "VALIDATING",
#   "PASS", "FAIL"
# Kept as a plain string (not an enum) for Step 3 simplicity; revisit
# with a proper set of uint8 constants if/when a strict state machine
# is enforced in code (Section 31 of the project plan).
string status_text
