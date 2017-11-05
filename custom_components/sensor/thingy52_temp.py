"""
    HomeAssistant: Thingy52 temperature sensor

    This sensor device is taking data from the Nordic Thingy:52 IoT Sensor Platform.
    It is derived from HA example sensor; https://home-assistant.io/developers/platform_example_sensor/
    and uses bluepy's Thingy:52 implementation. More docs on this and snippets used in this file is 
    found at Nordic Semiconductor's devzone blog:
    https://devzone.nordicsemi.com/blogs/1162/nordic-thingy52-raspberry-pi-python-interface/
    
    BATTERY_SERVICE_UUID = 0x180F
    BATTERY_LEVEL_UUID = 0x2A19

    def Nordic_UUID(val):
        # Adds base UUID and inserts value to return Nordic UUID
        return UUID("EF68%04X-9B35-4933-9B10-52FFA9740042" % val)

    batteryServiceUUID = Nordic_UUID(BATTERY_SERVICE_UUID) 
    battery_charUUID = NORDIC_UUID(BATTERY_LEVEL_UUID)
    getCharacteristic...
    battery_char = self.environment_service.getCharacteristics(self.batteryServiceUUID)[0]
    battery_handle = self.battery_char.getHandle()
    battery_cccd = self.battery_char.getDescriptors(forUUID=CCCD_UUID)[0]

    def set_battery_notification(self, state):
        if self.battery_cccd is not None:
            if state == True:
                self.battery_cccd.write(b"\x01\x00", True)
            else:
                self.battery_cccd.write(b"\x00\x00", True)



"""

from homeassistant.const import TEMP_CELSIUS, CONF_MAC
from homeassistant.helpers.entity import Entity
from bluepy import btle, thingy52
import binascii

# DEPENDENCIES = ['libglib2.0-dev']
# REQUIREMENTS = ['bluepy']

# Definition of all UUID used by Thingy
CCCD_UUID = 0x2902

CONF_SENSORS = 'sensors'
CONF_TEMP = 'temp'
CONF_HUMID = 'humid'

SENSOR_UNITS = {
    "humidity": '%',
    "temperature" : TEMP_CELSIUS,
    "gas": 'ppm',
    "pressure": 'hPA',
    "battery": '%'
}


""" Custom delegate class to handle notifications from the Thingy:52 """
class NotificationDelegate(btle.DefaultDelegate):
    def __init__(self, sensors):
        self.thingysensors = {}
        for s in sensors:
            self.thingysensors[s._name] = s

    print("# [THINGYSENSOR]: Delegate class called")
    def handleNotification(self, hnd, data):
        print("# [THINGYSENSOR]: Got notification")
        if (hnd == thingy52.e_temperature_handle):
            teptep = binascii.b2a_hex(data)
            print('Notification: Temp received:  {}.{} degCelcius'.format(
                        self._str_to_int(teptep[:-2]), int(teptep[-2:], 16)))
            tempinteg = self._str_to_int(teptep[:-2])
            tempdec = int(teptep[-2:], 16)

            div = 100 if((int(teptep[-2:], 16) / 10) > 1.0) else 10
            print("Setting state for {}".format(self.thingysensors["temperature"]._name))
            self.thingysensors["temperature"]._state = (tempinteg + (tempdec / div))   
        
        elif (hnd == thingy52.e_humidity_handle):
            teptep = binascii.b2a_hex(data)
            print('Notification: Humidity received: {} %'.format(
                self._str_to_int(teptep)))
            
            print("Setting state for {}".format(self.thingysensors["humidity"]._name))
            self.thingysensors["humidity"]._state = self._str_to_int(teptep)

        elif (hnd == thingy52.e_pressure_handle):
            pressure_int, pressure_dec = self._extract_pressure_data(data)
            print('Notification: Press received: {}.{} hPa'.format(
                        pressure_int, pressure_dec))

            div = 100 if( (pressure_dec / 10) > 1.0) else 10
            self.thingysensors["pressure"]._state = pressure_int + (pressure_dec/div)

        elif (hnd == thingy52.e_gas_handle):
            eco2, tvoc = self._extract_gas_data(data)
            print(
                'Notification: Gas received: eCO2 ppm: {}, TVOC ppb: {} %'.format(eco2, tvoc))
            self.thingysensors["gas"]._state = eco2
    
    def _extract_pressure_data(self, data):
        """ Extract pressure data from data string. """
        teptep = binascii.b2a_hex(data)
        pressure_int = 0
        for i in range(0, 4):
                pressure_int += (int(teptep[i*2:(i*2)+2], 16) << 8*i)
        pressure_dec = int(teptep[-2:], 16)
        return (pressure_int, pressure_dec)

    def _extract_gas_data(self, data):
        """ Extract gas data from data string. """
        teptep = binascii.b2a_hex(data)
        eco2 = int(teptep[:2], 16)) + (int(teptep[2:4], 16) << 8)
        tvoc = int(teptep[4:6], 16) + (int(teptep[6:8], 16) << 8)
        return eco2, tvoc

    def _str_to_int(self, s):
        """ Transform hex str into int. """
        i = int(s, 16)
        if i >= 2**7:
            i -= 2**8
        return i 

