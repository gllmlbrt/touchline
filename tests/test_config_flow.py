"""Tests for the Roth Touchline config flow."""
from unittest.mock import MagicMock, patch

import pytest

from custom_components.touchline.config_flow import TouchlineConfigFlow
from custom_components.touchline.const import DOMAIN


@pytest.mark.asyncio
async def test_config_flow_user_step_success():
    """Test a successful config flow user step."""
    flow = TouchlineConfigFlow()
    flow.hass = MagicMock()
    flow.hass.async_add_executor_job = _sync_exec
    flow._abort_if_unique_id_configured = MagicMock()
    flow.async_set_unique_id = _async_noop
    flow.async_create_entry = lambda title, data: {"title": title, "data": data}

    with patch(
        "custom_components.touchline.config_flow.PyTouchline"
    ) as mock_cls:
        instance = MagicMock()
        instance.get_number_of_devices.return_value = "3"
        mock_cls.return_value = instance

        result = await flow.async_step_user({"host": "192.168.1.100"})

    assert result["title"] == "192.168.1.100"
    assert result["data"]["host"] == "192.168.1.100"


@pytest.mark.asyncio
async def test_config_flow_user_step_no_devices():
    """Test config flow when controller reports zero devices."""
    flow = TouchlineConfigFlow()
    flow.hass = MagicMock()
    flow.hass.async_add_executor_job = _sync_exec
    flow.async_show_form = lambda step_id, data_schema, errors: {
        "step_id": step_id,
        "errors": errors,
    }

    with patch(
        "custom_components.touchline.config_flow.PyTouchline"
    ) as mock_cls:
        instance = MagicMock()
        instance.get_number_of_devices.return_value = "0"
        mock_cls.return_value = instance

        result = await flow.async_step_user({"host": "192.168.1.100"})

    assert result["errors"]["base"] == "no_devices"


@pytest.mark.asyncio
async def test_config_flow_user_step_cannot_connect():
    """Test config flow when connection fails."""
    flow = TouchlineConfigFlow()
    flow.hass = MagicMock()
    flow.hass.async_add_executor_job = _sync_exec
    flow.async_show_form = lambda step_id, data_schema, errors: {
        "step_id": step_id,
        "errors": errors,
    }

    with patch(
        "custom_components.touchline.config_flow.PyTouchline"
    ) as mock_cls:
        instance = MagicMock()
        instance.get_number_of_devices.side_effect = Exception("Connection refused")
        mock_cls.return_value = instance

        result = await flow.async_step_user({"host": "192.168.1.100"})

    assert result["errors"]["base"] == "cannot_connect"


@pytest.mark.asyncio
async def test_config_flow_user_step_shows_form_without_input():
    """Test config flow shows form when called without user input."""
    flow = TouchlineConfigFlow()
    flow.hass = MagicMock()
    flow.async_show_form = lambda step_id, data_schema, errors: {
        "step_id": step_id,
        "errors": errors,
    }

    result = await flow.async_step_user(None)

    assert result["step_id"] == "user"
    assert result["errors"] == {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def _sync_exec(func, *args):
    """Execute a sync callable as if it were run in an executor."""
    return func(*args)


async def _async_noop(*args, **kwargs):
    """No-op coroutine used to stub async_set_unique_id."""
