9
import bluetooth
from bleak import BleakClient, BleakScanner
import struct
import asyncio
from bleak import BleakScanner
import sys, os
from ahrs.filters.madgwick import Madgwick
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import position_finding.final as pff
import position_finding.wiimote as pfw

async def discovery():
    devices = await BleakScanner.discover()
    for d in devices:
        print(d, d.name) #, d.details, dir(d))

# to get mac address
# asyncio.run(discovery())

address = "F0:6F:5A:3F:50:D3"#"96:66:7C:29:BE:9D" #"96:66:7C:29:BE:9D" # which is the right arduino nano #"F0:6F:5A:3F:50:D3"
channels = {
    "a001": "acc_x",
    "a002": "acc_y",
    "a003": "acc_z",
    "b001": "gyr_x",
    "b002": "gyr_y",
    "b003": "gyr_z",
    "c001": "mag_x",
    "c002": "mag_y",
    "c003": "mag_z",
    "d001": "heading",
    "abcd": "cmd"
}
channels_n = {}
channels_w = []
c_data = {}
lp = pff.Lampe((0., 0., 0.), "antela_9w_rgb_cct")
enc = pff.Speaker((0., 0., 0.))
pfw.init_position()
pfw.start_proc()
#enc.connect()

import math
 
def euler_from_quaternion(x, y, z, w):
        """
        Convert a quaternion into euler angles (roll, pitch, yaw)
        roll is rotation around x in radians (counterclockwise)
        pitch is rotation around y in radians (counterclockwise)
        yaw is rotation around z in radians (counterclockwise)
        """
        t0 = +2.0 * (w * x + y * z)
        t1 = +1.0 - 2.0 * (x * x + y * y)
        roll_x = math.atan2(t0, t1)
     
        t2 = +2.0 * (w * y - z * x)
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch_y = math.asin(t2)
     
        t3 = +2.0 * (w * z + x * y)
        t4 = +1.0 - 2.0 * (y * y + z * z)
        yaw_z = math.atan2(t3, t4)
     
        return roll_x * 180. / np.pi, pitch_y * 180. / np.pi, yaw_z * 180. / np.pi# in radians

def compute_heading():
    try:
        print(c_data["gyr_x"])
        print(np.array([[c_data["gyr_x"][0], c_data["gyr_y"][0], c_data["gyr_z"][0]]]))
        madgwick = Madgwick(gyr=np.array([[c_data["gyr_x"][0], c_data["gyr_y"][0], c_data["gyr_z"][0]]]),
                            acc=np.array([[c_data["acc_x"][0], c_data["acc_y"][0], c_data["acc_z"][0]]]),
                            mag=np.array([[c_data["mag_x"][0], c_data["mag_y"][0], c_data["mag_z"][0]]])) # frequency  Hz?
        print(madgwick.Q)
        print(euler_from_quaternion(madgwick.Q[0][0], madgwick.Q[0][1], madgwick.Q[0][2], madgwick.Q[0][3]))

        # pitch = 180 * atan (accelerationX/sqrt(accelerationY*accelerationY + accelerationZ*accelerationZ))/M_PI;
#roll = 180 * atan (accelerationY/sqrt(accelerationX*accelerationX + accelerationZ*accelerationZ))/M_PI;
        # yaw = 180 * atan (accelerationZ/sqrt(accelerationX*accelerationX + accelerationZ*accelerationZ))/M_PI;

        yaw = 180. / np.pi * np.arctan(c_data["acc_z"][0]/np.sqrt(c_data["acc_x"][0]**2+c_data["acc_z"][0]**2))
        print(yaw)

    except Exception as ee:
        print("Erreurs", c_data)
        print(ee)

async def callback(sender: int, data: bytearray):
    print("\t", channels_n[sender])
    src = channels[channels_n[sender]]
    if src == "cmd":
        val = str(data.decode())
        print(f"Notification STR {src}: {val}")
        if val == "TEST":
            #pfw.update_pointage()
            print(pfw.last_pos)
            lp.switch()
            print(c_data)
            await loc_client.write_gatt_char(channels_w[0], 'a'.encode())
            print("Send", channels_w[0], 'a'.encode())
            compute_heading()        
        elif val == "end":
            print(pfw.last_pos)
            #pfw.update_pointage()
            pass
        elif val == "POSI":
            print(pfw.last_pos)
            pass
            #pfw.update_pointage()
        elif val == "LMPE":
            print(pfw.last_pos)
            lp.switch()
        elif val == "PNTE":
            print(pfw.last_pos)
            print("POINTAGE")
            enc.play()
    else:
        val = struct.unpack('f', data)
        print(f"Notification {src}: {val}")
        c_data[src] = val
    #except:
    #    try:
    #        k_int = int.from_bytes(data, byteorder='big')
    #       if (k_int > 1000000):
    #            raise Exception()
    #       print(f"Notification2 {src}: {k_int}")
    #    except:
    #        val = str(data.decode())
    #        print(f"Notification3 {src}: {val}")
    #        if val == "TEST":
    #            print(c_data)

loc_client = None

async def main(address):
    global loc_client
    async with BleakClient(address) as client:
        loc_client = client
        services = await client.get_services()
        for service in services:
            print(service)
            for c in service.characteristics:
                try:
                    await client.start_notify(c.uuid, callback) # should see abce
                    channels_n[c.handle] = c.uuid[4:8]
                except:
                    channels_w.append(c.uuid)
                    pass
                    #print("Writing")
                print("\t", c)

        print(channels)
        print(channels_n)

        #model_number = await client.read_gatt_char(char_specifier)
        #print("Model Number: {0}".format(int.from_bytes(model_number, byteorder="big")))

        while client.is_connected:
            await asyncio.sleep(1)

asyncio.run(main(address))
