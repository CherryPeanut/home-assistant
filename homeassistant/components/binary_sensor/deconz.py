"""
Support for deCONZ binary sensor.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/binary_sensor.deconz/
"""

import asyncio

from homeassistant.components.binary_sensor import BinarySensorDevice
from homeassistant.components.deconz import DOMAIN as DECONZ_DATA
from homeassistant.const import ATTR_BATTERY_LEVEL
from homeassistant.core import callback

DEPENDENCIES = ['deconz']


@asyncio.coroutine
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """Setup binary sensor for deCONZ component."""
    if discovery_info is None:
        return

    from pydeconz.sensor import DECONZ_BINARY_SENSOR
    sensors = hass.data[DECONZ_DATA].sensors
    entities = []

    for key in sorted(sensors.keys(), key=int):
        sensor = sensors[key]
        if sensor and sensor.type in DECONZ_BINARY_SENSOR:
            entities.append(DeconzBinarySensor(sensor))
    async_add_devices(entities, True)


class DeconzBinarySensor(BinarySensorDevice):
    """Representation of a binary sensor."""

    def __init__(self, sensor):
        """Setup sensor and add update callback to get data from websocket."""
        self._sensor = sensor

    @asyncio.coroutine
    def async_added_to_hass(self):
        """Subscribe sensors events."""
        self._sensor.register_async_callback(self.async_update_callback)

    @callback
    def async_update_callback(self, reason):
        """Update the sensor's state.

        If reason is that state is updated,
        or reachable has changed or battery has changed.
        """
        if reason['state'] or \
           'reachable' in reason['attr'] or \
           'battery' in reason['attr']:
            self.async_schedule_update_ha_state()

    @property
    def is_on(self):
        """Return true if sensor is on."""
        return self._sensor.is_tripped

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._sensor.name

    @property
    def device_class(self):
        """Class of the sensor."""
        return self._sensor.sensor_class

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        return self._sensor.sensor_icon

    @property
    def available(self):
        """Return True if sensor is available."""
        return self._sensor.reachable

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def device_state_attributes(self):
        """Return the state attributes of the sensor."""
        from pydeconz.sensor import PRESENCE
        attr = {
            ATTR_BATTERY_LEVEL: self._sensor.battery,
        }
        if self._sensor.type == PRESENCE:
            attr['dark'] = self._sensor.dark
        return attr
