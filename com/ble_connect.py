9
import bluetooth
from bleak import BleakClient, BleakScanner
import struct
import asyncio
from bleak import BleakScanner
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import position_finding.final as pf

async def discovery():
    devices = await BleakScanner.discover()
    for d in devices:
        print(d, d.name) #, d.details, dir(d))

# to get mac address
# asyncio.run(discovery())

address = "96:66:7C:29:BE:9D" #"96:66:7C:29:BE:9D" # which is the right arduino nano #"F0:6F:5A:3F:50:D3"
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
    "abcd": "cmd"
}
channels_n = {}
channels_w = []
c_data = {}
lp = pf.Lampe((0., 0., 0.), "antela_9w_rgb_cct")
pf.init_position()

async def callback(sender: int, data: bytearray):
    print("\t", channels_n[sender])
    src = channels[channels_n[sender]]
    if src == "cmd":
        val = str(data.decode())
        print(f"Notification3 {src}: {val}")
        if val == "TEST":
            lp.switch()
            print(c_data)
            await loc_client.write_gatt_char(channels_w[0], 'a'.encode())
            print("Send", channels_w[0], 'a'.encode())
        elif val == "end":
            pf.update_pointage()
            pass
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
