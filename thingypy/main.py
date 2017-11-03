# Thingy 52 HomeAssistant component
# My thingy mac: D0:C0:1D:B9:45:E1


from bluepy import btle, thingy52
import binascii

MAC_ADDRESS = "d0:c0:1d:b9:45:e1"

print("# Creating new delegate class to handle notifications...")
class NotificationDelegate(btle.DefaultDelegate):
    def __init__(self, obj):
        self.thingyobj = obj

    def handleNotification(self, hnd, data):
        if (hnd == thingy52.e_temperature_handle):
            print("Notification: Temperature received: {}".format(repr(data)))
            teptep = binascii.b2a_hex(data)
            print('Notification: Temp received:  {}.{} degCelcius'.format(
                        self._str_to_int(teptep[:-2]), int(teptep[-2:], 16)))
            
            self.thingyobj._state = self._str_to_int(teptep[:-2]), int(teptep[-2:], 16))

        if (hnd == thingy52.ui_button_handle):
            print("Notification: Button press received: {}".format(repr(data)))
    
    def _str_to_int(self, s):
        """ Transform hex str into int. """
        i = int(s, 16)
        if i >= 2**7:
            i -= 2**8
        return i 

class StartAndTest():
    def __init__():
        self._state = None

        print("# Connecting to Thingy with address {}...".format(MAC_ADDRESS))
        self.thingy = thingy52.Thingy52(MAC_ADDRESS)

        #print("# Setting notification handler to default handler...")
        #thingy.setDelegate(thingy52.MyDelegate())
        print("# Setting notification handler to new handler...")

        self.thingy.setDelegate(NotificationDelegate(), self)

        print("# Configuring and enabling temperature notification...")
        self.thingy.environment.enable()
        self.thingy.environment.configure(temp_int=1000)
        self.thingy.environment.set_temperature_notification(True)

        print("# Configuring and enabling button press notification...")
        self.thingy.ui.enable()
        self.thingy.ui.set_btn_notification(True)

    def waitfordata(self):
        print("# Waiting for three notifications...")
        self.thingy.waitForNotifications(timeout=5)
        print("Internal state")
        print(self._state)
        self.thingy.waitForNotifications(timeout=5)
        print("Internal state")
        print(self._state)
        self.thingy.waitForNotifications(timeout=5)
        print("Internal state")
        print(self._state)
    
    def disconnect(self):
        print("# Disconnecting...")
        self.thingy.disconnect()


if (__name__ is "__main__"):
    t = StartAndTest()
    t.waitfordata()
    t.disconnect()
