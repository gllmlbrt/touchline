"""The Roth Touchline integration."""
from __future__ import annotations

import logging
from datetime import timedelta

from pytouchline import PyTouchline

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.CLIMATE, Platform.SENSOR]

SCAN_INTERVAL = timedelta(seconds=30)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Roth Touchline from a config entry."""
    host = entry.data[CONF_HOST]

    coordinator = TouchlineDataUpdateCoordinator(hass, host)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


class TouchlineDataUpdateCoordinator(DataUpdateCoordinator):
    """Coordinator to manage fetching Touchline data."""

    def __init__(self, hass: HomeAssistant, host: str) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.host = host
        self._url = f"http://{host}"
        self.devices: list[PyTouchline] = []
        self.controller_id: int | None = None
        self.controller_status: str | None = None

    async def _async_update_data(self) -> list[PyTouchline]:
        """Fetch data from Touchline controller."""
        try:
            return await self.hass.async_add_executor_job(self._fetch_data)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with Touchline: {err}") from err

    def _fetch_data(self) -> list[PyTouchline]:
        """Synchronously fetch all device data."""
        if not self.devices:
            probe = PyTouchline()
            # get_number_of_devices sets the class-level _ip_address used by update()
            num = int(probe.get_number_of_devices(self._url))
            self.devices = [PyTouchline(id=i) for i in range(num)]
        else:
            # Ensure the class-level URL stays current (e.g. after HA restart)
            PyTouchline._ip_address = self._url

        for device in self.devices:
            device.update()

        if self.devices:
            # controller_id and controller_status are system-level values shared
            # across all devices; reading from the first device is sufficient.
            self.controller_id = self.devices[0].get_controller_id()
            self.controller_status = self.devices[0].get_status()

        return self.devices
