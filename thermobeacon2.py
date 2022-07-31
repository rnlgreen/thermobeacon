#!/usr/bin/python3
from bluepy import btle # pylint: disable=import-error

#Transmit Handle 0x0021
TX_CHAR_UUID = btle.UUID('0000fff5-0000-1000-8000-00805F9B34FB')
#Read Handle 0x0024
RX_CHAR_UUID = btle.UUID('0000fff3-0000-1000-8000-00805F9B34FB')

#Function to return a byte array as zero padded, space separated, hex values
def convert_to_text(results):
    hex_results = []
    for v in range(len(results)):
        hex_results.append("{:x}".format(results[v]).zfill(2))
    return " ".join(hex_results)

#Function to send a string to the device as a bytearray and return the results received
def write_bytes(vals):
    write_val = bytearray.fromhex(vals)
    tx.write(write_val)
    read_val = rx.read()
    return read_val

#Function to convert the readings we get back into temperatures and humidities
def convert_to_readings(response):
    readings = []
    for v in range(6):
        results_position = 6 + (v * 2)
        reading = int.from_bytes(response[results_position:results_position+2],byteorder='little')
        reading = reading * 0.0625
        if reading > 2048:
            reading = -1 * (4096-reading)
        readings.append("{:.2f}".format(reading))
    print(",".join(readings))

SENSORS = {"02:0d:00:00:08:f3": "Loft" ,"02:0d:00:00:10:85" : "Study"}

for sensor in SENSORS:
    #Connect to the device
    print("Connecting...")
    connected = False
    tries = 0
    while not connected and tries < 5:
        try:
            dev = btle.Peripheral(sensor)
            connected = True
        except:
            #print ("Failed to connect to",SENSORS[sensor])
            tries += 1
    if connected:
        #Get handles to the transmit and receieve characteristics
        tx = dev.getCharacteristics(uuid=TX_CHAR_UUID)[0]
        rx = dev.getCharacteristics(uuid=RX_CHAR_UUID)[0]

        #Send initial command to get the number of available data points
        response = write_bytes("0100000000")
        #The number of available values is stored in the second and third bytes of the response, little endian order
        available = int.from_bytes(response[1:3], byteorder='little')

        print ("There are {} available data points from this device ({})".format(available,SENSORS[sensor]))

        try:
            #Data is returned as three pairs of temperature and humidity values
            for data_point in range(int(available / 3)):
                index = data_point * 3
                #print index for reference
                print(str(index).zfill(4),": ",end='')
                #convert index to hex, padded with leading zeroes
                index_hex = hex(index)[2:].zfill(4)
                #reverse the byte order of the hex values
                index_hex_reversed = index_hex[2:] + index_hex[0:2]
                #build the request string to be sent to the device
                hex_string = "07" + index_hex_reversed + "000003"
                #send the request and get the response
                response = write_bytes(hex_string)
                #Print the response as text
                print(convert_to_text(response))
                #convert the response to temperature and humidity readings
                convert_to_readings(response)
            dev.disconnect()
        except:
            pass
