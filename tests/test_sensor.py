"""Tests for the Roth Touchline sensor platform."""
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from zoneinfo import ZoneInfo

from custom_components.touchline.sensor import (
    TouchlineControllerStatusSensor,
    TouchlineControllerDateTimeSensor,
    TouchlineControllerErrorCodeSensor,
    TouchlineControllerHwIpSensor,
    TouchlineControllerHwMacSensor,
    TouchlineControllerHwHostnameSensor,
    TouchlineControllerFwStellAppSensor,
    TouchlineControllerFwStellBlSensor,
    TouchlineControllerFwStmAppSensor,
    TouchlineControllerFwStmBlSensor,
)


def _make_coordinator(
    controller_status="OK",
    controller_id=0,
    host="192.168.1.100",
    owner_kurz_id="12345",
    datetime_value="1709302958",
    error_code="0",
    hw_ip="192.168.1.100",
    hw_mac="AA:BB:CC:DD:EE:FF",
    hw_hostname="touchline",
    fw_stell_app="1.0.0",
    fw_stell_bl="1.0.0",
    fw_stm_app="2.0.0",
    fw_stm_bl="2.0.0",
):
    coordinator = MagicMock()
    coordinator.host = host
    coordinator.controller_status = controller_status
    coordinator.controller_id = controller_id
    coordinator.owner_kurz_id = owner_kurz_id
    coordinator.datetime = datetime_value
    coordinator.error_code = error_code
    coordinator.hw_ip = hw_ip
    coordinator.hw_mac = hw_mac
    coordinator.hw_hostname = hw_hostname
    coordinator.fw_stell_app = fw_stell_app
    coordinator.fw_stell_bl = fw_stell_bl
    coordinator.fw_stm_app = fw_stm_app
    coordinator.fw_stm_bl = fw_stm_bl
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
        """Test that native_value returns the controller datetime as formatted string in local timezone."""
        # Unix timestamp 1709302958 = 2024-03-01 14:22:38 UTC
        coordinator = _make_coordinator(datetime_value="1709302958")
        sensor = TouchlineControllerDateTimeSensor(coordinator)

        # Mock dt_util to use Europe/Paris timezone (UTC+1 in winter)
        with patch("custom_components.touchline.sensor.dt_util") as mock_dt_util:
            # Mock get_default_time_zone to return Europe/Paris
            mock_dt_util.get_default_time_zone.return_value = ZoneInfo("Europe/Paris")
            # Mock utc_from_timestamp to return the UTC datetime
            mock_dt_util.utc_from_timestamp.return_value = datetime.fromtimestamp(1709302958, tz=timezone.utc)

            result = sensor.native_value
            assert isinstance(result, str)
            # In Europe/Paris (UTC+1), the time should be 15:22:38
            assert result == "2024-03-01 15:22:38 CET"

    def test_native_value_none(self):
        """Test that native_value returns None when datetime is not available."""
        coordinator = _make_coordinator(datetime_value=None)
        sensor = TouchlineControllerDateTimeSensor(coordinator)
        assert sensor.native_value is None

    def test_native_value_invalid(self):
        """Test that native_value returns None for invalid timestamp."""
        coordinator = _make_coordinator(datetime_value="invalid")
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

    def test_device_class_removed(self):
        """Test that the sensor no longer uses TIMESTAMP device class."""
        coordinator = _make_coordinator()
        sensor = TouchlineControllerDateTimeSensor(coordinator)
        assert sensor.entity_description.device_class is None


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


class TestTouchlineControllerHwIpSensor:
    """Tests for the TouchlineControllerHwIpSensor entity."""

    def test_unique_id(self):
        """Test that unique_id is set based on host."""
        coordinator = _make_coordinator()
        sensor = TouchlineControllerHwIpSensor(coordinator)
        assert sensor.unique_id == "192.168.1.100_controller_hw_ip"

    def test_native_value(self):
        """Test that native_value returns the controller IP address."""
        coordinator = _make_coordinator(hw_ip="10.0.0.1")
        sensor = TouchlineControllerHwIpSensor(coordinator)
        assert sensor.native_value == "10.0.0.1"

    def test_native_value_none(self):
        """Test that native_value returns None when IP is not available."""
        coordinator = _make_coordinator(hw_ip=None)
        sensor = TouchlineControllerHwIpSensor(coordinator)
        assert sensor.native_value is None

    def test_device_info(self):
        """Test that device_info identifies the controller device."""
        coordinator = _make_coordinator()
        sensor = TouchlineControllerHwIpSensor(coordinator)
        assert sensor.device_info is not None
        assert ("touchline", "192.168.1.100_controller") in sensor.device_info["identifiers"]
        assert sensor.device_info["manufacturer"] == "Roth"
        assert sensor.device_info["model"] == "Touchline Controller"

    def test_entity_category_diagnostic(self):
        """Test that the sensor is categorized as diagnostic."""
        from homeassistant.helpers.entity import EntityCategory
        coordinator = _make_coordinator()
        sensor = TouchlineControllerHwIpSensor(coordinator)
        assert sensor.entity_description.entity_category == EntityCategory.DIAGNOSTIC


