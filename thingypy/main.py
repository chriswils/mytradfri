# Thingy 52 HomeAssistant component
# My thingy mac: D0:C0:1D:B9:45:E1


from bluepy import btle, thingy52
import binascii

MAC_ADDRESS = "d0:c0:1d:b9:45:e1"

print("# Creating new delegate class to handle notifications...")
class NewDelegate(btle.DefaultDelegate):
    def handleNotification(self, hnd, data):
        if (hnd == thingy52.e_temperature_handle):
            print("Notification: Temperature received: {}".format(repr(data)))
        if (hnd == thingy52.ui_button_handle):
            print("Notification: Button press received: {}".format(repr(data)))
            teptep = binascii.b2a_hex(data)
            print('Notification: Temp received:  {}.{} degCelcius'.format(
                        self._str_to_int(teptep[:-2]), int(teptep[-2:], 16)))

print("# Connecting to Thingy with address {}...".format(MAC_ADDRESS))
thingy = thingy52.Thingy52(MAC_ADDRESS)

#print("# Setting notification handler to default handler...")
#thingy.setDelegate(thingy52.MyDelegate())
print("# Setting notification handler to new handler...")
thingy.setDelegate(NewDelegate())

print("# Configuring and enabling temperature notification...")
thingy.environment.enable()
thingy.environment.configure(temp_int=1000)
thingy.environment.set_temperature_notification(True)

print("# Configuring and enabling button press notification...")
thingy.ui.enable()
thingy.ui.set_btn_notification(True)

print("# Waiting for three notifications...")
thingy.waitForNotifications(timeout=5)
thingy.waitForNotifications(timeout=5)
thingy.waitForNotifications(timeout=5)

print("# Disconnecting...")
thingy.disconnect()


