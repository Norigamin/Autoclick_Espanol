import tkinter as tk
from tkinter import ttk

import keyboard
import pyautogui
import time
import threading
import ctypes

SendInput = ctypes.windll.user32.SendInput

PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL)
    ]

class HardwareInput(ctypes.Structure):
    _fields_ = [
        ("uMsg", ctypes.c_ulong),
        ("wParamL", ctypes.c_short),
        ("wParamH", ctypes.c_ushort)
    ]

class MouseInput(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", PUL)
    ]

class Input_I(ctypes.Union):
    _fields_ = [
        ("ki", KeyBdInput),
        ("mi", MouseInput),
        ("hi", HardwareInput)
    ]

class Input(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("ii", Input_I)
    ]

# Constantes
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010

# Variables
running = False
letra_iniciar = "z"
letra_parar = "x"
cantidad_clicks = 1
contador_clicks = 0
click_interval = 1.0

def click_rapido_izquierdo():
    x = Input(ctypes.c_ulong(0), 
              Input_I(mi=MouseInput(0, 0, 0, MOUSEEVENTF_LEFTDOWN, 0, ctypes.pointer(ctypes.c_ulong(0)))))
    y = Input(ctypes.c_ulong(0), 
              Input_I(mi=MouseInput(0, 0, 0, MOUSEEVENTF_LEFTUP, 0, ctypes.pointer(ctypes.c_ulong(0)))))
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
    SendInput(1, ctypes.pointer(y), ctypes.sizeof(y))

def click_rapido_derecho():
    x = Input(ctypes.c_ulong(0), 
              Input_I(mi=MouseInput(0, 0, 0, MOUSEEVENTF_RIGHTDOWN, 0, ctypes.pointer(ctypes.c_ulong(0)))))
    y = Input(ctypes.c_ulong(0), 
              Input_I(mi=MouseInput(0, 0, 0, MOUSEEVENTF_RIGHTUP, 0, ctypes.pointer(ctypes.c_ulong(0)))))
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
    SendInput(1, ctypes.pointer(y), ctypes.sizeof(y))

def actualizar_cps():
    global cantidad_clicks, click_interval
    try:
        cantidad_clicks = float(cantidad_clicks_entry.get())
        if cantidad_clicks > 0:
            click_interval = 1.0 / cantidad_clicks
        else:
            cantidad_clicks = 1  
            click_interval = 1.0
            cantidad_clicks_entry.delete(0, tk.END)
            cantidad_clicks_entry.insert(0, "1")
    except ValueError:
        cantidad_clicks = 1  
        click_interval = 1.0
        cantidad_clicks_entry.delete(0, tk.END)
        cantidad_clicks_entry.insert(0, "1")
    cps_label.config(text=f"Cantidad de cps actuales: {cantidad_clicks}")

def stop_running():
    global running, contador_clicks
    running = False
    start_button.config(state="active", bg="green", fg="white")
    contador_clicks = 0
    contador_label.config(text=f"Contador de clicks actuales: {contador_clicks}")

def actualizar_etiqueta_contador():
    contador_label.config(text=f"Contador de clicks actuales: {contador_clicks}")
    if running:
        window.after(100, actualizar_etiqueta_contador)

def autoclick():
    global running, contador_clicks, click_interval
    
    click_func = click_rapido_izquierdo if boton_click.get() == "Izquierdo" else click_rapido_derecho
    
    next_time = time.time()
    while running:
        current_time = time.time()
        
        if current_time >= next_time:
            clicks_to_do = int((current_time - next_time) / click_interval) + 1
            
            clicks_to_do = min(clicks_to_do, 100)
            
            for _ in range(clicks_to_do):
                if not running:
                    break
                click_func()
                contador_clicks += 1
            
            next_time = current_time + click_interval
        
        sleep_time = max(0.001, min(0.005, next_time - time.time()))
        time.sleep(sleep_time)

def start_autoclick():
    global running
    if not running:
        actualizar_cps()
        running = True
        start_button.config(state="disabled", bg="gray", fg="black")
        actualizar_etiqueta_contador()
        thread = threading.Thread(target=autoclick, daemon=True)
        thread.start()