class TestTouchlineControllerHwMacSensor:
    """Tests for the TouchlineControllerHwMacSensor entity."""

    def test_unique_id(self):
        """Test that unique_id is set based on host."""
        coordinator = _make_coordinator()
        sensor = TouchlineControllerHwMacSensor(coordinator)
        assert sensor.unique_id == "192.168.1.100_controller_hw_mac"

    def test_native_value(self):
        """Test that native_value returns the controller MAC address."""
        coordinator = _make_coordinator(hw_mac="AA:BB:CC:DD:EE:FF")
        sensor = TouchlineControllerHwMacSensor(coordinator)
        assert sensor.native_value == "AA:BB:CC:DD:EE:FF"

    def test_native_value_none(self):
        """Test that native_value returns None when MAC is not available."""
        coordinator = _make_coordinator(hw_mac=None)
        sensor = TouchlineControllerHwMacSensor(coordinator)
        assert sensor.native_value is None

    def test_device_info(self):
        """Test that device_info identifies the controller device."""
        coordinator = _make_coordinator()
        sensor = TouchlineControllerHwMacSensor(coordinator)
        assert sensor.device_info is not None
        assert ("touchline", "192.168.1.100_controller") in sensor.device_info["identifiers"]
        assert sensor.device_info["manufacturer"] == "Roth"
        assert sensor.device_info["model"] == "Touchline Controller"

    def test_entity_category_diagnostic(self):
        """Test that the sensor is categorized as diagnostic."""
        from homeassistant.helpers.entity import EntityCategory
        coordinator = _make_coordinator()
        sensor = TouchlineControllerHwMacSensor(coordinator)
        assert sensor.entity_description.entity_category == EntityCategory.DIAGNOSTIC


class TestTouchlineControllerHwHostnameSensor:
    """Tests for the TouchlineControllerHwHostnameSensor entity."""

    def test_unique_id(self):
        """Test that unique_id is set based on host."""
        coordinator = _make_coordinator()
        sensor = TouchlineControllerHwHostnameSensor(coordinator)
        assert sensor.unique_id == "192.168.1.100_controller_hw_hostname"

    def test_native_value(self):
        """Test that native_value returns the controller hostname."""
        coordinator = _make_coordinator(hw_hostname="touchline-ctrl")
        sensor = TouchlineControllerHwHostnameSensor(coordinator)
        assert sensor.native_value == "touchline-ctrl"

    def test_native_value_none(self):
        """Test that native_value returns None when hostname is not available."""
        coordinator = _make_coordinator(hw_hostname=None)
        sensor = TouchlineControllerHwHostnameSensor(coordinator)
        assert sensor.native_value is None

    def test_device_info(self):
        """Test that device_info identifies the controller device."""
        coordinator = _make_coordinator()
        sensor = TouchlineControllerHwHostnameSensor(coordinator)
        assert sensor.device_info is not None
        assert ("touchline", "192.168.1.100_controller") in sensor.device_info["identifiers"]
        assert sensor.device_info["manufacturer"] == "Roth"
        assert sensor.device_info["model"] == "Touchline Controller"

    def test_entity_category_diagnostic(self):
        """Test that the sensor is categorized as diagnostic."""
        from homeassistant.helpers.entity import EntityCategory
        coordinator = _make_coordinator()
        sensor = TouchlineControllerHwHostnameSensor(coordinator)
        assert sensor.entity_description.entity_category == EntityCategory.DIAGNOSTIC


class TestTouchlineControllerFwStellAppSensor:
    """Tests for the TouchlineControllerFwStellAppSensor entity."""

    def test_unique_id(self):
        """Test that unique_id is set based on host."""
        coordinator = _make_coordinator()
        sensor = TouchlineControllerFwStellAppSensor(coordinator)
        assert sensor.unique_id == "192.168.1.100_controller_fw_stell_app"

    def test_native_value(self):
        """Test that native_value returns the actuator app firmware version."""
        coordinator = _make_coordinator(fw_stell_app="1.2.3")
        sensor = TouchlineControllerFwStellAppSensor(coordinator)
        assert sensor.native_value == "1.2.3"

    def test_native_value_none(self):
        """Test that native_value returns None when not available."""
        coordinator = _make_coordinator(fw_stell_app=None)
        sensor = TouchlineControllerFwStellAppSensor(coordinator)
        assert sensor.native_value is None

    def test_device_info(self):
        """Test that device_info identifies the controller device."""
        coordinator = _make_coordinator()
        sensor = TouchlineControllerFwStellAppSensor(coordinator)
        assert sensor.device_info is not None
        assert ("touchline", "192.168.1.100_controller") in sensor.device_info["identifiers"]
        assert sensor.device_info["manufacturer"] == "Roth"
        assert sensor.device_info["model"] == "Touchline Controller"

    def test_entity_category_diagnostic(self):
        """Test that the sensor is categorized as diagnostic."""
        from homeassistant.helpers.entity import EntityCategory
        coordinator = _make_coordinator()
        sensor = TouchlineControllerFwStellAppSensor(coordinator)
        assert sensor.entity_description.entity_category == EntityCategory.DIAGNOSTIC


