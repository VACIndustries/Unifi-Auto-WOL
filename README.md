# UniFi Auto Wake-on-LAN

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]][license]
[![hacs][hacsbadge]][hacs]

Automatically creates Wake-on-LAN switches for all devices discovered by the UniFi integration in Home Assistant.

## Features

- 🔄 **Automatic Discovery**: Creates WoL switches for all UniFi devices with MAC addresses
- 🏷️ **Name Sync**: Updates switch names when you rename devices in UniFi
- 🧹 **Auto Cleanup**: Removes switches for devices no longer in UniFi
- 📱 **Real-time Monitoring**: Shows device online/offline status based on UniFi presence
- 🎯 **No Duplicates**: One switch per MAC address, regardless of name changes

## Prerequisites

- Home Assistant with the [UniFi integration](https://www.home-assistant.io/integrations/unifi/) configured
- UniFi devices with Wake-on-LAN capability enabled in BIOS/OS
- Devices must be connected via Ethernet (Wi-Fi WoL is unreliable)

## Installation

### HACS (Recommended)

1. Ensure [HACS](https://hacs.xyz/) is installed
2. Go to HACS → Integrations
3. Click the three dots in the top right → Custom repositories
4. Add this repository URL with category "Integration"
5. Find "UniFi Auto Wake-on-LAN" and click Install
6. Restart Home Assistant

### Manual Installation

1. Download the `custom_components/unifi_auto_wol` folder
2. Copy it to your `config/custom_components/` directory
3. Restart Home Assistant

## Configuration

1. Go to Settings → Devices & Services
2. Click "Add Integration"
3. Search for "UniFi Auto Wake-on-LAN"
4. Click to add it

The integration will automatically:
- Scan for existing UniFi devices
- Create WoL switches for devices with MAC addresses
- Monitor for new devices and name changes

## Usage

### Wake a Device
- Use the switch in the UI: `switch.wol_device_name`
- Call the service: `switch.turn_on` with entity `switch.wol_device_name`
- In automations:
```yaml
service: switch.turn_on
target:
  entity_id: switch.wol_my_computer
```

### Switch States
- **On**: Device is connected to UniFi (online)
- **Off**: Device is not connected to UniFi (offline/sleeping)

## Enabling Wake-on-LAN on Devices

### Windows
1. Open Device Manager
2. Find your network adapter → Properties
3. Power Management tab
4. Enable "Allow this device to wake the computer"
5. Enable "Only allow a magic packet to wake the computer"

### BIOS/UEFI
1. Boot into BIOS/UEFI settings
2. Look for "Wake on LAN", "WOL", or "Power on by PCI-E"
3. Enable the setting
4. Save and exit

### Linux
```bash
sudo ethtool -s eth0 wol g
```

## Troubleshooting

### Switch Not Created
- Verify UniFi integration is working
- Check that device has a MAC address in device tracker attributes
- Check logs for errors: `grep unifi_auto_wol home-assistant.log`

### Wake-on-LAN Not Working
- Ensure device has WoL enabled in BIOS and OS
- Use Ethernet connection (Wi-Fi WoL is unreliable)
- Check if device is on same network segment
- Test manually: `wakeonlan AA:BB:CC:DD:EE:FF`

### Name Not Updating
- Integration updates names automatically when UniFi device names change
- Restart integration if names seem stuck
- Check entity registry for conflicts

## Advanced Usage

### Automation Example
```yaml
automation:
  - alias: "Wake Computer When I Get Home"
    trigger:
      - platform: state
        entity_id: person.me
        to: "home"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.wol_my_computer
```

### Script Example
```yaml
script:
  wake_all_computers:
    alias: "Wake All Computers"
    sequence:
      - service: switch.turn_on
        target:
          entity_id:
            - switch.wol_desktop
            - switch.wol_server
            - switch.wol_laptop
```

## Contributing

Issues and pull requests are welcome! Please check existing issues before creating new ones.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

[releases-shield]: https://img.shields.io/github/release/yourusername/unifi-auto-wol.svg?style=for-the-badge
[releases]: https://github.com/yourusername/unifi-auto-wol/releases
[commits-shield]: https://img.shields.io/github/commit-activity/y/yourusername/unifi-auto-wol.svg?style=for-the-badge
[commits]: https://github.com/yourusername/unifi-auto-wol/commits/main
[license-shield]: https://img.shields.io/github/license/yourusername/unifi-auto-wol.svg?style=for-the-badge
[license]: https://github.com/yourusername/unifi-auto-wol/blob/main/LICENSE
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
