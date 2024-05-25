import logging
from .const import DOMAIN
from homeassistant.config_entries import ConfigEntry

from homeassistant.components.button import ButtonEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.persistent_notification import create
from homeassistant.helpers.template import device_id as get_device_id

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities) -> None:

    hon2 = hass.data[DOMAIN][entry.unique_id]

    appliances = []
    for appliance in hon2.appliances:

        coordinator = await hon2.async_get_coordinator(appliance)
        device = coordinator.device
        appliances.extend([Hon2BaseButtonEntity(coordinator, appliance)])
        if( "settings" in device.commands ):
            appliances.extend([Hon2BaseSettingsButtonEntity(coordinator, appliance)])


    async_add_entities(appliances)



class Hon2BaseButtonEntity(CoordinatorEntity, ButtonEntity):
    def __init__(self, coordinator, appliance) -> None:
        super().__init__(coordinator)
        self._coordinator   = coordinator
        self._device        = coordinator.device

        self._attr_unique_id = self._device.mac_address + "_start_button"
        self._attr_name = self._device.name + " Get programs details"

    @property
    def device_info(self):
        return self._device.device_info

    async def async_press(self) -> None:
        """Handle the button press."""
        command = self._device.commands.get("startProgram")
        programs = command.get_programs()
        device_id = get_device_id(self._coordinator.hass, self.entity_id)

        for program in programs.keys():
            command.set_program(program)
            command = self._device.commands.get("startProgram")
            alert_text, example = command.dump()

            text = f"""#### Parameters:
{alert_text}
#### Start this program with default parameters:
    service: hon2.start_program
    data:
      program: {program}
    target:
      device_id: {device_id}

#### Start this program with customized parameters:
    service: hon2.start_program
    data:
      program: {program}
      parameters: >-
        {example}
    target:
      device_id: {device_id}
"""
            create(self._coordinator.hass, text, "Program ["+program+"]")


            
class Hon2BaseSettingsButtonEntity(CoordinatorEntity, ButtonEntity):
    def __init__(self, coordinator, appliance) -> None:
        super().__init__(coordinator)
        self._coordinator   = coordinator
        self._device        = coordinator.device

        self._attr_unique_id = self._device.mac_address + "_settings_button"
        self._attr_name = self._device.name + " Get settings details"

    @property
    def device_info(self):
        return self._device.device_info

    async def async_press(self) -> None:
        """Handle the button press."""
        device_id = get_device_id(self._coordinator.hass, self.entity_id)
        command = self._device.commands.get("settings")
        alert_text, example = command.dump()

        text = f"""#### Parameters:
{alert_text}
#### Update settings:
    service: hon2.update_settings
    data:
      parameters: >-
        {example}
    target:
      device_id: {device_id}
"""
        create(self._coordinator.hass, text, "Get all settings")