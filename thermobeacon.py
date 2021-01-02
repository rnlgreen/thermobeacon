#!/usr/bin/python3 -u
# # This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# thermobeacon.py - Simple bluetooth LE scanner and data extractor

from bluepy.btle import Scanner, DefaultDelegate
from time import strftime

#Enter the MAC address of the sensors
SENSORS = {"02:0d:00:00:08:f3": "Garage" ,"02:0d:00:00:10:85" : "Garage2"}

class DecodeErrorException(Exception):
     def __init__(self, value):
         self.value = value
     def __str__(self):
         return repr(self.value)

class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if isNewDev:
            #print ("Discovered device", dev.addr)
            pass
        elif isNewData:
            #print ("Received new data from", dev.addr)
            pass

def write_temp(where,what,value):
	with open("data.csv", "a") as log:
		log.write("{0}:00,{1},{2},{3}\n".format(strftime("%Y-%m-%d %H:%M"),where,what,value))

#print("Establishing scanner...")
scanner = Scanner().withDelegate(ScanDelegate())
##myConnection = pymysql.connect (host=hostname, user=username, passwd=password, db=database)

print ("-----------------------------------------------------------")

sampled = {}
ReadLoop = True
try:
    while (ReadLoop):
        #print ("Initiating scan...")
        devices = scanner.scan(2.0)

        ManuData = ""
        retry = False

        for dev in devices:
            if dev.addr in SENSORS and not dev.addr in sampled:
                #print ("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))
                CurrentDevAddr = dev.addr
                CurrentDevLoc = SENSORS[dev.addr]
                for (adtype, desc, value) in dev.getScanData():
                    #print ("  %s = %s" % (desc, value))
                    if (desc == "Manufacturer"):
                        ManuData = value

                if (ManuData == ""):
                    print ("No data received, end decoding")
                    continue

                #print (ManuData)
                
                ManuDataHex = []
                for i, j in zip (ManuData[::2], ManuData[1::2]):
                    ManuDataHex.append(int(i+j, 16))

                if not len(ManuDataHex) == 20:
                    print ("Ignoring invalid data length for {}: {}".format(CurrentDevLoc,len(ManuDataHex)))
                    retry = True
                    ReadLoop = True
                    continue

                tempidx = 12
                humidityidx = 14

                TempData = ManuDataHex[tempidx]
                TempData += ManuDataHex[tempidx+1] * 0x100
                TempData = TempData * 0.0625
                if TempData > 4000:
                    TempData = -1 * (4096 - TempData)

                HumidityData = ManuDataHex[humidityidx]
                HumidityData += ManuDataHex[humidityidx+1] * 0x100
                HumidityData = HumidityData * 0.0625

                #print ("Device Address: " + CurrentDevAddr )
                #print ("Device Location: " + CurrentDevLoc )
                print ("Device: {} Temperature: {} Humidity: {}%".format(CurrentDevLoc,TempData,HumidityData))
                write_temp(CurrentDevLoc,"Temperature",TempData)
                write_temp(CurrentDevLoc,"Humidity",HumidityData)
                sampled[CurrentDevAddr] = True
                if not retry:
                    ReadLoop = False
    
except DecodeErrorException:
    print("Decode Exception")
    pass

print ("-----------------------------------------------------------")
