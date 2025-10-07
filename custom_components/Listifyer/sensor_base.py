"""Base class and definitions for Listifyer sensors."""
import logging
from typing import Any, Dict
from datetime import datetime

from homeassistant.helpers.restore_state import RestoreEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

DATA_TYPES = [
    "shopping_list", "todo_list", "recipes", "wishlist", "trips",
    "diary_entries", "bucket_list", "custom_workout_categories", "workout_exercises",
    "workout_logs", "workout_routines", "media_items", "medications",
    "countdowns", "stopwatch_sessions", "voice_recordings", "meal_plan", "trip_logs",
    "fixed_addresses", "documents", "training_event", "notes", "bills", "bill_exceptions",
    "incomes", "mood_entries", "pantry_items", "custom_moods", "activities", "goals",
    "goal_logs", "activity_streaks", "work_logs", "surcharges",
    "lieutime_logs", "appointments"
]

ICONS = { "shopping_list": "mdi:cart", "todo_list": "mdi:check-circle-outline", "recipes": "mdi:silverware-fork-knife", "wishlist": "mdi:gift", "trips": "mdi:wallet-travel", "bills": "mdi:receipt", "appointments": "mdi:calendar-month", "medications": "mdi:pill", "workout_routines": "mdi:dumbbell", "pantry_items": "mdi:food-apple" }


MONTHLY_FILTER_TYPES = [
    "trips",
    "appointments",
    "work_logs",
    "bills",
    "incomes",
    "mood_entries",
    "diary_entries",
    "bill_exceptions",
    "surcharges",
    "lieutime_logs",
    "stopwatch_sessions",
    "workout_logs",
    "goal_logs"
]

DAILY_FILTER_TYPES = [
    "medications"
]


class ListifyerDataSensor(RestoreEntity):
    """Represents a sensor that is updated via the REST API by the Listifyer app."""

    def __init__(self, data_type: str):
        self._data_type = data_type
        self._name = f"Listifyer {data_type.replace('_', ' ').title()}"
        self._state = 0
        self._attributes: Dict[str, Any] = {"items": []}
        self._unique_id = f"{DOMAIN}_{self._data_type}"
        self._icon = ICONS.get(data_type, "mdi:format-list-bulleted-type")

    async def async_added_to_hass(self) -> None:
        """Restore last known state."""
        await super().async_added_to_hass()
        last_state = await self.async_get_last_state()
        if last_state:
            self._state = last_state.state
            self._attributes = last_state.attributes


    async def async_update_data(self, data: Any) -> None:
        """Update sensor data, filtering if necessary, and schedule a state update."""
        _LOGGER.debug("Updating data for sensor: %s", self._name)
        
        processed_data = data

    
        if isinstance(data, list):
            if self._data_type in MONTHLY_FILTER_TYPES:
                processed_data = self._filter_for_current_month(data)
            elif self._data_type in DAILY_FILTER_TYPES:
                processed_data = self._filter_for_current_day(data)

        # Update de staat en attributen met de (mogelijk gefilterde) data
        if isinstance(processed_data, list):
            self._state = len(processed_data)
            self._attributes["items"] = processed_data
        else: # Voor data die geen lijst is (bv. meal_plan)
            self._state = 1 if processed_data else 0
            self._attributes["item"] = processed_data
        
        self.async_write_ha_state()


    def _filter_for_current_month(self, data: list) -> list:
        """Filters a list of items to only include those relevant to the current month."""
        now = datetime.now()
        current_year = now.year
        current_month = now.month
        filtered_list = []

    
        types_with_simple_date = [
            "appointments", "work_logs", "incomes", "mood_entries", "diary_entries", 
            "bill_exceptions", "surcharges", "lieutime_logs", "stopwatch_sessions",
            "workout_logs", "goal_logs"
        ]

        for item in data:
            try:
                item_is_relevant = False
         
                if self._data_type in types_with_simple_date:
                    date_str = item.get("date")
                    if date_str:
                        item_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                        if item_date.year == current_year and item_date.month == current_month:
                            item_is_relevant = True

            
                elif self._data_type == "trips":
                    start_date_str = item.get("startDate")
                    if start_date_str:
                        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                        if start_date.year == current_year and start_date.month == current_month:
                            item_is_relevant = True
                    
                    # Als de trip niet deze maand start, kijk of hij deze maand eindigt
                    if not item_is_relevant:
                        end_date_str = item.get("endDate")
                        if end_date_str:
                            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
                            if end_date.year == current_year and end_date.month == current_month:
                                item_is_relevant = True

                # Logica voor 'bills' die deze maand actief zijn
                elif self._data_type == "bills":
                    start_date_str = item.get("startDate")
                    end_date_str = item.get("endDate")
                    if start_date_str:
                        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                        # De rekening moet al gestart zijn
                        if start_date <= now.date():
                            # En hij is nog niet afgelopen (of heeft geen einddatum)
                            if not end_date_str or datetime.strptime(end_date_str, "%Y-%m-%d").date() >= now.date():
                                item_is_relevant = True

                if item_is_relevant:
                    filtered_list.append(item)

            except (ValueError, TypeError) as e:
                _LOGGER.warning("Could not parse date for item in %s: %s. Error: %s", self._data_type, item, e)
        
        return filtered_list

    # ===================================================================
    # NIEUWE DAGELIJKSE FILTERLOGICA
    # ===================================================================
    def _filter_for_current_day(self, data: list) -> list:
        """Filters a list of items to only include those relevant to the current day."""
        now_date = datetime.now().date()
        filtered_list = []

        for item in data:
            try:
                item_is_relevant = False

                # Logica voor 'medications' die vandaag actief zijn
                if self._data_type == "medications":
                    start_date_str = item.get("startDate")
                    end_date_str = item.get("endDate")
                    
                    if start_date_str:
                        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
                        
                        # Vandaag moet na of op de startdatum zijn
                        is_started = start_date <= now_date
                        
                        # Als er een einddatum is, moet vandaag voor of op die datum zijn
                        is_not_ended = not end_date_str or datetime.strptime(end_date_str, "%Y-%m-%d").date() >= now_date
                        
                        if is_started and is_not_ended:
                            # Hier kan eventueel nog complexere logica komen voor bv. specifieke dagen van de week
                            item_is_relevant = True
                
                if item_is_relevant:
                    filtered_list.append(item)

            except (ValueError, TypeError) as e:
                _LOGGER.warning("Could not parse date for item in %s: %s. Error: %s", self._data_type, item, e)
        
        return filtered_list
    
    # De properties blijven ongewijzigd
    @property
    def unique_id(self) -> str:
        return self._unique_id
    @property
    def name(self) -> str:
        return self._name
    @property
    def state(self) -> int:
        return self._state
    @property
    def extra_state_attributes(self) -> Dict[str, Any]:
        return self._attributes
    @property
    def icon(self) -> str:
        return self._icon
    @property
    def should_poll(self) -> bool:
        return False