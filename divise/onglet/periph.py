# # lister tous les périphériques connectés localement à un système Windows
# import wmi

# def get_local_devices():
#     c = wmi.WMI()
#     devices = []
#     for device in c.Win32_PnPEntity():
#         devices.append(device.Name)
#     return devices


import platform

def get_local_devices():
    devices = []
    system = platform.system()

    if system == "Windows":
        import wmi
        c = wmi.WMI()
        for device in c.Win32_PnPEntity():
            devices.append(device.Name)

    elif system == "Linux":
        import pyudev
        context = pyudev.Context()
        for device in context.list_devices(subsystem="usb"):
            devices.append(device.get("ID_MODEL", "Unknown Device"))

    else:
        devices.append("Périphériques non supportés sur ce système")

    return devices

