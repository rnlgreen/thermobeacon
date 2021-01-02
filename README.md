# thermobeacon
Python script to scan temperatures and humidity from a Thermobeacon, also known as "Wireless Thermometer Hygrometer".

If you have one of these devices:
https://www.amazon.co.uk/Thermometer-Hygrometer-ORIA-Bluetooth-Temperature/dp/B08DL5NN58/ref=sr_1_9?dchild=1&keywords=hygrometer&qid=1609604628&sr=8-9

then this script might be of some interest to you; it scans for all available bluetooth devices, matches the specific device addresses that you provide, then pulls the temperature and humidity from the manufacturer's data, reporting to stdout and writing values to a csv file.

As discussed on this thread: https://www.raspberrypi.org/forums/viewtopic.php?f=91&t=283011

You'll need to install the bluepy Python library (https://pypi.org/project/bluepy/).
