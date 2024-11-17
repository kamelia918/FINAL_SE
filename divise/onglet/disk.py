import psutil

# def diskinfo():
#     disks = []
#     for partition in psutil.disk_partitions():
#         usage = psutil.disk_usage(partition.mountpoint)
#         disks.append({
#             "device": partition.device,
#             "total": usage.total // (1024 ** 3),  
#             "used": usage.used // (1024 ** 3),    
#             "free": usage.free // (1024 ** 3),    
#             "filesystem": partition.fstype
#         })
    
#     return disks
    

def diskinfo():
    import psutil
    disks = []
    for partition in psutil.disk_partitions():
        usage = psutil.disk_usage(partition.mountpoint)
        disks.append((
            partition.device,
            f"{usage.total / (1024 ** 3):.2f} GB",
            f"{usage.used / (1024 ** 3):.2f} GB",
            f"{usage.free / (1024 ** 3):.2f} GB",
            partition.fstype
        ))
    return disks
