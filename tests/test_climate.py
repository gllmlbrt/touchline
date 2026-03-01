"""Tests for the Roth Touchline climate platform."""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from homeassistant.components.climate import HVACMode

from custom_components.touchline.climate import (
    PRESET_MODES,
    TOUCHLINE_TO_HA_PRESET,
    TouchlineClimate,
)
from custom_components.touchline.const import (
    OPERATION_MODE_AUTO,
    OPERATION_MODE_HOLIDAY,
    OPERATION_MODE_MANUAL,
)


def _make_device(
    op_mode=0, week_program=0, current_temp=21.5, target_temp=22.0, name="Zone 1",
    device_id=42, controller_id=0,
):
    device = MagicMock()
    device.get_name.return_value = name
    device.get_current_temperature.return_value = current_temp
    device.get_target_temperature.return_value = target_temp
    device.get_target_temperature_high.return_value = 25.0
    device.get_target_temperature_low.return_value = 18.0
    device.get_operation_mode.return_value = op_mode
    device.get_week_program.return_value = week_program
    device.get_device_id.return_value = device_id
    device.get_controller_id.return_value = controller_id
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


class TestPresetModeMappings:
    """Verify preset mode mapping tables are consistent."""

    def test_preset_modes_count(self):
        """Test that all 6 preset modes are defined."""
        assert len(PRESET_MODES) == 6
        assert "Normal" in PRESET_MODES
        assert "Night" in PRESET_MODES
        assert "Holiday" in PRESET_MODES
        assert "Pro 1" in PRESET_MODES
        assert "Pro 2" in PRESET_MODES
        assert "Pro 3" in PRESET_MODES

    def test_touchline_to_ha_preset_mapping(self):
        """Test that all presets can be mapped back from Touchline values."""
        for preset_name, preset_settings in PRESET_MODES.items():
            key = (preset_settings.mode, preset_settings.program)
            assert key in TOUCHLINE_TO_HA_PRESET
            assert TOUCHLINE_TO_HA_PRESET[key] == preset_name

    def test_preset_mode_constants(self):
        """Test that preset modes use correct operation mode constants."""
        assert PRESET_MODES["Normal"].mode == OPERATION_MODE_AUTO
        assert PRESET_MODES["Normal"].program == 0
        assert PRESET_MODES["Night"].mode == OPERATION_MODE_MANUAL
        assert PRESET_MODES["Night"].program == 0
        assert PRESET_MODES["Holiday"].mode == OPERATION_MODE_HOLIDAY
        assert PRESET_MODES["Holiday"].program == 0
        assert PRESET_MODES["Pro 1"].mode == OPERATION_MODE_AUTO
        assert PRESET_MODES["Pro 1"].program == 1
        assert PRESET_MODES["Pro 2"].mode == OPERATION_MODE_AUTO
        assert PRESET_MODES["Pro 2"].program == 2
        assert PRESET_MODES["Pro 3"].mode == OPERATION_MODE_AUTO
        assert PRESET_MODES["Pro 3"].program == 3


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

    def test_hvac_mode_always_heat(self):
        """Test that HVAC mode is always HEAT."""
        dev = _make_device(op_mode=OPERATION_MODE_AUTO)
        entity = _make_entity(_make_coordinator([dev]))
        assert entity.hvac_mode == HVACMode.HEAT

    def test_hvac_modes_list(self):
        """Test that only HEAT mode is in the list of supported modes."""
        dev = _make_device()
        entity = _make_entity(_make_coordinator([dev]))
        assert entity.hvac_modes == [HVACMode.HEAT]

    def test_preset_mode_normal(self):
        """Test Normal preset (AUTO mode, program 0)."""
        dev = _make_device(op_mode=OPERATION_MODE_AUTO, week_program=0)
        entity = _make_entity(_make_coordinator([dev]))
        assert entity.preset_mode == "Normal"

    def test_preset_mode_night(self):
        """Test Night preset (MANUAL mode, program 0)."""
        dev = _make_device(op_mode=OPERATION_MODE_MANUAL, week_program=0)
        entity = _make_entity(_make_coordinator([dev]))
        assert entity.preset_mode == "Night"

    def test_preset_mode_holiday(self):
        """Test Holiday preset (HOLIDAY mode, program 0)."""
        dev = _make_device(op_mode=OPERATION_MODE_HOLIDAY, week_program=0)
        entity = _make_entity(_make_coordinator([dev]))
        assert entity.preset_mode == "Holiday"

    def test_preset_mode_pro1(self):
        """Test Pro 1 preset (AUTO mode, program 1)."""
        dev = _make_device(op_mode=OPERATION_MODE_AUTO, week_program=1)
        entity = _make_entity(_make_coordinator([dev]))
        assert entity.preset_mode == "Pro 1"

    def test_preset_mode_pro2(self):
        """Test Pro 2 preset (AUTO mode, program 2)."""
        dev = _make_device(op_mode=OPERATION_MODE_AUTO, week_program=2)
        entity = _make_entity(_make_coordinator([dev]))
        assert entity.preset_mode == "Pro 2"

    def test_preset_mode_pro3(self):
        """Test Pro 3 preset (AUTO mode, program 3)."""
        dev = _make_device(op_mode=OPERATION_MODE_AUTO, week_program=3)
        entity = _make_entity(_make_coordinator([dev]))
        assert entity.preset_mode == "Pro 3"

    def test_preset_mode_unknown_defaults_to_normal(self):
        """Test unknown preset combination defaults to Normal."""
        dev = _make_device(op_mode=99, week_program=99)
        entity = _make_entity(_make_coordinator([dev]))
        assert entity.preset_mode == "Normal"

    def test_preset_mode_none_defaults_to_normal(self):
        """Test None values default to Normal preset."""
        dev = _make_device()
        dev.get_operation_mode.return_value = None
        dev.get_week_program.return_value = None
        entity = _make_entity(_make_coordinator([dev]))
        assert entity.preset_mode == "Normal"

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

    def test_device_info_serial_number(self):
        """Test that device info includes the hardware device ID as serial_number."""
        dev = _make_device(device_id=99)
        entity = _make_entity(_make_coordinator([dev]))
        assert entity.device_info is not None
        assert entity.device_info.get("serial_number") == "99"

    def test_device_info_serial_number_none(self):
        """Test that device info serial_number is None when device_id is None."""
        dev = _make_device()
        dev.get_device_id.return_value = None
        entity = _make_entity(_make_coordinator([dev]))
        assert entity.device_info is not None
        assert entity.device_info.get("serial_number") is None

    def test_device_info_via_device(self):
        """Test that device info links to the controller via via_device."""
        dev = _make_device()
        entity = _make_entity(_make_coordinator([dev]))
        assert entity.device_info is not None
        assert entity.device_info.get("via_device") == ("touchline", "192.168.1.100_controller")


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
        """Test setting HVAC mode to HEAT (should be no-op)."""
        dev = _make_device()
        coordinator = _make_coordinator([dev])
        entity = _make_entity(coordinator)

        await entity.async_set_hvac_mode(HVACMode.HEAT)

        # Should not call any device methods since HEAT is the only mode
        entity.hass.async_add_executor_job.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_set_preset_mode_normal(self):
        """Test setting preset to Normal."""
        dev = _make_device()
        coordinator = _make_coordinator([dev])
        entity = _make_entity(coordinator)

        await entity.async_set_preset_mode("Normal")

        # Should set mode to AUTO (0) and program to 0
        calls = entity.hass.async_add_executor_job.await_args_list
        assert len(calls) == 2
        assert calls[0][0][0] == dev.set_operation_mode
        assert calls[0][0][1] == OPERATION_MODE_AUTO
        assert calls[1][0][0] == dev.set_week_program
        assert calls[1][0][1] == 0
        coordinator.async_request_refresh.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_set_preset_mode_night(self):
        """Test setting preset to Night."""
        dev = _make_device()
        coordinator = _make_coordinator([dev])
        entity = _make_entity(coordinator)

        await entity.async_set_preset_mode("Night")

        # Should set mode to MANUAL (1) and program to 0
        calls = entity.hass.async_add_executor_job.await_args_list
        assert len(calls) == 2
        assert calls[0][0][0] == dev.set_operation_mode
        assert calls[0][0][1] == OPERATION_MODE_MANUAL
        assert calls[1][0][0] == dev.set_week_program
        assert calls[1][0][1] == 0

    @pytest.mark.asyncio
    async def test_set_preset_mode_holiday(self):
        """Test setting preset to Holiday."""
        dev = _make_device()
        coordinator = _make_coordinator([dev])
        entity = _make_entity(coordinator)

        await entity.async_set_preset_mode("Holiday")

        # Should set mode to HOLIDAY (2) and program to 0
        calls = entity.hass.async_add_executor_job.await_args_list
        assert len(calls) == 2
        assert calls[0][0][0] == dev.set_operation_mode
        assert calls[0][0][1] == OPERATION_MODE_HOLIDAY
        assert calls[1][0][0] == dev.set_week_program
        assert calls[1][0][1] == 0

    @pytest.mark.asyncio
    async def test_set_preset_mode_pro1(self):
        """Test setting preset to Pro 1."""
        dev = _make_device()
        coordinator = _make_coordinator([dev])
        entity = _make_entity(coordinator)

        await entity.async_set_preset_mode("Pro 1")

        # Should set mode to AUTO (0) and program to 1
        calls = entity.hass.async_add_executor_job.await_args_list
        assert len(calls) == 2
        assert calls[0][0][0] == dev.set_operation_mode
        assert calls[0][0][1] == OPERATION_MODE_AUTO
        assert calls[1][0][0] == dev.set_week_program
        assert calls[1][0][1] == 1

    @pytest.mark.asyncio
    async def test_set_preset_mode_pro2(self):
        """Test setting preset to Pro 2."""
        dev = _make_device()
        coordinator = _make_coordinator([dev])
        entity = _make_entity(coordinator)

        await entity.async_set_preset_mode("Pro 2")

        # Should set mode to AUTO (0) and program to 2
        calls = entity.hass.async_add_executor_job.await_args_list
        assert len(calls) == 2
        assert calls[1][0][1] == 2

    @pytest.mark.asyncio
    async def test_set_preset_mode_pro3(self):
        """Test setting preset to Pro 3."""
        dev = _make_device()
        coordinator = _make_coordinator([dev])
        entity = _make_entity(coordinator)

        await entity.async_set_preset_mode("Pro 3")

        # Should set mode to AUTO (0) and program to 3
        calls = entity.hass.async_add_executor_job.await_args_list
        assert len(calls) == 2
        assert calls[1][0][1] == 3

    @pytest.mark.asyncio
    async def test_set_preset_mode_invalid(self):
        """Test setting invalid preset raises error."""
        dev = _make_device()
        coordinator = _make_coordinator([dev])
        entity = _make_entity(coordinator)

        with pytest.raises(ValueError):
            await entity.async_set_preset_mode("InvalidPreset")
