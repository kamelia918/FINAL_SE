import os
import sys
import socket
import psutil
import platform
import json
import time
from pathlib import Path

# Configuration du serveur
SERVER_HOST = '127.0.0.1'  # Remplacez par l'adresse IP du serveur
SERVER_PORT = 44434

def get_connected_devices():
    if platform.system() == "Windows":
        try:
            import wmi
            c = wmi.WMI()
            devices = [device.Name for device in c.Win32_PnPEntity() if device.Name]
            return devices
        except Exception as e:
            print(f"Erreur lors de la récupération des périphériques sous Windows : {e}")
            return ["Erreur lors de la récupération des périphériques"]
    elif platform.system() == "Linux":
        try:
            devices = os.listdir('/dev')
            return devices
        except Exception as e:
            print(f"Erreur lors de la récupération des périphériques sous Linux : {e}")
            return ["Erreur lors de la récupération des périphériques"]
    else:
        return ["Système non supporté pour la récupération des périphériques"]

# Fonction pour obtenir les informations système du client
def get_system_info():
    # Informations sur la batterie
    battery = psutil.sensors_battery()
    battery_info = f"{battery.percent}%" if battery else "Non disponible"
    is_charging = "En charge" if battery and battery.power_plugged else "Pas en charge"

    # Informations sur la mémoire
    memory = psutil.virtual_memory()
    memory_info = (
        f"Memory Usage: {memory.percent}%\n"
        f"Total RAM: {memory.total // (1024 ** 2)} MB\n"
        f"Used RAM: {memory.used // (1024 ** 2)} MB\n"
        f"Free RAM: {memory.free // (1024 ** 2)} MB"
    )

    # Informations CPU
    cpu_info = (
        f"CPU Usage: {psutil.cpu_percent(interval=1)}%\n"
        f"CPU Frequency: {psutil.cpu_freq().current if psutil.cpu_freq() else 'Non disponible'} MHz\n"
        f"Physical Cores: {psutil.cpu_count(logical=False)}\n"
        f"Logical Cores: {psutil.cpu_count(logical=True)}"
    )

    # Informations sur les disques
    disks = []
    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append({
                "device": partition.device,
                "total": usage.total // (1024 ** 3),  # Convertir en GB
                "used": usage.used // (1024 ** 3),    # Convertir en GB
                "free": usage.free // (1024 ** 3),    # Convertir en GB
                "filesystem": partition.fstype
            })
        except PermissionError:
            continue

    # Processus actifs
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = proc.info
            processes.append((info['pid'], info['name'], info['cpu_percent'], info['memory_percent']))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    # Récupérer les périphériques
    devices = get_connected_devices()

    # Informations système
    info = {
        "infoG": (
            f"Système: {platform.system()}\n"
            f"Version: {platform.version()}\n"
            f"Machine: {platform.node()}\n"
            f"Structure: {platform.machine()}\n"
            f"Processeur: {platform.processor()}\n"
            f"Niveau de batterie: {battery_info}\n"
            f"État de charge: {is_charging}\n"
        ),
        "CPU": cpu_info,
        "Memory": memory_info,
        "Disks": disks,
        "Processes": processes,
        "Devices": devices
    }
    return json.dumps(info)

# Fonction pour envoyer les informations au serveur
def send_data():
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_HOST, SERVER_PORT))

        system_info = get_system_info()
        data = system_info.encode('utf-8')

        data_length = len(data)
        client_socket.sendall(f"{data_length:<10}".encode('utf-8'))  # Préfixe de 10 octets pour la longueur
        client_socket.sendall(data)
        print("Données envoyées au serveur :", system_info)

        client_socket.close()
    except ConnectionRefusedError:
        print("Connexion au serveur refusée. Assurez-vous que le serveur est en marche.")
    except Exception as e:
        print("Erreur lors de l'envoi des données :", e)

# Fonction pour exécuter le script au démarrage
def add_to_startup():
    if platform.system() == "Windows":
        script_path = os.path.realpath(sys.argv[0])
        startup_folder = Path.home() / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup"
        bat_script_path = startup_folder / "client_script.bat"
        bat_script_content = f'@echo off\npythonw "{script_path}"\n'
        with open(bat_script_path, 'w') as bat_file:
            bat_file.write(bat_script_content)
        print(f"Script ajouté au démarrage Windows : {bat_script_path}")
    elif platform.system() == "Linux":
        # Crée une tâche cron
        cron_job = f"@reboot python3 {os.path.realpath(sys.argv[0])}\n"
        with open("/etc/crontab", "a") as crontab:
            crontab.write(cron_job)
        print("Script ajouté au démarrage Linux via cron.")
    else:
        print("Ajout au démarrage non supporté pour ce système.")

# Fonction principale
def main():
    if platform.system() != "Linux":
        add_to_startup()  # Ne fonctionne qu'avec les permissions root sous Linux
    while True:
        send_data()
        time.sleep(10)

if __name__ == '__main__':
    main()
