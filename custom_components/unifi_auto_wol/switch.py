"""Switch platform for UniFi Auto WoL."""
import logging
import socket
from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_state_change_event

DOMAIN = "unifi_auto_wol"

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up UniFi Auto WoL switches."""
    
    coordinator = UniFiWoLCoordinator(hass, async_add_entities)
    hass.data[DOMAIN][config_entry.entry_id]["coordinator"] = coordinator
    
    # Initial setup
    await coordinator.async_setup()

class UniFiWoLCoordinator:
    """Coordinates UniFi device discovery and WoL switch creation."""
    
    def __init__(self, hass: HomeAssistant, async_add_entities):
        self.hass = hass
        self.async_add_entities = async_add_entities
        self._switches = {}  # MAC -> switch entity
        self._entity_registry_ids = {}  # MAC -> entity registry entry ID
        self._unsub = None
    
    async def async_setup(self):
        """Set up device tracking."""
        # Create switches for existing devices
        await self._scan_devices()
        
        # Track new devices using event bus
        from homeassistant.const import EVENT_STATE_CHANGED
        self._unsub = self.hass.bus.async_listen(
            EVENT_STATE_CHANGED, self._handle_state_change
        )
    
    async def _scan_devices(self):
        """Scan for UniFi devices and create switches."""
        new_switches = []
        current_macs = set()
        
        for state in self.hass.states.async_all():
            entity_id = state.entity_id
            if (entity_id.startswith("device_tracker.") and 
                state.attributes.get("source_type") == "router" and
                state.attributes.get("mac")):
                
                mac = state.attributes["mac"].upper()
                current_macs.add(mac)
                name = state.attributes.get("friendly_name") or entity_id.split(".")[-1]
                
                if mac not in self._switches:
                    # Create new switch
                    switch = UniFiWoLSwitch(
                        entity_id,
                        mac,
                        state.attributes.get("ip"),
                        name
                    )
                    self._switches[mac] = switch
                    new_switches.append(switch)
                else:
                    # Update existing switch if name changed
                    existing_switch = self._switches[mac]
                    new_name = f"WoL {name}"
                    if existing_switch._attr_name != new_name:
                        await self._update_switch_name(mac, name, entity_id, state.attributes.get("ip"))
        
        # Remove switches for devices no longer present
        await self._cleanup_removed_devices(current_macs)
        
        if new_switches:
            self.async_add_entities(new_switches)
            _LOGGER.info(f"Added {len(new_switches)} WoL switches")
    
    async def _update_switch_name(self, mac: str, new_name: str, entity_id: str, ip: str):
        """Update switch name and entity registry."""
        from homeassistant.helpers import entity_registry as er
        
        # Update the switch object
        switch = self._switches[mac]
        old_name = switch._attr_name
        switch._attr_name = f"WoL {new_name}"
        switch._device_entity_id = entity_id
        switch._ip = ip
        
        # Update entity registry
        entity_registry = er.async_get(self.hass)
        unique_id = f"wol_{mac.replace(':', '').lower()}"
        entry = entity_registry.async_get_entity_id("switch", "unifi_auto_wol", unique_id)
        
        if entry:
            entity_registry.async_update_entity(
                entry,
                name=f"WoL {new_name}",
                original_name=f"WoL {new_name}"
            )
            # Force state update
            switch.async_write_ha_state()
        
        _LOGGER.info(f"Updated WoL switch from '{old_name}' to 'WoL {new_name}' for MAC {mac}")
    
    async def _cleanup_removed_devices(self, current_macs: set):
        """Remove switches for devices no longer in UniFi."""
        from homeassistant.helpers import entity_registry as er
        
        removed_macs = set(self._switches.keys()) - current_macs
        entity_registry = er.async_get(self.hass)
        
        for mac in removed_macs:
            switch = self._switches.pop(mac)
            unique_id = f"wol_{mac.replace(':', '').lower()}"
            
            # Remove from entity registry
            entity_id = entity_registry.async_get_entity_id("switch", "unifi_auto_wol", unique_id)
            if entity_id:
                entity_registry.async_remove(entity_id)
                _LOGGER.info(f"Removed WoL switch for {switch._attr_name} (MAC: {mac}) - device no longer in UniFi")
    
    @callback
    def _handle_state_change(self, event):
        """Handle device tracker state changes."""
        entity_id = event.data["entity_id"]
        new_state = event.data["new_state"]
        
        if (entity_id.startswith("device_tracker.") and 
            new_state and
            new_state.attributes.get("source_type") == "router" and
            new_state.attributes.get("mac")):
            
            mac = new_state.attributes["mac"].upper()
            name = new_state.attributes.get("friendly_name") or entity_id.split(".")[-1]
            
            if mac not in self._switches:
                # Create new switch
                switch = UniFiWoLSwitch(
                    entity_id,
                    mac,
                    new_state.attributes.get("ip"),
                    name
                )
                self._switches[mac] = switch
                self.async_add_entities([switch])
                _LOGGER.info(f"Added new WoL switch for {switch._attr_name}")
            else:
                # Check if name changed
                existing_switch = self._switches[mac]
                new_name = f"WoL {name}"
                if existing_switch._attr_name != new_name:
                    self.hass.async_create_task(
                        self._update_switch_name(mac, name, entity_id, new_state.attributes.get("ip"))
                    )

class UniFiWoLSwitch(SwitchEntity):
    """Wake-on-LAN switch for UniFi device."""
    
    def __init__(self, device_entity_id: str, mac: str, ip: str, name: str):
        """Initialize the switch."""
        self._device_entity_id = device_entity_id
        self._mac = mac.upper()
        self._ip = ip
        self._attr_name = f"WoL {name}"
        self._attr_unique_id = f"wol_{mac.replace(':', '').lower()}"
        self._attr_icon = "mdi:power"
        self._attr_should_poll = False
    
    @property
    def name(self) -> str:
        """Return the name of the switch."""
        return self._attr_name
    
    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return self._attr_unique_id
    
    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {("unifi_auto_wol", self._mac)},
            "name": self._attr_name,
            "manufacturer": "UniFi Auto WoL",
            "model": "Wake-on-LAN Switch",
            "via_device": ("unifi", "controller"),
        }
    
    @property
    def extra_state_attributes(self):
        """Return extra state attributes."""
        return {
            "mac_address": self._mac,
            "ip_address": self._ip,
            "device_tracker": self._device_entity_id,
        }
    
    @property
    def is_on(self) -> bool:
        """Return if device is on based on device tracker state."""
        state = self.hass.states.get(self._device_entity_id)
        return state and state.state == "home"
    
    async def async_turn_on(self, **kwargs) -> None:
        """Send wake-on-LAN magic packet."""
        try:
            mac_bytes = bytes.fromhex(self._mac.replace(":", ""))
            magic_packet = b'\xff' * 6 + mac_bytes * 16
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            targets = []
            if self._ip:
                targets.append(self._ip)
            targets.append("255.255.255.255")
            
            for target in targets:
                try:
                    sock.sendto(magic_packet, (target, 9))
                    _LOGGER.info(f"Sent WoL packet to {self.name} at {target}")
                except Exception as e:
                    _LOGGER.warning(f"Failed to send WoL to {target}: {e}")
            
            sock.close()
            
        except Exception as e:
            _LOGGER.error(f"Failed to send WoL packet to {self.name}: {e}")
    
    async def async_turn_off(self, **kwargs) -> None:
        """Turn off is not supported for WoL."""
        pass