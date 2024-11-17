import psutil

def memoryinfo():
    # Informations sur la mémoire sous forme de dictionnaire
    memory = psutil.virtual_memory()
    memory_info = {
        "Memory Usage": f"{memory.percent}%",
        "Total RAM": f"{memory.total / (1024 ** 3):.2f} GB",
        "Used RAM": f"{memory.used / (1024 ** 3):.2f} GB",
        "Free RAM": f"{memory.free / (1024 ** 3):.2f} GB",
    }
    return memory_info
