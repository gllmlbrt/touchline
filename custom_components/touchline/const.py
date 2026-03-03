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
HEAT_MODE_HEATING_THRESHOLD = 0.2  # Temperature difference to trigger heating (°C below target)
HEAT_MODE_IDLE_THRESHOLD = 0.3  # Temperature difference to trigger idle (°C above target)
HEAT_MODE_DELAY = 300  # Delay in seconds (5 minutes) before switching to idle
