# -*- coding: utf-8 -*-
"""
Created on Wed Mar 26 15:11:18 2025

@author: Annev
"""

import tkinter as tk
from tkinter import messagebox
import serial

# Probeer de seriële verbinding te openen, maar vang de fout op als er geen Arduino is aangesloten
ser = None
try:
    ser = serial.Serial("COM2", 9600)  # Pas COM-poort aan als nodig
except serial.SerialException:
    print("Geen Arduino gevonden, GUI wordt zonder seriële verbinding gestart.")

def send_command(command):
    """Verstuur het geselecteerde scenario naar de Arduino, als verbonden, en update de feedback."""
    if ser:
        ser.write(command.encode())
    else:
        print(f"Simulatie: zou {command} naar Arduino sturen.")
    
    # Update feedbackvak
    feedback_var.set(f"Huidig scenario: {command}")

def select_occlusion():
    """Toon een extra menu voor occlusie-selectie."""
    occlusion_window = tk.Toplevel(root)
    occlusion_window.title("Kies Occlusie Type")
    occlusion_window.geometry("300x200")

    def send_occlusion(type, severity):
        send_command(f"Occlusie-{type}-{severity}")
        occlusion_window.destroy()

    tk.Label(occlusion_window, text="Selecteer type occlusie:", font=("Arial", 12)).pack(pady=10)
    tk.Button(occlusion_window, text="Veneus - Mild", command=lambda: send_occlusion("Veneus", "Mild")).pack(fill="x")
    tk.Button(occlusion_window, text="Veneus - Ernstig", command=lambda: send_occlusion("Veneus", "Ernstig")).pack(fill="x")
    tk.Button(occlusion_window, text="Arterieel - Mild", command=lambda: send_occlusion("Arterieel", "Mild")).pack(fill="x")
    tk.Button(occlusion_window, text="Arterieel - Ernstig", command=lambda: send_occlusion("Arterieel", "Ernstig")).pack(fill="x")

# GUI Setup
root = tk.Tk()
root.title("Scenario Selectie")
root.geometry("800x480")  # Geschikt voor een 7-inch display

# Label
tk.Label(root, text="Selecteer een scenario:", font=("Arial", 16)).pack(pady=10)

# Scenario-knoppen
scenarios = {
    "Hypertensie": lambda: send_command("Hypertensie"),
    "Hypotensie": lambda: send_command("Hypotensie"),
    "Occlusie": select_occlusion,
    "Stabiel": lambda: send_command("Stabiel"),
}

# Frame voor knoppen
button_frame = tk.Frame(root)
button_frame.pack(pady=20)

for name, action in scenarios.items():
    tk.Button(button_frame, text=name, command=action, font=("Arial", 14), width=20, height=2).pack(pady=5)

# Feedback Label
feedback_var = tk.StringVar()
feedback_var.set("Huidig scenario: Geen")
feedback_label = tk.Label(root, textvariable=feedback_var, font=("Arial", 14), fg="blue")
feedback_label.pack(pady=20)

# Start GUI-loop
root.mainloop()
