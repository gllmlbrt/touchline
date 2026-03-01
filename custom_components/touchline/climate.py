"""Climate platform for Roth Touchline integration."""
from __future__ import annotations

import logging
from typing import Any

from pytouchline import PyTouchline

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import TouchlineDataUpdateCoordinator
from .const import DOMAIN, OPERATION_MODE_AUTO, OPERATION_MODE_FROST, OPERATION_MODE_MANUAL

_LOGGER = logging.getLogger(__name__)

HVAC_MODES = [HVACMode.AUTO, HVACMode.HEAT, HVACMode.OFF]

HA_TO_TOUCHLINE_HVAC: dict[HVACMode, int] = {
    HVACMode.AUTO: OPERATION_MODE_AUTO,
    HVACMode.HEAT: OPERATION_MODE_MANUAL,
    HVACMode.OFF: OPERATION_MODE_FROST,
}

TOUCHLINE_TO_HA_HVAC: dict[int, HVACMode] = {
    v: k for k, v in HA_TO_TOUCHLINE_HVAC.items()
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Touchline climate entities from a config entry."""
    coordinator: TouchlineDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    await coordinator.async_refresh()

    async_add_entities(
        TouchlineClimate(coordinator, idx)
        for idx in range(len(coordinator.data))
    )


class TouchlineClimate(CoordinatorEntity[TouchlineDataUpdateCoordinator], ClimateEntity):
    """Representation of a Roth Touchline thermostat zone."""

    _attr_hvac_modes = HVAC_MODES
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE
    _attr_temperature_unit = UnitOfTemperature.CELSIUS

    def __init__(
        self,
        coordinator: TouchlineDataUpdateCoordinator,
        idx: int,
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._idx = idx
        self._attr_unique_id = f"{coordinator.host}_{idx}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{coordinator.host}_{idx}")},
            manufacturer="Roth",
            model="Touchline",
            name=self._device_name,
        )

    @property
    def _device(self) -> PyTouchline:
        """Return the underlying device object."""
        return self.coordinator.data[self._idx]

    @property
    def _device_name(self) -> str:
        """Return the zone name from the device."""
        name = self._device.get_name()
        return name if name else f"Zone {self._idx + 1}"

    @property
    def name(self) -> str:
        """Return the name of the thermostat."""
        return self._device_name

    @property
    def current_temperature(self) -> float | None:
        """Return the current temperature."""
        return self._device.get_current_temperature()

    @property
    def target_temperature(self) -> float | None:
        """Return the target temperature."""
        return self._device.get_target_temperature()

    @property
    def target_temperature_high(self) -> float | None:
        """Return the upper target temperature."""
        return self._device.get_target_temperature_high()

    @property
    def target_temperature_low(self) -> float | None:
        """Return the lower target temperature."""
        return self._device.get_target_temperature_low()

    @property
    def hvac_mode(self) -> HVACMode:
        """Return the current HVAC mode."""
        op_mode = self._device.get_operation_mode()
        if op_mode is None:
            return HVACMode.AUTO
        return TOUCHLINE_TO_HA_HVAC.get(op_mode, HVACMode.AUTO)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        op_mode = HA_TO_TOUCHLINE_HVAC[hvac_mode]
        await self.hass.async_add_executor_job(
            self._device.set_operation_mode, op_mode
        )
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        await self.hass.async_add_executor_job(
            self._device.set_target_temperature, temperature
        )
        await self.coordinator.async_request_refresh()