def setup_platform(hass, config, add_devices, discovery_info=None):
    """ Set up the Thingy 52 temperature sensor"""
    global e_battery_handle
    mac_address = config.get(CONF_MAC)
    environments = config.get(CONF_SENSORS)
    sensors = []
    print("#[THINGYSENSOR]: Connecting to Thingy with address {}...".format(mac_address))
    thingy = thingy52.Thingy52(mac_address)


    print("#[THINGYSENSOR]: Configuring and enabling environment notifications...")
    thingy.environment.enable()

    # Enable notifications for enabled services
    # Update interval 1000ms = 1s
    if "temperature" in environments:
        print("Enabling notification for temperature")
        thingy.environment.set_temperature_notification(True)
        thingy.environment.configure(temp_int=1000)
    if "humidity" in environments:
        print("Enabling notification for humidity")
        thingy.environment.set_humidity_notification(True)
        thingy.environment.configure(humid_int=1000)
    if "gas" in environments:
        thingy.environment.set_gas_notification(True)
        # 1 = 1 s interval
        # 2 = 10 s interval
        # 3 = 60 s interval
        thingy.environment.configure(gas_mode_int=1)
    if "pressure" in environments:
        thingy.environment.set_pressure_notification(True)
        thingy.environment.configure(press_int=1000)
    if "battery" in environments:
        thingy.battery.enable()
        e_battery_handle = thingy.battery.battery_char.getHandle()
        battery_cccd = thingy.battery.battery_char.getDescriptors(forUUID=CCCD_UUID)[
            0]
        battery_ccd.write(b"\x01\x00", True)
    

    for sensorname in environments:
        print("Adding sensor: {}".format(sensorname))
        sensors.append(Thingy52Sensor(thingy, sensorname, SENSOR_UNITS[sensorname]))
    
    add_devices(sensors)
    thingy.setDelegate(NotificationDelegate(sensors))

class Thingy52Sensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, thingy, name, unit_measurement=TEMP_CELSIUS):
        """Initialize the sensor."""
        self._thingy = thingy
        self._name = name
        self._state = None
        self._unit_measurement = unit_measurement
        

    @property
    def name(self):
        """Return the name of the sensor."""
        return ("Thingy52: " + self._name)

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_measurement

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        if(self._name == "battery"):
                self._state = self._thingy.battery.read()
        else:
            self._thingy.waitForNotifications(timeout=5)
            print("# [{}]: method update, state is {}".format(self._name, self._state))

        # self._state = state

if (__name__ == "__main__"):
    setup_platform()
