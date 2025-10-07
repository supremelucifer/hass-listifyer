
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

from .sensor_base import ListifyerDataSensor, DATA_TYPES

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:

    sensors = [ListifyerDataSensor(data_type) for data_type in DATA_TYPES]
    async_add_entities(sensors)