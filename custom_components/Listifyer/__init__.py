"""The Listifyer App integration."""
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


PLATFORMS: list[str] = ["sensor"]



async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Listifyer from a config entry."""
    
   
    hass.data.setdefault(DOMAIN, {})

    @callback
    def async_handle_update(data_type: str, data: Any):
        """Find the correct sensor entity and call its update method."""
     
        entity_id = f"sensor.listifyer_{data_type}"
        

        entity_registry = async_get_entity_registry(hass)
        

        entity = entity_registry.async_get(entity_id)

        if entity:
         
            sensor_entity = hass.data["sensor"].get_entity(entity_id)
            if sensor_entity:
        
                hass.async_create_task(sensor_entity.async_update_data(data))
            else:
                _LOGGER.warning("Could not find sensor entity object for %s", entity_id)
        else:
            _LOGGER.debug("Sensor entity %s not found in registry yet.", entity_id)

   
    hass.data[DOMAIN][entry.entry_id] = async_handle_update

 
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
   
    hass.data[DOMAIN].pop(entry.entry_id)
    
  
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    
    return unload_ok