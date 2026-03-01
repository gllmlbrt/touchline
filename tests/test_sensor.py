"""Tests for the Roth Touchline sensor platform."""
from unittest.mock import MagicMock

from custom_components.touchline.sensor import TouchlineControllerStatusSensor


def _make_coordinator(controller_status="OK", controller_id=0, host="192.168.1.100"):
    coordinator = MagicMock()
    coordinator.host = host
    coordinator.controller_status = controller_status
    coordinator.controller_id = controller_id
    coordinator.data = []
    return coordinator


class TestTouchlineControllerStatusSensor:
    """Tests for the TouchlineControllerStatusSensor entity."""

    def test_unique_id(self):
        """Test that unique_id is set based on host."""
        coordinator = _make_coordinator()
        sensor = TouchlineControllerStatusSensor(coordinator)
        assert sensor.unique_id == "192.168.1.100_controller_status"

    def test_native_value(self):
        """Test that native_value returns the controller_status."""
        coordinator = _make_coordinator(controller_status="Standby")
        sensor = TouchlineControllerStatusSensor(coordinator)
        assert sensor.native_value == "Standby"

    def test_native_value_none(self):
        """Test that native_value returns None when status is not available."""
        coordinator = _make_coordinator(controller_status=None)
        sensor = TouchlineControllerStatusSensor(coordinator)
        assert sensor.native_value is None

    def test_device_info(self):
        """Test that device_info identifies the controller device."""
        coordinator = _make_coordinator()
        sensor = TouchlineControllerStatusSensor(coordinator)
        assert sensor.device_info is not None
        assert ("touchline", "192.168.1.100_controller") in sensor.device_info["identifiers"]
        assert sensor.device_info["manufacturer"] == "Roth"
        assert sensor.device_info["model"] == "Touchline Controller"

    def test_entity_category_diagnostic(self):
        """Test that the sensor is categorized as diagnostic."""
        from homeassistant.helpers.entity import EntityCategory
        coordinator = _make_coordinator()
        sensor = TouchlineControllerStatusSensor(coordinator)
        assert sensor.entity_description.entity_category == EntityCategory.DIAGNOSTIC
