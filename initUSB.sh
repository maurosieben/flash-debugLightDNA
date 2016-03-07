#! /bin/bash

cp LightDNAProgrammer.rules /etc/udev/rules.d/
chmod a+r /etc/udev/rules.d/LightDNAProgrammer.rules
udevadm control --reload-rules
service udev restart
udevadm trigger
