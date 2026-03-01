"""Sensor platform for Roth Touchline integration."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import TouchlineDataUpdateCoordinator
from .const import DOMAIN

CONTROLLER_STATUS_DESCRIPTION = SensorEntityDescription(
    key="controller_status",
    name="System Status",
    entity_category=EntityCategory.DIAGNOSTIC,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Touchline sensor entities from a config entry."""
    coordinator: TouchlineDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([TouchlineControllerStatusSensor(coordinator)])


class TouchlineControllerStatusSensor(
    CoordinatorEntity[TouchlineDataUpdateCoordinator], SensorEntity
):
    """Sensor representing the Touchline controller system status."""

    entity_description = CONTROLLER_STATUS_DESCRIPTION

    def __init__(self, coordinator: TouchlineDataUpdateCoordinator) -> None:
        """Initialize the controller status sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_controller_status"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{coordinator.host}_controller")},
            manufacturer="Roth",
            model="Touchline Controller",
            name="Touchline Controller",
        )

    @property
    def native_value(self) -> str | None:
        """Return the system status."""
        return self.coordinator.controller_status
