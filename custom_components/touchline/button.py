"""Button platform for Roth Touchline integration."""
from __future__ import annotations

from datetime import datetime
import logging

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import TouchlineDataUpdateCoordinator
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SYNC_TIME_BUTTON_DESCRIPTION = ButtonEntityDescription(
    key="sync_time",
    name="Sync Time",
    entity_category=EntityCategory.CONFIG,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Touchline button entities from a config entry."""
    coordinator: TouchlineDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        TouchlineSyncTimeButton(coordinator),
    ])


class TouchlineSyncTimeButton(
    CoordinatorEntity[TouchlineDataUpdateCoordinator], ButtonEntity
):
    """Button to sync time with the Touchline controller."""

    entity_description = SYNC_TIME_BUTTON_DESCRIPTION

    def __init__(self, coordinator: TouchlineDataUpdateCoordinator) -> None:
        """Initialize the sync time button."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_sync_time"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{coordinator.host}_controller")},
            manufacturer="Roth",
            model="Touchline Controller",
            name="Touchline Controller",
        )

    async def async_press(self) -> None:
        """Handle the button press to sync time."""
        # Get current system time in a format the controller expects
        # The format will depend on what the controller expects
        current_time = datetime.now()

        # Format as timestamp or specific format expected by controller
        # This may need adjustment based on controller requirements
        datetime_value = int(current_time.timestamp())

        _LOGGER.info(f"Syncing time to controller: {current_time}")

        # Use the first device to set the time (R0 is system-level)
        if self.coordinator.devices:
            device = self.coordinator.devices[0]
            success = await self.hass.async_add_executor_job(
                device.set_datetime, datetime_value
            )

            if success:
                _LOGGER.info("Time synced successfully")
                # Request coordinator refresh to update the datetime sensor
                await self.coordinator.async_request_refresh()
            else:
                _LOGGER.error("Failed to sync time")
        else:
            _LOGGER.error("No devices available to sync time")