class TestTouchlineControllerFwStellBlSensor:
    """Tests for the TouchlineControllerFwStellBlSensor entity."""

    def test_unique_id(self):
        """Test that unique_id is set based on host."""
        coordinator = _make_coordinator()
        sensor = TouchlineControllerFwStellBlSensor(coordinator)
        assert sensor.unique_id == "192.168.1.100_controller_fw_stell_bl"

    def test_native_value(self):
        """Test that native_value returns the actuator bootloader firmware version."""
        coordinator = _make_coordinator(fw_stell_bl="1.0.5")
        sensor = TouchlineControllerFwStellBlSensor(coordinator)
        assert sensor.native_value == "1.0.5"

    def test_native_value_none(self):
        """Test that native_value returns None when not available."""
        coordinator = _make_coordinator(fw_stell_bl=None)
        sensor = TouchlineControllerFwStellBlSensor(coordinator)
        assert sensor.native_value is None

    def test_device_info(self):
        """Test that device_info identifies the controller device."""
        coordinator = _make_coordinator()
        sensor = TouchlineControllerFwStellBlSensor(coordinator)
        assert sensor.device_info is not None
        assert ("touchline", "192.168.1.100_controller") in sensor.device_info["identifiers"]
        assert sensor.device_info["manufacturer"] == "Roth"
        assert sensor.device_info["model"] == "Touchline Controller"

    def test_entity_category_diagnostic(self):
        """Test that the sensor is categorized as diagnostic."""
        from homeassistant.helpers.entity import EntityCategory
        coordinator = _make_coordinator()
        sensor = TouchlineControllerFwStellBlSensor(coordinator)
        assert sensor.entity_description.entity_category == EntityCategory.DIAGNOSTIC


class TestTouchlineControllerFwStmAppSensor:
    """Tests for the TouchlineControllerFwStmAppSensor entity."""

    def test_unique_id(self):
        """Test that unique_id is set based on host."""
        coordinator = _make_coordinator()
        sensor = TouchlineControllerFwStmAppSensor(coordinator)
        assert sensor.unique_id == "192.168.1.100_controller_fw_stm_app"

    def test_native_value(self):
        """Test that native_value returns the STM app firmware version."""
        coordinator = _make_coordinator(fw_stm_app="2.1.0")
        sensor = TouchlineControllerFwStmAppSensor(coordinator)
        assert sensor.native_value == "2.1.0"

    def test_native_value_none(self):
        """Test that native_value returns None when not available."""
        coordinator = _make_coordinator(fw_stm_app=None)
        sensor = TouchlineControllerFwStmAppSensor(coordinator)
        assert sensor.native_value is None

    def test_device_info(self):
        """Test that device_info identifies the controller device."""
        coordinator = _make_coordinator()
        sensor = TouchlineControllerFwStmAppSensor(coordinator)
        assert sensor.device_info is not None
        assert ("touchline", "192.168.1.100_controller") in sensor.device_info["identifiers"]
        assert sensor.device_info["manufacturer"] == "Roth"
        assert sensor.device_info["model"] == "Touchline Controller"

    def test_entity_category_diagnostic(self):
        """Test that the sensor is categorized as diagnostic."""
        from homeassistant.helpers.entity import EntityCategory
        coordinator = _make_coordinator()
        sensor = TouchlineControllerFwStmAppSensor(coordinator)
        assert sensor.entity_description.entity_category == EntityCategory.DIAGNOSTIC


class TestTouchlineControllerFwStmBlSensor:
    """Tests for the TouchlineControllerFwStmBlSensor entity."""

    def test_unique_id(self):
        """Test that unique_id is set based on host."""
        coordinator = _make_coordinator()
        sensor = TouchlineControllerFwStmBlSensor(coordinator)
        assert sensor.unique_id == "192.168.1.100_controller_fw_stm_bl"

    def test_native_value(self):
        """Test that native_value returns the STM bootloader firmware version."""
        coordinator = _make_coordinator(fw_stm_bl="2.0.1")
        sensor = TouchlineControllerFwStmBlSensor(coordinator)
        assert sensor.native_value == "2.0.1"

    def test_native_value_none(self):
        """Test that native_value returns None when not available."""
        coordinator = _make_coordinator(fw_stm_bl=None)
        sensor = TouchlineControllerFwStmBlSensor(coordinator)
        assert sensor.native_value is None

    def test_device_info(self):
        """Test that device_info identifies the controller device."""
        coordinator = _make_coordinator()
        sensor = TouchlineControllerFwStmBlSensor(coordinator)
        assert sensor.device_info is not None
        assert ("touchline", "192.168.1.100_controller") in sensor.device_info["identifiers"]
        assert sensor.device_info["manufacturer"] == "Roth"
        assert sensor.device_info["model"] == "Touchline Controller"

    def test_entity_category_diagnostic(self):
        """Test that the sensor is categorized as diagnostic."""
        from homeassistant.helpers.entity import EntityCategory
        coordinator = _make_coordinator()
        sensor = TouchlineControllerFwStmBlSensor(coordinator)
        assert sensor.entity_description.entity_category == EntityCategory.DIAGNOSTIC
