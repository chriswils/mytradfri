Starting hass with init.d 
====
Just adapted from here https://home-assistant.io/docs/autostart/init.d/

* Copy hass-daemon to /etc/init.d/

* Set it as executable 
`sudo chmod +x /etc/init.d/hass-daemon`

* Change the RUN_AS parameter to your username if changed from homeassistant

Register the daemon
`sudo update-rc.d hass-daemon defaults`

Install the service
`sudo service hass-daemon install`

Restart the machine
`reboot`

Verify everything in `/var/opt/homeassistant/home-assistant.log` if it doesn't start

