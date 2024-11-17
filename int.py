import socket
import tkinter as tk
from tkinter import ttk
import threading
import platform
import psutil
import json
from queue import Queue
# Configuration du serveur
HOST = '0.0.0.0'
PORT = 44434

# Dictionnaire pour stocker les informations par client
client_data = {}
log_queue = Queue()

# Fonction pour démarrer le serveur
# Fonction pour démarrer le serveur
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    while True:
        client_socket, addr = server_socket.accept()
        try:
            # Lire la longueur des données (10 octets)
            data_length = int(client_socket.recv(10).decode('utf-8').strip())
            
            # Lire les données réelles
            data = b""  
            while len(data) < data_length:
                packet = client_socket.recv(1024)
                if not packet:
                    break
                data += packet
            
            # Décoder les données JSON et les stocker
            if data:
                client_data[str(addr[0])] = json.loads(data.decode('utf-8'))
                update_dropdown()  # Mettre à jour le menu déroulant

                # Envoyer un message dans la queue pour afficher le log
                log_queue.put(f"Client connecté: {addr[0]}")

        except Exception as e:
            log_queue.put(f"Erreur lors du traitement des données de {addr}: {e}")
        
        finally:
            client_socket.close()

# Fonction pour mettre à jour le log texte en lisant depuis la queue
def update_log_text():
    try:
        while not log_queue.empty():
            message = log_queue.get_nowait()
            log_text.config(state='normal')
            log_text.insert(tk.END, message + '\n')
            log_text.config(state='disabled')
    except Exception as e:
        print(f"Erreur dans update_log_text: {e}")
    
    root.after(100, update_log_text)  # Planifier la mise à jour suivante

import wmi

def get_local_devices():
    c = wmi.WMI()
    devices = []
    for device in c.Win32_PnPEntity():
        devices.append(device.Name)
    return devices


# Fonction pour obtenir les informations système locales
def get_local_info():
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
        f"CPU Usage: {psutil.cpu_percent()}%\n"
        f"CPU Frequency: {psutil.cpu_freq().current} MHz\n"
        f"Physical Cores: {psutil.cpu_count(logical=False)}\n"
        f"Logical Cores: {psutil.cpu_count(logical=True)}"
    )

    # Informations sur les disques
    disks = []
    for partition in psutil.disk_partitions():
        usage = psutil.disk_usage(partition.mountpoint)
        disks.append({
            "device": partition.device,
            "total": usage.total // (1024 ** 3),  # Convertir en GB
            "used": usage.used // (1024 ** 3),    # Convertir en GB
            "free": usage.free // (1024 ** 3),    # Convertir en GB
            "filesystem": partition.fstype
        })
    devices = get_local_devices()
    # Informations système
    info = {
        "infoG": (
            f"Système: {platform.system()}\n"
            f"Version: {platform.version()}\n"
            f"Machine: {platform.node()}\n"
            f"Structure: {platform.machine()}\n"
            f"Processeur: {platform.processor()}\n"
            f"Dernier démarrage: {psutil.boot_time()}\n"
            f"Niveau de batterie: {battery_info}\n"
            f"État de charge: {is_charging}\n"
            f"Utilisateur: {psutil.users()[0].name if psutil.users() else 'Non disponible'}"
        ),
        "CPU": cpu_info,
        "Memory": memory_info,
        "Disks": disks,  # Ajout de la liste des disques
        "Devices": devices  # Ajout des périphériques locaux
    }
    return info
def get_active_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = proc.info
            processes.append((info['pid'], info['name'], info['cpu_percent'], info['memory_percent']))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return processes


def update_process_table():
    selected_pc = dropdown.get()
    if selected_pc == "Serveur":
        processes = get_active_processes()
    else:
        processes = client_data.get(selected_pc, {}).get("Processes", [])
    
    process_table.delete(*process_table.get_children())
    for pid, name, cpu, memory in processes:
        process_table.insert("", "end", values=(pid, name, f"{cpu:.2f}%", f"{memory:.2f}%"))
    
    # Rafraîchir automatiquement si on est sur l'onglet "Serveur"
    if selected_pc == "Serveur":
        root.after(1000, update_process_table)



# Fonction pour mettre à jour le menu déroulant
def update_dropdown():
    dropdown["values"] = ["Serveur"] + list(client_data.keys())
    dropdown.set("Serveur")

