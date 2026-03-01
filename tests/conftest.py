"""Shared fixtures for Roth Touchline tests."""
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def mock_pytouchline_device():
    """Return a mock PyTouchline device."""
    device = MagicMock()
    device.get_name.return_value = "Living Room"
    device.get_current_temperature.return_value = 21.5
    device.get_target_temperature.return_value = 22.0
    device.get_target_temperature_high.return_value = 25.0
    device.get_target_temperature_low.return_value = 18.0
    device.get_operation_mode.return_value = 0  # AUTO
    device.get_week_program.return_value = 0
    device.get_device_id.return_value = 1
    device.get_controller_id.return_value = 0
    return device


@pytest.fixture
def mock_pytouchline(mock_pytouchline_device):
    """Patch PyTouchline so no real network calls are made."""
    with patch(
        "custom_components.touchline.config_flow.PyTouchline"
    ) as mock_cls, patch(
        "custom_components.touchline.PyTouchline"
    ) as mock_cls2:
        instance = MagicMock()
        instance.get_number_of_devices.return_value = "2"
        mock_cls.return_value = instance
        mock_cls2.return_value = instance
        yield instance, mock_pytouchline_device
