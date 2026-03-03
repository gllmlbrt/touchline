"""Climate platform for Roth Touchline integration."""
from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Any, NamedTuple

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from . import TouchlineDataUpdateCoordinator, ExtendedPyTouchline
from .const import (
    CONF_VIRTUAL_HEAT_MODE,
    DOMAIN,
    HEAT_MODE_DELAY,
    HEAT_MODE_HEATING_THRESHOLD,
    HEAT_MODE_IDLE_THRESHOLD,
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

    virtual_heat_mode = entry.options.get(CONF_VIRTUAL_HEAT_MODE, False)

    async_add_entities(
        TouchlineClimate(coordinator, idx, virtual_heat_mode)
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
        virtual_heat_mode: bool,
    ) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator)
        self._idx = idx
        self._virtual_heat_mode = virtual_heat_mode
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
        # Track state for virtual heat mode
        self._last_heating_time: datetime | None = None
        self._is_heating = False

    @property
    def _device(self) -> ExtendedPyTouchline:
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
    def hvac_action(self) -> HVACAction | None:
        """Return the current HVAC action."""
        # If not in HEAT mode, return OFF
        if self.hvac_mode == HVACMode.OFF:
            return HVACAction.OFF

        # If virtual heat mode is not enabled, return None (no action reported)
        if not self._virtual_heat_mode:
            return None

        # Get current and target temperatures
        current_temp = self.current_temperature
        target_temp = self.target_temperature

        # If temperatures are unavailable, return None
        if current_temp is None or target_temp is None:
            return None

        # Calculate temperature difference
        temp_diff = target_temp - current_temp

        # Logic as per requirements:
        # - When temp drops 0.2°C below target -> immediately heating
        # - When temp rises 0.3°C above target -> after 5 min delay, idle

        if temp_diff >= HEAT_MODE_HEATING_THRESHOLD:
            # Temperature is below target (needs heating)
            self._is_heating = True
            self._last_heating_time = dt_util.utcnow()
            return HVACAction.HEATING
        elif temp_diff <= -HEAT_MODE_IDLE_THRESHOLD:
            # Temperature is above target
            # Check if we should transition to idle after delay
            if self._is_heating:
                # We were heating, check if delay has passed
                if self._last_heating_time is None:
                    self._last_heating_time = dt_util.utcnow()

                time_since_heating = dt_util.utcnow() - self._last_heating_time
                if time_since_heating.total_seconds() >= HEAT_MODE_DELAY:
                    # Delay passed, transition to idle
                    self._is_heating = False
                    return HVACAction.IDLE
                else:
                    # Still within delay period, remain heating
                    return HVACAction.HEATING
            else:
                # Already idle
                return HVACAction.IDLE
        else:
            # Within hysteresis band (between -0.3°C and +0.2°C)
            # Maintain current state
            if self._is_heating:
                return HVACAction.HEATING
            else:
                return HVACAction.IDLE

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