# Fonction pour afficher les informations sélectionnées dans les onglets
def show_info(event=None):
    selected_pc = dropdown.get()
    if selected_pc == "Serveur":
        data = get_local_info()  # Récupère les infos locales pour le serveur
        processes = get_active_processes()  # Récupère les processus
    else:
        data = client_data.get(selected_pc, {})  # Récupère les infos du client
        processes = data.get("Processes", [])

    # Mise à jour des informations dans chaque onglet
    infoG_info.config(state='normal')
    infoG_info.delete(1.0, tk.END)
    infoG_info.insert(tk.END, data.get("infoG", "Pas de données"))
    infoG_info.config(state='disabled')

    cpu_info.config(state='normal')
    cpu_info.delete(1.0, tk.END)
    cpu_info.insert(tk.END, data.get("CPU", "Pas de données"))
    cpu_info.config(state='disabled')

    memory_info.config(state='normal')
    memory_info.delete(1.0, tk.END)
    memory_info.insert(tk.END, data.get("Memory", "Pas de données"))
    memory_info.config(state='disabled')

    # Mise à jour de la table des disques
    disk_table.delete(*disk_table.get_children())
    for disk in data.get("Disks", []):
        disk_table.insert("", "end", values=(disk["device"], f"{disk['total']} GB", f"{disk['used']} GB", f"{disk['free']} GB", disk["filesystem"]))

    # Mise à jour de la table des processus
    process_table.delete(*process_table.get_children())
    for pid, name, cpu, memory in processes:
        process_table.insert("", "end", values=(pid, name, f"{cpu:.2f}%", f"{memory:.2f}%"))
    
    # Mise à jour de l'onglet Périphériques
    devices_list.config(state='normal')
    devices_list.delete(1.0, tk.END)
    devices = data.get("Devices", ["Pas de données"])
    devices_list.insert(tk.END, "\n".join([device for device in devices if device]))  # Filtrer les None

    devices_list.config(state='disabled')


# Fonction pour rafraîchir les données
def refresh_data():
    update_dropdown()
    update_process_table()
    show_info()

# Création de l'interface utilisateur principale
root = tk.Tk()
root.title("Serveur de Communication avec Sélection")

# Menu déroulant pour sélectionner la machine
dropdown_label = tk.Label(root, text="Sélectionnez une machine :")
dropdown_label.pack()
dropdown = ttk.Combobox(root, state="readonly")
dropdown.pack()
dropdown.bind("<<ComboboxSelected>>", show_info)

# Zone de texte pour afficher les logs
log_text = tk.Text(root, height=1)
log_text.pack(fill=tk.BOTH, expand=False)

# Bouton de rafraîchissement
refresh_button = tk.Button(root, text="Rafraîchir", command=refresh_data)
refresh_button.pack()

# Création des onglets
tab_control = ttk.Notebook(root)

# Onglet infoG
infoG_tab = ttk.Frame(tab_control)
tab_control.add(infoG_tab, text='Informations générales')
infoG_info = tk.Text(infoG_tab, width=60, height=10)
infoG_info.pack(fill=tk.BOTH, expand=True)
infoG_info.config(state='disabled')  # Rendre la zone de texte non modifiable

# Onglet CPU
cpu_tab = ttk.Frame(tab_control)
tab_control.add(cpu_tab, text='CPU')
cpu_info = tk.Text(cpu_tab, width=60, height=10)
cpu_info.pack(fill=tk.BOTH, expand=True)
cpu_info.config(state='disabled')  # Rendre la zone de texte non modifiable

# Onglet Mémoire
memory_tab = ttk.Frame(tab_control)
tab_control.add(memory_tab, text='Mémoire')
memory_info = tk.Text(memory_tab, width=60, height=10)
memory_info.pack(fill=tk.BOTH, expand=True)
memory_info.config(state='disabled')  # Rendre la zone de texte non modifiable


# Onglet Disque avec table
disk_tab = ttk.Frame(tab_control)
tab_control.add(disk_tab, text='Disque')
disk_table = ttk.Treeview(disk_tab, columns=("Device", "Total", "Used", "Free", "File System"), show='headings')
disk_table.heading("Device", text="Device")
disk_table.heading("Total", text="Total (GB)")
disk_table.heading("Used", text="Used (GB)")
disk_table.heading("Free", text="Free (GB)")
disk_table.heading("File System", text="File System")
disk_table.pack(fill=tk.BOTH, expand=True)

process_tab = ttk.Frame(tab_control)
tab_control.add(process_tab, text='Processus')
process_table = ttk.Treeview(process_tab, columns=("PID", "Nom", "CPU", "Mémoire"), show='headings')
process_table.heading("PID", text="PID")
process_table.heading("Nom", text="Nom")
process_table.heading("CPU", text="CPU (%)")
process_table.heading("Mémoire", text="Mémoire (%)")
process_table.pack(fill=tk.BOTH, expand=True)



# Onglet Périphériques
devices_tab = ttk.Frame(tab_control)
tab_control.add(devices_tab, text='Périphériques')
devices_list = tk.Text(devices_tab, width=60, height=10)
devices_list.pack(fill=tk.BOTH, expand=True)
devices_list.config(state='disabled')  # Rendre la zone de texte non modifiable


# Afficher les onglets
tab_control.pack(expand=1, fill='both')

# Démarrage du serveur dans un thread
server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

# Appel initial pour afficher les informations sans appuyer sur "Rafraîchir"
refresh_data()

# Lancement de l'interface graphique
root.mainloop()
