"""Tests for the Roth Touchline sensor platform."""
from unittest.mock import MagicMock

from custom_components.touchline.sensor import (
    TouchlineControllerStatusSensor,
    TouchlineControllerDateTimeSensor,
    TouchlineControllerErrorCodeSensor,
)


def _make_coordinator(
    controller_status="OK",
    controller_id=0,
    host="192.168.1.100",
    owner_kurz_id="12345",
    datetime="2026-03-01 14:42:38",
    error_code="0",
):
    coordinator = MagicMock()
    coordinator.host = host
    coordinator.controller_status = controller_status
    coordinator.controller_id = controller_id
    coordinator.owner_kurz_id = owner_kurz_id
    coordinator.datetime = datetime
    coordinator.error_code = error_code
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

    def test_device_info_with_owner_kurz_id(self):
        """Test that device_info includes ownerKurzID as serial_number."""
        coordinator = _make_coordinator(owner_kurz_id="12345")
        sensor = TouchlineControllerStatusSensor(coordinator)
        # Access native_value to trigger _update_device_info
        _ = sensor.native_value
        assert sensor.device_info is not None
        assert sensor.device_info.get("serial_number") == "12345"

    def test_entity_category_diagnostic(self):
        """Test that the sensor is categorized as diagnostic."""
        from homeassistant.helpers.entity import EntityCategory
        coordinator = _make_coordinator()
        sensor = TouchlineControllerStatusSensor(coordinator)
        assert sensor.entity_description.entity_category == EntityCategory.DIAGNOSTIC


class TestTouchlineControllerDateTimeSensor:
    """Tests for the TouchlineControllerDateTimeSensor entity."""

    def test_unique_id(self):
        """Test that unique_id is set based on host."""
        coordinator = _make_coordinator()
        sensor = TouchlineControllerDateTimeSensor(coordinator)
        assert sensor.unique_id == "192.168.1.100_controller_datetime"

    def test_native_value(self):
        """Test that native_value returns the controller datetime."""
        coordinator = _make_coordinator(datetime="2026-03-01 14:42:38")
        sensor = TouchlineControllerDateTimeSensor(coordinator)
        assert sensor.native_value == "2026-03-01 14:42:38"

    def test_native_value_none(self):
        """Test that native_value returns None when datetime is not available."""
        coordinator = _make_coordinator(datetime=None)
        sensor = TouchlineControllerDateTimeSensor(coordinator)
        assert sensor.native_value is None

    def test_device_info(self):
        """Test that device_info identifies the controller device."""
        coordinator = _make_coordinator()
        sensor = TouchlineControllerDateTimeSensor(coordinator)
        assert sensor.device_info is not None
        assert ("touchline", "192.168.1.100_controller") in sensor.device_info["identifiers"]
        assert sensor.device_info["manufacturer"] == "Roth"
        assert sensor.device_info["model"] == "Touchline Controller"

    def test_entity_category_diagnostic(self):
        """Test that the sensor is categorized as diagnostic."""
        from homeassistant.helpers.entity import EntityCategory
        coordinator = _make_coordinator()
        sensor = TouchlineControllerDateTimeSensor(coordinator)
        assert sensor.entity_description.entity_category == EntityCategory.DIAGNOSTIC


class TestTouchlineControllerErrorCodeSensor:
    """Tests for the TouchlineControllerErrorCodeSensor entity."""

    def test_unique_id(self):
        """Test that unique_id is set based on host."""
        coordinator = _make_coordinator()
        sensor = TouchlineControllerErrorCodeSensor(coordinator)
        assert sensor.unique_id == "192.168.1.100_controller_error_code"

    def test_native_value(self):
        """Test that native_value returns the controller error code."""
        coordinator = _make_coordinator(error_code="0")
        sensor = TouchlineControllerErrorCodeSensor(coordinator)
        assert sensor.native_value == "0"

    def test_native_value_none(self):
        """Test that native_value returns None when error code is not available."""
        coordinator = _make_coordinator(error_code=None)
        sensor = TouchlineControllerErrorCodeSensor(coordinator)
        assert sensor.native_value is None

    def test_device_info(self):
        """Test that device_info identifies the controller device."""
        coordinator = _make_coordinator()
        sensor = TouchlineControllerErrorCodeSensor(coordinator)
        assert sensor.device_info is not None
        assert ("touchline", "192.168.1.100_controller") in sensor.device_info["identifiers"]
        assert sensor.device_info["manufacturer"] == "Roth"
        assert sensor.device_info["model"] == "Touchline Controller"

    def test_entity_category_diagnostic(self):
        """Test that the sensor is categorized as diagnostic."""
        from homeassistant.helpers.entity import EntityCategory
        coordinator = _make_coordinator()
        sensor = TouchlineControllerErrorCodeSensor(coordinator)
        assert sensor.entity_description.entity_category == EntityCategory.DIAGNOSTIC
