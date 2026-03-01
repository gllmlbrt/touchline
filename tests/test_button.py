"""Tests for the Roth Touchline button platform."""
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime

import pytest

from custom_components.touchline.button import TouchlineSyncTimeButton


def _make_coordinator(host="192.168.1.100"):
    coordinator = MagicMock()
    coordinator.host = host
    coordinator.data = []

    # Create mock device
    mock_device = MagicMock()
    mock_device.set_datetime = MagicMock(return_value=True)
    coordinator.devices = [mock_device]
    coordinator.async_request_refresh = AsyncMock()

    return coordinator


class TestTouchlineSyncTimeButton:
    """Tests for the TouchlineSyncTimeButton entity."""

    def test_unique_id(self):
        """Test that unique_id is set based on host."""
        coordinator = _make_coordinator()
        button = TouchlineSyncTimeButton(coordinator)
        assert button.unique_id == "192.168.1.100_sync_time"

    def test_device_info(self):
        """Test that device_info identifies the controller device."""
        coordinator = _make_coordinator()
        button = TouchlineSyncTimeButton(coordinator)
        assert button.device_info is not None
        assert ("touchline", "192.168.1.100_controller") in button.device_info["identifiers"]
        assert button.device_info["manufacturer"] == "Roth"
        assert button.device_info["model"] == "Touchline Controller"

    def test_entity_category_config(self):
        """Test that the button is categorized as config."""
        from homeassistant.helpers.entity import EntityCategory
        coordinator = _make_coordinator()
        button = TouchlineSyncTimeButton(coordinator)
        assert button.entity_description.entity_category == EntityCategory.CONFIG

    @pytest.mark.asyncio
    async def test_press_button_success(self):
        """Test pressing the sync time button successfully."""
        coordinator = _make_coordinator()
        button = TouchlineSyncTimeButton(coordinator)

        # Mock hass
        button.hass = MagicMock()
        button.hass.async_add_executor_job = AsyncMock(return_value=True)

        # Press the button
        await button.async_press()

        # Verify set_datetime was called
        button.hass.async_add_executor_job.assert_called_once()
        # Verify refresh was requested
        coordinator.async_request_refresh.assert_called_once()

    @pytest.mark.asyncio
    async def test_press_button_no_devices(self):
        """Test pressing the button when no devices are available."""
        coordinator = _make_coordinator()
        coordinator.devices = []
        button = TouchlineSyncTimeButton(coordinator)

        # Mock hass
        button.hass = MagicMock()
        button.hass.async_add_executor_job = AsyncMock()

        # Press the button
        await button.async_press()

        # Verify set_datetime was not called
        button.hass.async_add_executor_job.assert_not_called()
        # Verify refresh was not requested
        coordinator.async_request_refresh.assert_not_called()

    @pytest.mark.asyncio
    async def test_press_button_failure(self):
        """Test pressing the button when set_datetime fails."""
        coordinator = _make_coordinator()
        button = TouchlineSyncTimeButton(coordinator)

        # Mock hass to return False (failure)
        button.hass = MagicMock()
        button.hass.async_add_executor_job = AsyncMock(return_value=False)

        # Press the button
        await button.async_press()

        # Verify set_datetime was called
        button.hass.async_add_executor_job.assert_called_once()
        # Verify refresh was not requested when failed
        coordinator.async_request_refresh.assert_not_called()
