import win32com.client

def discover_bluetooth_devices():
    manager = win32com.client.Dispatch("Bluetooth.DeviceManager")
    devices = manager.DiscoverDevices()

    print("Bluetooth devices in range:")
    for device in devices:
        print(f"Device: {device.Name} ({device.Address})")

if __name__ == "__main__":
    discover_bluetooth_devices()