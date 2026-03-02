"""The Roth Touchline integration."""
from __future__ import annotations

import logging
from datetime import timedelta, datetime

from pytouchline import PyTouchline

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.CLIMATE, Platform.SENSOR, Platform.BUTTON]

SCAN_INTERVAL = timedelta(seconds=30)


class ExtendedPyTouchline(PyTouchline):
    """Extended PyTouchline with additional R0 parameters."""

    def __init__(self, id=0):
        """Initialize with extended parameters."""
        super().__init__(id=id)
        # Add R0.DateTime and R0.ErrorCode to the xml_element_list
        # These use type R (R0) instead of G (Gx)
        from pytouchline import Parameter
        self._xml_element_list.append(
            Parameter(name="R0.DateTime", desc="R0 DateTime", type=Parameter.R))
        self._xml_element_list.append(
            Parameter(name="R0.ErrorCode", desc="R0 ErrorCode", type=Parameter.R))

    def get_datetime(self):
        """Get R0.DateTime value in readable format."""
        if "R0 DateTime" in self._parameter:
            raw_value = self._parameter["R0 DateTime"]
            if raw_value and raw_value != "NA":
                try:
                    # Parse the datetime value if it's in a specific format
                    # The exact format depends on the controller output
                    return raw_value
                except Exception:
                    return raw_value
        return None

    def get_error_code(self):
        """Get R0.ErrorCode value."""
        if "R0 ErrorCode" in self._parameter:
            error_code = self._parameter["R0 ErrorCode"]
            return error_code if error_code != "NA" else None
        return None

    def get_owner_kurz_id(self):
        """Get ownerKurzID value - same as controller_id."""
        return self.get_controller_id()

    def set_datetime(self, datetime_value):
        """Set R0.DateTime value to sync controller time."""
        # For R0 parameters, we need to write directly to R0.DateTime
        # instead of using G prefix
        try:
            import httplib2
            h = httplib2.Http()
            (resp, content) = h.request(
                uri=PyTouchline._ip_address +
                    self._write_path + "?" +
                    "R0.DateTime=" + str(datetime_value),
                method="GET"
            )
            if resp.reason == "OK":
                return True
        except Exception as e:
            _LOGGER.error(f"Error setting datetime: {e}")
        return False

    def get_firmware_info(self):
        """Get STELL-APP, STELL-BL, STM-APP, STM-BL firmware versions."""
        fw_items = [
            "<i><n>STELL-APP</n></i>",
            "<i><n>STELL-BL</n></i>",
            "<i><n>STM-APP</n></i>",
            "<i><n>STM-BL</n></i>",
        ]
        request = self._get_touchline_request(fw_items)
        response = self._request_and_receive_xml(request)
        result = {}
        item_list = response.find("item_list")
        if item_list is not None:
            for item in item_list.findall("i"):
                name_el = item.find("n")
                value_el = item.find("v")
                if name_el is not None and value_el is not None:
                    result[name_el.text] = value_el.text
        return result

    def get_network_info(self):
        """Get hw.IP, hw.Addr, hw.HostName from the controller."""
        hw_items = [
            "<i><n>hw.IP</n></i>",
            "<i><n>hw.Addr</n></i>",
            "<i><n>hw.HostName</n></i>",
        ]
        request = self._get_touchline_request(hw_items)
        response = self._request_and_receive_xml(request)
        result = {}
        item_list = response.find("item_list")
        if item_list is not None:
            for item in item_list.findall("i"):
                name_el = item.find("n")
                value_el = item.find("v")
                if name_el is not None and value_el is not None:
                    result[name_el.text] = value_el.text
        return result

    def _get_touchline_device_item(self, id):
        """Override to include R0 parameters."""
        items = []
        parameters = ""
        from pytouchline import Parameter
        for parameter in self._xml_element_list:
            if parameter.get_type() == Parameter.G:
                parameters += "<n>G%d.%s</n>" % (id, parameter.get_name())
            elif parameter.get_type() == Parameter.R:
                parameters += "<n>%s</n>" % (parameter.get_name())
            else:
                parameters += "<n>CD.%s</n>" % (parameter.get_name())
        items.append("<i>" + parameters + "</i>")
        return items


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Roth Touchline from a config entry."""
    host = entry.data[CONF_HOST]

    coordinator = TouchlineDataUpdateCoordinator(hass, host)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


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
        self.devices: list[ExtendedPyTouchline] = []
        self.controller_id: int | None = None
        self.controller_status: str | None = None
        self.owner_kurz_id: str | None = None
        self.datetime: str | None = None
        self.error_code: str | None = None
        self.hw_ip: str | None = None
        self.hw_mac: str | None = None
        self.hw_hostname: str | None = None
        self._hw_info_loaded: bool = False
        self.fw_stell_app: str | None = None
        self.fw_stell_bl: str | None = None
        self.fw_stm_app: str | None = None
        self.fw_stm_bl: str | None = None
        self._fw_info_loaded: bool = False

    async def _async_update_data(self) -> list[ExtendedPyTouchline]:
        """Fetch data from Touchline controller."""
        try:
            return await self.hass.async_add_executor_job(self._fetch_data)
        except Exception as err:
            raise UpdateFailed(f"Error communicating with Touchline: {err}") from err

    def _fetch_data(self) -> list[ExtendedPyTouchline]:
        """Synchronously fetch all device data."""
        if not self.devices:
            probe = ExtendedPyTouchline()
            # get_number_of_devices sets the class-level _ip_address used by update()
            num = int(probe.get_number_of_devices(self._url))
            self.devices = [ExtendedPyTouchline(id=i) for i in range(num)]
        else:
            # Ensure the class-level URL stays current (e.g. after HA restart)
            ExtendedPyTouchline._ip_address = self._url

        for device in self.devices:
            device.update()

        if self.devices:
            # controller_id and controller_status are system-level values shared
            # across all devices; reading from the first device is sufficient.
            self.controller_id = self.devices[0].get_controller_id()
            self.controller_status = self.devices[0].get_status()

            # Get ownerKurzID - use get_owner_kurz_id() method
            controller_id = self.devices[0].get_owner_kurz_id()
            self.owner_kurz_id = str(controller_id) if controller_id is not None else None

            # Get datetime and error_code
            self.datetime = self.devices[0].get_datetime()
            self.error_code = self.devices[0].get_error_code()

        if not self._hw_info_loaded and self.devices:
            try:
                hw_info = self.devices[0].get_network_info()
                self.hw_ip = hw_info.get("hw.IP")
                self.hw_mac = hw_info.get("hw.Addr")
                self.hw_hostname = hw_info.get("hw.HostName")
                self._hw_info_loaded = True
            except Exception:
                _LOGGER.warning("Could not fetch hw network info", exc_info=True)

        if not self._fw_info_loaded and self.devices:
            try:
                fw_info = self.devices[0].get_firmware_info()
                self.fw_stell_app = fw_info.get("STELL-APP")
                self.fw_stell_bl = fw_info.get("STELL-BL")
                self.fw_stm_app = fw_info.get("STM-APP")
                self.fw_stm_bl = fw_info.get("STM-BL")
                self._fw_info_loaded = True
            except Exception:
                _LOGGER.warning("Could not fetch firmware info", exc_info=True)

        return self.devices
