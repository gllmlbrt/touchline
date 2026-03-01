"""Sensor platform for Roth Touchline integration."""
from __future__ import annotations

from datetime import datetime, timezone

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
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

CONTROLLER_DATETIME_DESCRIPTION = SensorEntityDescription(
    key="controller_datetime",
    name="Controller DateTime",
    device_class=SensorDeviceClass.TIMESTAMP,
    entity_category=EntityCategory.DIAGNOSTIC,
)

CONTROLLER_ERROR_CODE_DESCRIPTION = SensorEntityDescription(
    key="controller_error_code",
    name="Controller Error Code",
    entity_category=EntityCategory.DIAGNOSTIC,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Touchline sensor entities from a config entry."""
    coordinator: TouchlineDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([
        TouchlineControllerStatusSensor(coordinator),
        TouchlineControllerDateTimeSensor(coordinator),
        TouchlineControllerErrorCodeSensor(coordinator),
    ])


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

    def _update_device_info(self) -> None:
        """Update device info with ownerKurzID once available."""
        if self.coordinator.owner_kurz_id and self._attr_device_info:
            self._attr_device_info["serial_number"] = self.coordinator.owner_kurz_id

    @property
    def native_value(self) -> str | None:
        """Return the system status."""
        self._update_device_info()
        return self.coordinator.controller_status


class TouchlineControllerDateTimeSensor(
    CoordinatorEntity[TouchlineDataUpdateCoordinator], SensorEntity
):
    """Sensor representing the Touchline controller datetime."""

    entity_description = CONTROLLER_DATETIME_DESCRIPTION

    def __init__(self, coordinator: TouchlineDataUpdateCoordinator) -> None:
        """Initialize the controller datetime sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_controller_datetime"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{coordinator.host}_controller")},
            manufacturer="Roth",
            model="Touchline Controller",
            name="Touchline Controller",
        )

    @property
    def native_value(self) -> datetime | None:
        """Return the controller datetime as a datetime object."""
        if self.coordinator.datetime is None:
            return None

        try:
            # Controller returns Unix timestamp as a string
            timestamp = int(self.coordinator.datetime)
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        except (ValueError, TypeError):
            # If parsing fails, return None
            return None


class TouchlineControllerErrorCodeSensor(
    CoordinatorEntity[TouchlineDataUpdateCoordinator], SensorEntity
):
    """Sensor representing the Touchline controller error code."""

    entity_description = CONTROLLER_ERROR_CODE_DESCRIPTION

    def __init__(self, coordinator: TouchlineDataUpdateCoordinator) -> None:
        """Initialize the controller error code sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{coordinator.host}_controller_error_code"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{coordinator.host}_controller")},
            manufacturer="Roth",
            model="Touchline Controller",
            name="Touchline Controller",
        )

    @property
    def native_value(self) -> str | None:
        """Return the controller error code."""
        return self.coordinator.error_code
