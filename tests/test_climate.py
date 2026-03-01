"""Tests for the Roth Touchline climate platform."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from homeassistant.components.climate import HVACMode

from custom_components.touchline.climate import (
    HA_TO_TOUCHLINE_HVAC,
    TOUCHLINE_TO_HA_HVAC,
    TouchlineClimate,
)
from custom_components.touchline.const import (
    OPERATION_MODE_AUTO,
    OPERATION_MODE_FROST,
    OPERATION_MODE_MANUAL,
)


def _make_device(op_mode=0, current_temp=21.5, target_temp=22.0, name="Zone 1"):
    device = MagicMock()
    device.get_name.return_value = name
    device.get_current_temperature.return_value = current_temp
    device.get_target_temperature.return_value = target_temp
    device.get_target_temperature_high.return_value = 25.0
    device.get_target_temperature_low.return_value = 18.0
    device.get_operation_mode.return_value = op_mode
    return device


def _make_coordinator(devices):
    coordinator = MagicMock()
    coordinator.data = devices
    coordinator.host = "192.168.1.100"
    coordinator.async_request_refresh = AsyncMock()
    return coordinator


def _make_entity(coordinator, idx=0):
    entity = TouchlineClimate(coordinator, idx)
    entity.hass = MagicMock()
    entity.hass.async_add_executor_job = AsyncMock(return_value=None)
    return entity


class TestHvacModeMappings:
    """Verify HVAC mode mapping tables are consistent."""

    def test_ha_to_touchline_contains_all_modes(self):
        assert HVACMode.AUTO in HA_TO_TOUCHLINE_HVAC
        assert HVACMode.HEAT in HA_TO_TOUCHLINE_HVAC
        assert HVACMode.OFF in HA_TO_TOUCHLINE_HVAC

    def test_touchline_to_ha_is_inverse(self):
        for ha_mode, op in HA_TO_TOUCHLINE_HVAC.items():
            assert TOUCHLINE_TO_HA_HVAC[op] == ha_mode

    def test_operation_mode_constants(self):
        assert HA_TO_TOUCHLINE_HVAC[HVACMode.AUTO] == OPERATION_MODE_AUTO
        assert HA_TO_TOUCHLINE_HVAC[HVACMode.HEAT] == OPERATION_MODE_MANUAL
        assert HA_TO_TOUCHLINE_HVAC[HVACMode.OFF] == OPERATION_MODE_FROST


class TestTouchlineClimateProperties:
    """Test property accessors of TouchlineClimate."""

    def test_current_temperature(self):
        dev = _make_device(current_temp=19.0)
        entity = _make_entity(_make_coordinator([dev]))
        assert entity.current_temperature == 19.0

    def test_target_temperature(self):
        dev = _make_device(target_temp=23.5)
        entity = _make_entity(_make_coordinator([dev]))
        assert entity.target_temperature == 23.5

    def test_hvac_mode_auto(self):
        dev = _make_device(op_mode=OPERATION_MODE_AUTO)
        entity = _make_entity(_make_coordinator([dev]))
        assert entity.hvac_mode == HVACMode.AUTO

    def test_hvac_mode_heat(self):
        dev = _make_device(op_mode=OPERATION_MODE_MANUAL)
        entity = _make_entity(_make_coordinator([dev]))
        assert entity.hvac_mode == HVACMode.HEAT

    def test_hvac_mode_off(self):
        dev = _make_device(op_mode=OPERATION_MODE_FROST)
        entity = _make_entity(_make_coordinator([dev]))
        assert entity.hvac_mode == HVACMode.OFF

    def test_hvac_mode_unknown_defaults_to_auto(self):
        dev = _make_device(op_mode=99)
        entity = _make_entity(_make_coordinator([dev]))
        assert entity.hvac_mode == HVACMode.AUTO

    def test_hvac_mode_none_defaults_to_auto(self):
        dev = _make_device()
        dev.get_operation_mode.return_value = None
        entity = _make_entity(_make_coordinator([dev]))
        assert entity.hvac_mode == HVACMode.AUTO

    def test_name_from_device(self):
        dev = _make_device(name="Kitchen")
        entity = _make_entity(_make_coordinator([dev]))
        assert entity.name == "Kitchen"

    def test_name_fallback_when_none(self):
        dev = _make_device()
        dev.get_name.return_value = None
        entity = _make_entity(_make_coordinator([dev]))
        assert entity.name == "Zone 1"

    def test_unique_id(self):
        devices = [_make_device(), _make_device(), _make_device()]
        entity = _make_entity(_make_coordinator(devices), idx=2)
        assert entity.unique_id == "192.168.1.100_2"


class TestTouchlineClimateActions:
    """Test async actions on TouchlineClimate."""

    @pytest.mark.asyncio
    async def test_set_temperature(self):
        dev = _make_device()
        coordinator = _make_coordinator([dev])
        entity = _make_entity(coordinator)

        await entity.async_set_temperature(temperature=24.0)

        entity.hass.async_add_executor_job.assert_awaited_once_with(
            dev.set_target_temperature, 24.0
        )
        coordinator.async_request_refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_set_temperature_no_value(self):
        dev = _make_device()
        coordinator = _make_coordinator([dev])
        entity = _make_entity(coordinator)

        await entity.async_set_temperature()

        entity.hass.async_add_executor_job.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_set_hvac_mode_heat(self):
        dev = _make_device()
        coordinator = _make_coordinator([dev])
        entity = _make_entity(coordinator)

        await entity.async_set_hvac_mode(HVACMode.HEAT)

        entity.hass.async_add_executor_job.assert_awaited_once_with(
            dev.set_operation_mode, OPERATION_MODE_MANUAL
        )

    @pytest.mark.asyncio
    async def test_set_hvac_mode_off(self):
        dev = _make_device()
        coordinator = _make_coordinator([dev])
        entity = _make_entity(coordinator)

        await entity.async_set_hvac_mode(HVACMode.OFF)

        entity.hass.async_add_executor_job.assert_awaited_once_with(
            dev.set_operation_mode, OPERATION_MODE_FROST
        )
