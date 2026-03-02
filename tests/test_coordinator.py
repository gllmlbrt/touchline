"""Tests for the Roth Touchline data update coordinator."""
from unittest.mock import MagicMock, patch

import pytest

from custom_components.touchline import TouchlineDataUpdateCoordinator


class TestTouchlineDataUpdateCoordinator:
    """Tests for coordinator _fetch_data behavior."""

    def _make_coordinator(self, host="192.168.1.100"):
        hass = MagicMock()
        coordinator = TouchlineDataUpdateCoordinator.__new__(TouchlineDataUpdateCoordinator)
        coordinator.hass = hass
        coordinator.host = host
        coordinator._url = f"http://{host}"
        coordinator.devices = []
        coordinator.controller_id = None
        coordinator.controller_status = None
        coordinator.owner_kurz_id = None
        coordinator.datetime = None
        coordinator.error_code = None
        coordinator.hw_ip = None
        coordinator.hw_mac = None
        coordinator.hw_hostname = None
        coordinator._hw_info_loaded = False
        return coordinator

    def test_fetch_data_sets_controller_id_and_status(self):
        """Test that _fetch_data populates controller_id and controller_status."""
        coordinator = self._make_coordinator()

        mock_device = MagicMock()
        mock_device.get_controller_id.return_value = 42
        mock_device.get_status.return_value = "Standby"
        mock_device.get_owner_kurz_id.return_value = 42
        mock_device.get_datetime.return_value = "2026-03-01 14:42:38"
        mock_device.get_error_code.return_value = "0"
        mock_device.get_network_info.return_value = {
            "hw.IP": "192.168.1.100",
            "hw.Addr": "AA:BB:CC:DD:EE:FF",
            "hw.HostName": "touchline",
        }
        coordinator.devices = [mock_device]

        with patch("custom_components.touchline.ExtendedPyTouchline"):
            coordinator._fetch_data()

        assert coordinator.controller_id == 42
        assert coordinator.controller_status == "Standby"
        assert coordinator.owner_kurz_id == "42"
        assert coordinator.datetime == "2026-03-01 14:42:38"
        assert coordinator.error_code == "0"
        assert coordinator.hw_ip == "192.168.1.100"
        assert coordinator.hw_mac == "AA:BB:CC:DD:EE:FF"
        assert coordinator.hw_hostname == "touchline"
        assert coordinator._hw_info_loaded is True

    def test_fetch_data_no_devices_skips_controller_info(self):
        """Test that _fetch_data with no devices leaves controller info unchanged."""
        coordinator = self._make_coordinator()
        coordinator.controller_id = None
        coordinator.controller_status = None
        coordinator.owner_kurz_id = None
        coordinator.datetime = None
        coordinator.error_code = None

        with patch("custom_components.touchline.ExtendedPyTouchline") as mock_cls:
            probe = MagicMock()
            probe.get_number_of_devices.return_value = "0"
            mock_cls.return_value = probe
            # _fetch_data will init devices list as empty
            result = coordinator._fetch_data()

        assert result == []
        assert coordinator.controller_id is None
        assert coordinator.controller_status is None
        assert coordinator.owner_kurz_id is None
        assert coordinator.datetime is None
        assert coordinator.error_code is None
        assert coordinator.hw_ip is None
        assert coordinator.hw_mac is None
        assert coordinator.hw_hostname is None