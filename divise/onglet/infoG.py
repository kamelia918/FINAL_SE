# import psutil
# import platform


# # Informations sur la batterie
# battery = psutil.sensors_battery()
# battery_info = f"{battery.percent}%" if battery else "Non disponible"
# is_charging = "En charge" if battery and battery.power_plugged else "Pas en charge"


# def generalinfo():
#     # Informations generales
#     infoG = (
#             f"Système: {platform.system()}\n"
#             f"Version: {platform.version()}\n"
#             f"Machine: {platform.node()}\n"
#             f"Structure: {platform.machine()}\n"
#             f"Processeur: {platform.processor()}\n"
#             f"Dernier démarrage: {psutil.boot_time()}\n"
#             f"Niveau de batterie: {battery_info}\n"
#             f"État de charge: {is_charging}\n"
#             f"Utilisateur: {psutil.users()[0].name if psutil.users() else 'Non disponible'}"
#         )
    
#     return infoG


import psutil
import platform


# Informations sur la batterie
battery = psutil.sensors_battery()
battery_info = f"{battery.percent}%" if battery else "Non disponible"
is_charging = "En charge" if battery and battery.power_plugged else "Pas en charge"


def generalinfo():
    # Informations générales sous forme de dictionnaire
    infoG = {
        "Système": platform.system(),
        "Version": platform.version(),
        "Machine": platform.node(),
        "Structure": platform.machine(),
        "Processeur": platform.processor(),
        "Dernier démarrage": psutil.boot_time(),
        "Niveau de batterie": battery_info,
        "État de charge": is_charging,
        "Utilisateur": psutil.users()[0].name if psutil.users() else "Non disponible",
    }
    return infoG
