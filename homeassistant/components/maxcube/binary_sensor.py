"""Support for MAX! binary sensors via MAX! Cube."""
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import DATA_KEY


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_devices: AddEntitiesCallback,
) -> None:
    """Set up a binary sensor for maxcube."""
    devices: list[MaxCubeBinarySensorBase] = []
    for handler in hass.data[DATA_KEY].values():
        for device in handler.cube.devices:
            devices.append(MaxCubeBattery(handler, device))
            # Only add Window Shutters
            if device.is_windowshutter():
                devices.append(MaxCubeShutter(handler, device))

    if devices:
        async_add_devices(devices)


class MaxCubeBinarySensorBase(BinarySensorEntity):
    """Base class for maxcube binary sensors."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, handler, device):
        """Initialize MAX! Cube BinarySensorEntity."""
        self._cubehandle = handler
        self._device = device
        self._room = handler.cube.room_by_id(device.room_id)

    def update(self):
        """Get latest data from MAX! Cube."""
        self._cubehandle.update()


class MaxCubeShutter(MaxCubeBinarySensorBase):
    """Representation of a MAX! Cube Binary Sensor device."""

    _attr_device_class = BinarySensorDeviceClass.WINDOW

    def __init__(self, handler, device):
        """Initialize MAX! Cube BinarySensorEntity."""
        super().__init__(handler, device)

        self._attr_name = f"{self._room.name} {self._device.name}"
        self._attr_unique_id = self._device.serial

    @property
    def is_on(self):
        """Return true if the binary sensor is on/open."""
        return self._device.is_open


class MaxCubeBattery(MaxCubeBinarySensorBase):
    """Representation of a MAX! Cube Binary Sensor device."""

    _attr_device_class = BinarySensorDeviceClass.BATTERY

    def __init__(self, handler, device):
        """Initialize MAX! Cube BinarySensorEntity."""
        super().__init__(handler, device)

        self._attr_name = f"{self._room.name} {device.name} battery"
        self._attr_unique_id = f"{self._device.serial}_battery"

    @property
    def is_on(self):
        """Return true if the binary sensor is on/open."""
        return self._device.battery == 1
