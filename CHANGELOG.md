# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-06-24

### Added
- Initial release
- Automatic discovery of UniFi devices for Wake-on-LAN
- Dynamic switch creation for devices with MAC addresses
- Real-time name synchronization with UniFi device names
- Automatic cleanup of switches for removed devices
- Device online/offline status based on UniFi presence detection
- Entity registry integration for persistent device management

### Features
- No duplicate switches (one per MAC address)
- Updates switch names when UniFi device names change
- Removes switches for devices no longer in UniFi
- Shows device attributes (MAC address, IP, device tracker entity)
- Compatible with HACS installation
