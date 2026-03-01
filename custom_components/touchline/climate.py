"""Climate platform for Roth Touchline integration."""
from __future__ import annotations

import logging
from typing import Any, NamedTuple

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
from .const import (
    DOMAIN,
    OPERATION_MODE_AUTO,
    OPERATION_MODE_FROST,
    OPERATION_MODE_HOLIDAY,
    OPERATION_MODE_MANUAL,
)

_LOGGER = logging.getLogger(__name__)


class PresetMode(NamedTuple):
    """Settings for preset mode."""

    mode: int
    program: int


PRESET_MODES = {
    "Normal": PresetMode(mode=OPERATION_MODE_AUTO, program=0),
    "Night": PresetMode(mode=OPERATION_MODE_MANUAL, program=0),
    "Pro 1": PresetMode(mode=OPERATION_MODE_AUTO, program=1),
    "Pro 2": PresetMode(mode=OPERATION_MODE_AUTO, program=2),
    "Pro 3": PresetMode(mode=OPERATION_MODE_AUTO, program=3),
}

TOUCHLINE_TO_HA_PRESET: dict[tuple[int, int], str] = {
    (settings.mode, settings.program): preset
    for preset, settings in PRESET_MODES.items()
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

    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_preset_modes = list(PRESET_MODES.keys())
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
    )
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
        device_id = self._device.get_device_id()
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{coordinator.host}_{idx}")},
            manufacturer="Roth",
            model="Touchline",
            name=self._device_name,
            serial_number=str(device_id) if device_id is not None else None,
            via_device=(DOMAIN, f"{coordinator.host}_controller"),
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
        if op_mode == OPERATION_MODE_HOLIDAY:
            return HVACMode.OFF
        return HVACMode.HEAT

    @property
    def preset_mode(self) -> str | None:
        """Return the current preset mode."""
        op_mode = self._device.get_operation_mode()
        week_program = self._device.get_week_program()
        if op_mode is None or week_program is None:
            return "Normal"
        return TOUCHLINE_TO_HA_PRESET.get((op_mode, week_program), "Normal")

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set new HVAC mode."""
        if hvac_mode == HVACMode.OFF:
            # Set to Holiday mode to turn off
            await self.hass.async_add_executor_job(
                self._device.set_operation_mode, OPERATION_MODE_HOLIDAY
            )
        elif hvac_mode == HVACMode.HEAT:
            # Set to Normal preset (AUTO mode, program 0)
            await self.hass.async_add_executor_job(
                self._device.set_operation_mode, OPERATION_MODE_AUTO
            )
            await self.hass.async_add_executor_job(
                self._device.set_week_program, 0
            )
        await self.coordinator.async_request_refresh()

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        """Set new preset mode."""
        if preset_mode not in PRESET_MODES:
            raise ValueError(f"Invalid preset mode: {preset_mode}")
        preset = PRESET_MODES[preset_mode]
        await self.hass.async_add_executor_job(
            self._device.set_operation_mode, preset.mode
        )
        await self.hass.async_add_executor_job(
            self._device.set_week_program, preset.program
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
