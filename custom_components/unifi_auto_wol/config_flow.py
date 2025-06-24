"""Config flow for UniFi Auto WoL."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

DOMAIN = "unifi_auto_wol"

class UniFiAutoWoLConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow for UniFi Auto WoL."""
    
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
            
        if user_input is not None:
            return self.async_create_entry(
                title="UniFi Auto Wake-on-LAN",
                data={}
            )
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            description_placeholders={}
        )