"""Config flow for Roth Touchline integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from pytouchline import PyTouchline

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
    }
)


class TouchlineConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Roth Touchline."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            try:
                num_devices = await self.hass.async_add_executor_job(
                    self._get_number_of_devices, host
                )
                if num_devices is None or int(num_devices) < 1:
                    errors["base"] = "no_devices"
                else:
                    await self.async_set_unique_id(host)
                    self._abort_if_unique_id_configured()
                    return self.async_create_entry(
                        title=host,
                        data={CONF_HOST: host},
                    )
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Unexpected error connecting to Touchline controller")
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    @staticmethod
    def _get_number_of_devices(host: str) -> str:
        """Return number of devices from the controller."""
        touchline = PyTouchline()
        return touchline.get_number_of_devices(f"http://{host}")
