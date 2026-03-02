"""Constants for the Roth Touchline integration."""

DOMAIN = "touchline"

CONF_HOST = "host"
CONF_VIRTUAL_HEAT_MODE = "virtual_heat_mode"

# Operation modes from pyTouchline
OPERATION_MODE_AUTO = 0
OPERATION_MODE_MANUAL = 1
OPERATION_MODE_HOLIDAY = 2
OPERATION_MODE_FROST = 3

# Virtual heat mode thresholds
HEAT_MODE_THRESHOLD = 0.1  # Temperature difference threshold in °C
HEAT_MODE_DELAY = 300  # Delay in seconds (5 minutes) before switching to idle
