import asyncio
import shelve
import threading
from bleak import BleakScanner
from time import strftime, gmtime, sleep


async def scan_for_devices():
    print("Scanning for Bluetooth devices...")
    devices = await BleakScanner.discover()
    for device in devices:
        print(f"Device Name: {device.name}, Address: {device.address}")
    return devices
asyncio.run(scan_for_devices())


KNOWN_DEVICES = {
    "QHM-T1BF": "36:46:3E:F6:1B:FB",
    "GVH5075_59C0": "A4:C1:38:CA:59:C0",
    "N0QTA": "64:16:66:6D:41:91",
}


async def check_for_known_devices():
    devices = await BleakScanner.discover()
    nearby_known_devices = {}
    for device in devices:
        if device.address in KNOWN_DEVICES.values():
            device_name = [name for name, addr in KNOWN_DEVICES.items() if addr == device.address][0]
            print(f"{device_name} is nearby!")
            nearby_known_devices[device_name] = device.address
    return nearby_known_devices


def log_devices(devices):
    with shelve.open( "device_log" ) as db:
        for name, address in devices.items():
            key = name + '_' + address
            formatted_time = strftime( "%Y-%m-%d %H:%M:%S", gmtime())
            if key in db:
                time_list = db[key]
                time_list.append(formatted_time)
                db[key] = time_list
            else:
                db[key] = [formatted_time]
    print( "Logged devices in the shelf database." )


async def scan():
    nearby_devices = await check_for_known_devices()
    if nearby_devices:
        log_devices(nearby_devices)
    else:
        print("No known devices nearby.")


async def clear_logs_periodically():
    while True:
        await asyncio.sleep(3600)
        with shelve.open( "device_log" ) as db:
            db.clear()
        print("Cleared the device log.")


def start_cleanup_thread():
    def runner():
        asyncio.run( clear_logs_periodically() )
    thread = threading.Thread(target=runner, daemon=True)
    thread.start()


def main():
    start_cleanup_thread()
    while True:
        print("Scanning...")
        asyncio.run(scan())
        print("sleeping till next loop...")
        sleep(15)
    print("Verifying log...")
    with shelve.open( "device_log" ) as db:
        for name, address in db.items():
            print(f"{name}: {address}")


if __name__ == '__main__':
    main()

