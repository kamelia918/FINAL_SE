import psutil

def cpuinfo():
    # Informations sur la CPU sous forme de dictionnaire
    cpu_info = {
        "CPU Usage": f"{psutil.cpu_percent()}%",
        "CPU Frequency": f"{psutil.cpu_freq().current} MHz",
        "Physical Cores": psutil.cpu_count(logical=False),
        "Logical Cores": psutil.cpu_count(logical=True),
    }
    return cpu_info
