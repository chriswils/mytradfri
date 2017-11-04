"""
    HomeAssistant: Thingy52 temperature sensor

    This sensor device is taking data from the Nordic Thingy:52 IoT Sensor Platform.
    It is derived from HA example sensor; https://home-assistant.io/developers/platform_example_sensor/
    and uses bluepy's Thingy:52 implementation. More docs on this and snippets used in this file is 
    found at Nordic Semiconductor's devzone blog:
    https://devzone.nordicsemi.com/blogs/1162/nordic-thingy52-raspberry-pi-python-interface/

"""

from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.entity import Entity
from bluepy import btle, thingy52
import binascii

# DEPENDENCIES = ['libglib2.0-dev']
# REQUIREMENTS = ['bluepy']

# TODO: Should be fetched from config file
MAC_ADDRESS = "d0:c0:1d:b9:45:e1"
state = None

""" Custom delegate class to handle notifications from the Thingy:52 """
class NotificationDelegate(btle.DefaultDelegate):
    def __init__(self, obj):
        self.thingyobj = obj

    print("# [THINGYTEMP]: Delegate class called")
    def handleNotification(self, hnd, data):
        print("# [THINGYTEMP]: Got notification")
        if (hnd == thingy52.e_temperature_handle):
            print("Notification: Temperature received: {}".format(repr(data)))
            teptep = binascii.b2a_hex(data)
            print('Notification: Temp received:  {}.{} degCelcius'.format(
                        self._str_to_int(teptep[:-2]), int(teptep[-2:], 16)))

            self.thingyobj._state = self._str_to_int(teptep[:-2])
    
    def _str_to_int(self, s):
        """ Transform hex str into int. """
        i = int(s, 16)
        if i >= 2**7:
            i -= 2**8
        return i 

def setup_platform(hass, config, add_devices, discovery_info=None):
    """ Set up the Thingy 52 temperature sensor"""
    add_devices([Thingy52TempSensor()])


class Thingy52TempSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self):
        """Initialize the sensor."""
        print("#[THINGYTEMP]: Connecting to Thingy with address {}...".format(MAC_ADDRESS))
        self.thingy = thingy52.Thingy52(MAC_ADDRESS)

        # Set delegate, and pass on a reference to self
        self.thingy.setDelegate(NotificationDelegate(self))

        print("#[THINGYTEMP]: Configuring and enabling temperature notification...")
        self.thingy.environment.enable()
        # Temperature update interval 1000ms = 1s
        self.thingy.environment.configure(temp_int=1000)
        # Enable notifications 
        self.thingy.environment.set_temperature_notification(True)

        self._state = 10

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'Thingy52 Temperature'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self.thingy.waitForNotifications(timeout=5)
        print("  # [THINGYTEMP]: method uppdate, state is {}".format(self._state))
        # self._state = state