def actualizar_teclas():
    global letra_iniciar, letra_parar
    letra_iniciar = tecla_iniciar_entry.get().lower()
    letra_parar = tecla_parar_entry.get().lower()
    keyboard.clear_all_hotkeys()
    keyboard.add_hotkey(letra_iniciar, start_autoclick)
    keyboard.add_hotkey(letra_parar, stop_running)
    start_button.config(text=f"Iniciar\n({letra_iniciar.upper()})")
    stop_button.config(text=f"Parar\n({letra_parar.upper()})")

def validar_cantidad_clicks(text):
    return text == "" or (text.replace(".", "", 1).isdigit() and len(text) <= 4)

def validar_tecla(text):
    return text == "" or (text.isalnum() and len(text) == 1)

# UI
window = tk.Tk()
window.geometry("300x670")
window.title("Autoclick")
window.resizable(0, 0)
try:
    window.iconbitmap("./Assets/icon.ico")
except tk.TclError:
    pass

tk.Label(window,text="ENTER para\ncambiar",font=("Segoe UI", 9, "bold")).place(x=175,y=140)

# Botones
start_button = tk.Button(window, text=f"Iniciar\n({letra_iniciar.upper()})", bg="green", fg="white", height=2, width=8, font=("Segoe UI", 14, "bold"), command=start_autoclick)
start_button.place(x=15, y=30)

stop_button = tk.Button(window, text=f"Parar\n({letra_parar.upper()})", bg="red", fg="white", height=2, width=8, font=("Segoe UI", 14, "bold"), command=stop_running)
stop_button.place(x=160, y=30)

# Configuración de clicks por segundo
tk.Label(window, text="Cantidad de\nClicks Por Segundo").place(x=20, y=180)
cantidad_clicks_entry = tk.Entry(window, width=4, validate="key", validatecommand=(window.register(validar_cantidad_clicks), "%P"))
cantidad_clicks_entry.insert(0, "1")
cantidad_clicks_entry.place(x=200, y=190)

# Etiquetas CPS/Contador de clics
information = ttk.LabelFrame(window, text="Información", width=260, height=130)
information.place(x=20, y=520)
cps_label = tk.Label(window, text=f"Cantidad de cps actuales: {cantidad_clicks}")
cps_label.place(x=30, y=560)
contador_label = tk.Label(window, text=f"Contador de clicks actuales: {contador_clicks}")
contador_label.place(x=30, y=610)

# Selección del botón del mouse
tk.Label(window, text="Seleccionar\nBotón del Click").place(x=30, y=240)
boton_click = ttk.Combobox(window, width=8, values=["Izquierdo", "Derecho"], state="readonly")
boton_click.set("Izquierdo")
boton_click.place(x=180, y=250)

# Asignar teclas
asignar_tecla = ttk.LabelFrame(window, text="Asignar Teclas")
asignar_tecla.place(x=20, y=320, width=260, height=140)

tk.Label(asignar_tecla, text="Iniciar").place(x=40, y=25)
tk.Label(asignar_tecla, text="Parar").place(x=40, y=65)

tecla_iniciar_entry = tk.Entry(window, width=3, validate="key", validatecommand=(window.register(validar_tecla), "%P"))
tecla_iniciar_entry.insert(0, letra_iniciar)
tecla_iniciar_entry.place(x=180, y=370)

tecla_parar_entry = tk.Entry(window, width=3, validate="key", validatecommand=(window.register(validar_tecla), "%P"))
tecla_parar_entry.insert(0, letra_parar)
tecla_parar_entry.place(x=180, y=410)

# Botón para actualizar teclas
tk.Button(window, text="Actualizar", command=actualizar_teclas).place(x=110, y=475)

# Asignar tecla ENTER para actualizar CPS
keyboard.add_hotkey("enter", actualizar_cps)

# Añadir teclas iniciales
keyboard.add_hotkey(letra_iniciar, start_autoclick)
keyboard.add_hotkey(letra_parar, stop_running)

# Mainloop
window.mainloop()