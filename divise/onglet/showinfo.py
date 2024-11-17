
import tkinter as tk
from onglet.memory import memoryinfo 
from onglet.cpu import cpuinfo
from onglet.disk import diskinfo
from onglet.periph import get_local_devices
from onglet.infoG import generalinfo
from onglet.processus import get_active_processes
from onglet.globals import client_data  # Assuming client_data is defined globally in another file

# Fonction pour obtenir les informations système locales
def get_local_info():
   
    # Informations système
    info = {
        "infoG":generalinfo(),
        "CPU": cpuinfo(),
        "Memory": memoryinfo(),
        "Devices": get_local_devices()  # les périphériques locaux
    }
    return info

    


# Fonction pour afficher les informations sélectionnées dans les onglets
def show_info(selected_pc, infoG_info, cpu_info, memory_info, disk_table, process_table, devices_list):
    if selected_pc == "Serveur":
        data = get_local_info()  # Get local server info
        processes = get_active_processes()  # Get active processes
    else:
        data = client_data.get(selected_pc, {})  # Get client info
        processes = data.get("Processes", [])

    # Update General Info tab
    infoG_info.config(state='normal')# Permet l'édition temporaire
    infoG_info.delete(1.0, tk.END)# Efface le contenu actuel
    
    # Définir un style pour le texte en gras
    infoG_info.tag_config("bold", font=("Arial", 15, "bold"))   # Style gras
    infoG_info.tag_config("normal", font=("Arial", 13))        # Style normal

    # Ajouter les informations avec leur style
    for key, value in data["infoG"].items():
        
        infoG_info.insert(tk.END, f"{key}: ", "bold")  # Texte clé en gras
        infoG_info.insert(tk.END, f"{value}\n","normal")  # Texte valeur en normal

    infoG_info.config(state='disabled')  # Rendre la zone non modifiable




    # Update CPU Info tab
    cpu_info.config(state='normal')
    cpu_info.delete(1.0, tk.END)

    # Définir un style pour le texte en gras
    cpu_info.tag_config("bold", font=("Arial", 15, "bold"))   # Style gras
    cpu_info.tag_config("normal", font=("Arial", 13))        # Style normal

    # Ajouter les informations avec leur style
    for key, value in data["CPU"].items():
        
        cpu_info.insert(tk.END, f"{key}: ", "bold")  # Texte clé en gras
        cpu_info.insert(tk.END, f"{value}\n","normal")  # Texte valeur en normal

    cpu_info.config(state='disabled')      # Rendre la zone non modifiable

    # Update Memory Info tab
    memory_info.config(state='normal')
    memory_info.delete(1.0, tk.END)
    # Définir un style pour le texte en gras
    memory_info.tag_config("bold", font=("Arial", 15, "bold"))   # Style gras
    memory_info.tag_config("normal", font=("Arial", 13))        # Style normal

    # Ajouter les informations avec leur style
    for key, value in data["Memory"].items():
        
        memory_info.insert(tk.END, f"{key}: ", "bold")  # Texte clé en gras
        memory_info.insert(tk.END, f"{value}\n","normal")  # Texte valeur en normal

    memory_info.config(state='disabled')

    # Update Disk Info tab
    disk_table.delete(*disk_table.get_children())  # Clear all existing rows
    disks = diskinfo()  # Get disk information
    for disk in disks:
        disk_table.insert("", "end", values=disk)  # Insert each disk as a row

    # Update Process Info tab
    process_table.delete(*process_table.get_children())
    for pid, name, cpu, memory in processes:
        process_table.insert("", "end", values=(pid, name, f"{cpu:.2f}%", f"{memory:.2f}%"))

    # Update Devices Info tab
    devices_list.config(state='normal')
    devices_list.delete(1.0, tk.END)
    devices = data.get("Devices", ["Pas de données"])
    devices_list.insert(tk.END, "\n".join([device for device in devices if device]))
    devices_list.config(state='disabled')


