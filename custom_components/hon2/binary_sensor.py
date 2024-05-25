import logging
import asyncio
import json
from datetime import datetime, timedelta, timezone
from dateutil.tz import gettz
from typing import Optional
from enum import IntEnum

from .const import DOMAIN, APPLIANCE_TYPE
from .base import Hon2BaseCoordinator, Hon2BaseBinarySensorEntity

from homeassistant.core import callback
from homeassistant.helpers import entity_platform
from homeassistant.config_entries import ConfigEntry

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, entry: ConfigEntry, async_add_entities) -> None:

    hon2 = hass.data[DOMAIN][entry.unique_id]

    appliances = []
    for appliance in hon2.appliances:

        coordinator = await hon2.async_get_coordinator(appliance)
        device = coordinator.device

        # Every device should have a OnOff status
        appliances.extend([Hon2BaseOnOff(hass, coordinator, entry, appliance)])

        if device.has("doorStatusZ1"):
            appliances.extend([Hon2BaseDoorStatus(hass, coordinator, entry, appliance, "Z1", "zone 1")])
        if device.has("doorStatusZ2"):
            appliances.extend([Hon2BaseDoorStatus(hass, coordinator, entry, appliance, "Z2", "zone 2")])
        if device.has("doorLockStatus"):
            appliances.extend([Hon2BaseDoorLockStatus(hass, coordinator, entry, appliance)])

        if device.has("door2StatusZ1"):
            appliances.extend([Hon2BaseDoor2Status(hass, coordinator, entry, appliance, "Z1", "zone 1")])
        if device.has("door2StatusZ2"):
            appliances.extend([Hon2BaseDoor2Status(hass, coordinator, entry, appliance, "Z2", "zone 2")])

        if device.has("lockStatus"):
            appliances.extend([Hon2BaseChildLockStatus(hass, coordinator, entry, appliance)])
        if device.has("lightStatus"):
            appliances.extend([Hon2BaseLightStatus(hass, coordinator, entry, appliance)])
        if device.has("remoteCtrValid"):
            appliances.extend([Hon2BaseRemoteControl(hass, coordinator, entry, appliance)])
        if device.has("preheatStatus"):
            appliances.extend([Hon2BasePreheating(hass, coordinator, entry, appliance)])
        if device.has("healthMode"):
            appliances.extend([Hon2BaseHealthMode(hass, coordinator, entry, appliance)])

    async_add_entities(appliances)




class Hon2BaseOnOff(Hon2BaseBinarySensorEntity):
    def __init__(self, hass, coordinator, entry, appliance) -> None:
        super().__init__(coordinator, appliance, "onOffStatus", "Status")

        self._attr_device_class = BinarySensorDeviceClass.POWER

    def coordinator_update(self):
        if self._device.has("onOffStatus"):
            self._attr_is_on = self._device.get("onOffStatus") == "1"
        else:
            self._attr_is_on = self._device.get("attributes.lastConnEvent.category") == "CONNECTED"

class Hon2BaseDoorStatus(Hon2BaseBinarySensorEntity):
    def __init__(self, hass, coordinator, entry, appliance, zone, zone_name) -> None:
        super().__init__(coordinator, appliance, "doorStatus" + zone, f"Door status {zone_name}")

        self._attr_device_class = BinarySensorDeviceClass.DOOR

class Hon2BaseDoor2Status(Hon2BaseBinarySensorEntity):
    def __init__(self, hass, coordinator, entry, appliance, zone, zone_name) -> None:
        super().__init__(coordinator, appliance, "door2Status" + zone, f"Door 2 status {zone_name}")

        self._attr_device_class = BinarySensorDeviceClass.DOOR


class Hon2BaseLightStatus(Hon2BaseBinarySensorEntity):
    def __init__(self, hass, coordinator, entry, appliance) -> None:
        super().__init__(coordinator, appliance, "lightStatus", "Light")

        self._attr_device_class = BinarySensorDeviceClass.LIGHT
        self._attr_icon = "mdi:lightbulb"

        self._attr_supported_attributes = ["SET_LIGHT"]

    @property
    def supported_attributes(self) -> set[str] | None:
        return self._attr_supported_attributes

class Hon2BaseRemoteControl(Hon2BaseBinarySensorEntity):
    def __init__(self, hass, coordinator, entry, appliance) -> None:
        super().__init__(coordinator, appliance, "remoteCtrValid", "Remote control")

        self._attr_device_class = BinarySensorDeviceClass.CONNECTIVITY
        self._attr_icon = "mdi:remote"


class Hon2BaseDoorLockStatus(Hon2BaseBinarySensorEntity):
    def __init__(self, hass, coordinator, entry, appliance) -> None:
        super().__init__(coordinator, appliance, "doorLockStatus", "Door lock")

        self._attr_device_class = BinarySensorDeviceClass.LOCK

    def coordinator_update(self):
        self._attr_is_on = self._device.get("doorLockStatus") == "0"


class Hon2BaseChildLockStatus(Hon2BaseBinarySensorEntity):
    def __init__(self, hass, coordinator, entry, appliance) -> None:
        super().__init__(coordinator, appliance, "lockStatus", "Child lock")

        translation_key = "lockStatus"
        self._attr_device_class = BinarySensorDeviceClass.LOCK

    def coordinator_update(self):
        self._attr_is_on = self._device.get("lockStatus") == "0"

class Hon2BasePreheating(Hon2BaseBinarySensorEntity):
    def __init__(self, hass, coordinator, entry, appliance) -> None:
        super().__init__(coordinator, appliance, "preheatStatus", "Preheating")

        self._attr_device_class = BinarySensorDeviceClass.HEAT
        self._attr_icon = "mdi:thermometer-chevron-up"


class Hon2BaseHealthMode(Hon2BaseBinarySensorEntity):
    def __init__(self, hass, coordinator, entry, appliance) -> None:
        super().__init__(coordinator, appliance, "healthMode", "Health mode")

        self._attr_device_class = BinarySensorDeviceClass.RUNNING
        self._attr_icon = "mdi:doctor"