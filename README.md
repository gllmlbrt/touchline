# Roth Touchline Integration for Home Assistant

A custom Home Assistant integration for Roth Touchline underfloor heating controllers with LAN connection. This integration provides full control over your Roth Touchline heating system directly from Home Assistant.

## Compatibility

This integration has been developed for and tested to be **fully functional** with older **Roth Touchline Controllers with LAN connection**, distributed between **2011 and 2017** with latest firmware version **2.8**.

## Features

This custom integration provides enhanced functionality compared to the core Home Assistant Touchline integration:

### Enhanced Features
- **Virtual Heat Mode**: Optional HVAC action monitoring with intelligent hysteresis control
- **Extended System Monitoring**: Access to controller datetime, error codes, and system status sensors
- **Time Synchronization**: Built-in button entity to sync controller time with Home Assistant
- **Controller Metadata**: Retrieves ownerKurzID and additional R0 parameters from the controller
- **Comprehensive Device Information**: Full device registry integration with proper serial numbers and device relationships
- **Multiple Preset Modes**: Support for Normal, Night, and 3 custom program modes (Pro 1, Pro 2, Pro 3)

### Core Features
- **Climate Control**: Full thermostat control for all heating zones
  - Set target temperature
  - View current temperature
  - Switch between heat and off modes
  - Multiple preset modes (Normal, Night, Pro 1-3)
- **Sensors**:
  - System status monitoring
  - Controller datetime display
  - Error code reporting
- **Button Entities**:
  - Time synchronization button

### Supported Platforms
- Climate (Thermostat zones)
- Sensor (System status, datetime, error codes)
- Button (Time sync)

## Installation

### HACS Installation (Recommended)

1. Make sure you have [HACS](https://hacs.xyz/) installed in your Home Assistant instance
2. In Home Assistant, go to **HACS** → **Integrations**
3. Click the **⋮** menu in the top right corner and select **Custom repositories**
4. Add this repository URL: `https://github.com/gllmlbrt/touchline`
5. Select **Integration** as the category
6. Click **Add**
7. Search for "Roth Touchline" in HACS
8. Click **Download**
9. Restart Home Assistant

### Manual Installation

1. Download the latest release from the [releases page](https://github.com/gllmlbrt/touchline/releases)
2. Extract the downloaded archive
3. Copy the `custom_components/touchline` folder to your Home Assistant's `custom_components` directory
   - If the `custom_components` directory doesn't exist, create it in your Home Assistant configuration directory
   - The path should look like: `config/custom_components/touchline/`
4. Restart Home Assistant

**Note**: This custom integration will override the core Home Assistant Touchline integration when installed.

## Configuration

### Adding the Integration

1. In Home Assistant, go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Roth Touchline"
4. Enter the IP address or hostname of your Touchline controller
5. Click **Submit**

The integration will automatically discover all heating zones configured on your controller.

### Configuration via UI

All configuration is done through the Home Assistant UI. No YAML configuration is required.

### Optional Features

#### Virtual Heat Mode

The integration includes an optional **Virtual Heat Mode** feature that provides HVAC action monitoring for your climate entities. This feature displays whether your heating system is actively heating or idle, giving you better visibility into your system's operation.

**Enabling Virtual Heat Mode:**
1. Go to **Settings** → **Devices & Services**
2. Find the "Roth Touchline" integration
3. Click **Configure**
4. Check the **"Virtual heat mode"** option
5. Click **Submit**

**How It Works:**

Virtual heat mode uses intelligent temperature-based logic with hysteresis control to determine the heating state:

- **Heating State**: Activated when the current temperature drops **0.2°C or more** below the target temperature
- **Idle State**: Activated when the current temperature rises **0.3°C or more** above the target temperature (with a 5-minute delay)
- **Hysteresis Band**: When temperature is within the -0.3°C to +0.2°C range relative to target, the system maintains its current state to prevent frequent switching

**Benefits:**
- **Better Visibility**: See at a glance whether your heating is actively working or idle
- **Energy Monitoring**: Track heating activity for better energy management
- **Automation Triggers**: Use HVAC action states in Home Assistant automations
- **Reduced Oscillation**: Asymmetric hysteresis prevents rapid on/off cycling

**Example Use Cases:**
- Create automations that notify you when heating starts or stops
- Track daily heating activity patterns
- Optimize heating schedules based on actual heating demand
- Monitor system efficiency

**Note**: This is a virtual/simulated feature based on temperature differences. The Roth Touchline controller itself does not provide direct heating state information.

## Usage

### Climate Entities

Each heating zone in your Roth Touchline system will be available as a climate entity. You can:
- **View current temperature**: Check the current temperature reading from each zone
- **Set target temperature**: Adjust the desired temperature for each zone
- **Monitor HVAC action** (when virtual heat mode is enabled): See whether the zone is actively heating, idle, or off
- **Change HVAC mode**:
  - `Heat`: Normal heating operation
  - `Off`: Holiday mode (disables heating)
- **Select preset modes**:
  - `Normal`: Auto mode with default program (program 0)
  - `Night`: Manual temperature control
  - `Pro 1`, `Pro 2`, `Pro 3`: Auto mode with custom programs 1, 2, or 3

### Sensor Entities

The integration provides system-level sensors:
- **System Status**: Current operational status of the controller
- **Controller DateTime**: Current date and time stored in the controller
- **Controller Error Code**: Any error codes reported by the controller

### Button Entities

- **Sync Time**: Synchronizes the controller's internal clock with Home Assistant's system time

## Troubleshooting

### Integration Not Found
If you don't see "Roth Touchline" in the integrations list after installation:
1. Ensure you've restarted Home Assistant after installation
2. Clear your browser cache
3. Check that the files are in the correct location: `config/custom_components/touchline/`

### Connection Issues
If the integration fails to connect:
1. Verify the IP address of your Touchline controller
2. Ensure the controller is on the same network as Home Assistant
3. Check that the controller's web interface is accessible from a browser at `http://<controller-ip>`
4. Verify your controller firmware version is 2.8 or compatible

### Time Sync Issues
If time synchronization fails:
1. Check the error logs in Home Assistant
2. Verify the controller is responding to web requests
3. Try refreshing the integration

## Support

For issues, feature requests, or contributions, please visit the [GitHub repository](https://github.com/gllmlbrt/touchline).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

This integration uses the [pyTouchline](https://github.com/jmahmens/pyTouchline) library for communication with Roth Touchline controllers.
