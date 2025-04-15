import tkinter as tk
from tkinter import messagebox
import serial
import threading
import time

# ========================== Seriële verbinding instellen ==========================
ser = None

def init_serial():
    global ser
    try:
        ser = serial.Serial("/dev/rfcomm0", 9600, timeout=1)
        print("Bluetooth verbinding met Arduino is geslaagd.")
    except serial.SerialException:
        print("Bluetooth-verbinding met Arduino mislukt. Controleer of /dev/rfcomm0 beschikbaar is.")
        ser = None

init_serial()

# ========================== Seriële communicatie ==========================
def send_command(command):
    """Verstuur een commando naar de Arduino, of print als simulatie."""
    if ser and ser.is_open:
        try:
            ser.write((command + "\n").encode())
            print(f"Verzonden naar Arduino: {command}")
        except serial.SerialException:
            print("Fout bij verzenden naar Arduino.")
    else:
        print(f"Simulatie: zou '{command}' naar Arduino sturen.")
    feedback_var.set(f"Huidig scenario: {command}")

def update_dc_values(*args):
    """Update de duty cycle waarden en stuur handmatige aanpassing naar Arduino."""
    dc_text = f"Arterieel DC: {arterial_dc.get()}% | Veneus DC: {venous_dc.get()}%"
    feedback_dc_var.set(dc_text)
    feedback_var.set("Huidig scenario: Handmatig")
    command = f"DC-Arterieel-{arterial_dc.get()}-Veneus-{venous_dc.get()}"
    send_command(command)

# ========================== Scenario logica ==========================
def set_scenario(scenario_name, dc_art, dc_ven):
    """Zet een scenario en update GUI + stuur naar Arduino."""
    send_command(scenario_name)
    arterial_dc.set(dc_art)
    venous_dc.set(dc_ven)
    feedback_dc_var.set(f"Arterieel DC: {dc_art}% | Veneus DC: {dc_ven}%")

def select_occlusion():
    """Pop-up voor occlusie-type + ernst."""
    occlusion_window = tk.Toplevel(root)
    occlusion_window.title("Selecteer Occlusie Type en Ernst")
    occlusion_window.geometry("300x200")

    def select_severity(occlusie_type):
        severity_window = tk.Toplevel(occlusion_window)
        severity_window.title(f"Ernst van {occlusie_type} occlusie")
        severity_window.geometry("200x150")

        def send_occlusion(severity):
            if occlusie_type == "arterieel":
                set_scenario(f"Arteriële Occlusie - {severity}", 40, 90)
            else:
                set_scenario(f"Veneuze Occlusie - {severity}", 95, 50)
            occlusion_window.destroy()
            severity_window.destroy()

        tk.Label(severity_window, text="Selecteer ernst:", font=("Arial", 12)).pack(pady=10)
        tk.Button(severity_window, text="Mild", command=lambda: send_occlusion("Mild")).pack(fill="x", pady=5)
        tk.Button(severity_window, text="Ernstig", command=lambda: send_occlusion("Ernstig")).pack(fill="x", pady=5)

    tk.Label(occlusion_window, text="Selecteer type occlusie:", font=("Arial", 12)).pack(pady=10)
    tk.Button(occlusion_window, text="Arterieel", command=lambda: select_severity("arterieel")).pack(fill="x", pady=5)
    tk.Button(occlusion_window, text="Veneus", command=lambda: select_severity("veneus")).pack(fill="x", pady=5)

# ========================== GUI setup ==========================
root = tk.Tk()
root.title("Scenario Selectie")
root.geometry("800x480")

# Variabelen
arterial_dc = tk.IntVar(value=55)
venous_dc = tk.IntVar(value=55)
feedback_var = tk.StringVar(value="Huidig scenario: Geen")
feedback_dc_var = tk.StringVar(value=f"Arterieel DC: {arterial_dc.get()}% | Veneus DC: {venous_dc.get()}%")

# === Links: sliders ===
slider_frame = tk.Frame(root)
slider_frame.pack(side="left", padx=30, pady=20)

tk.Label(slider_frame, text="Arteriële Duty Cycle:", font=("Arial", 14)).pack(pady=(10, 5))
tk.Label(slider_frame, textvariable=arterial_dc, font=("Arial", 12)).pack()
arterial_slider = tk.Scale(slider_frame, from_=55, to=95, orient="horizontal", variable=arterial_dc, command=update_dc_values)
arterial_slider.pack()

tk.Label(slider_frame, text="Veneuze Duty Cycle:", font=("Arial", 14)).pack(pady=(20, 5))
tk.Label(slider_frame, textvariable=venous_dc, font=("Arial", 12)).pack()
venous_slider = tk.Scale(slider_frame, from_=55, to=95, orient="horizontal", variable=venous_dc, command=update_dc_values)
venous_slider.pack()

# === Rechts: knoppen ===
button_frame = tk.Frame(root)
button_frame.pack(side="right", padx=30, pady=20)

tk.Label(button_frame, text="Selecteer een scenario:", font=("Arial", 16)).pack(pady=10)

scenarios = {
    "Hypertensie": lambda: set_scenario("Hypertensie", 70, 90),
    "Hypotensie": lambda: set_scenario("Hypotensie", 95, 62),
    "Occlusie": select_occlusion,
    "Stabiel": lambda: set_scenario("Stabiel", 95, 90),
}

for name, action in scenarios.items():
    tk.Button(button_frame, text=name, command=action, font=("Arial", 14), width=20, height=2).pack(pady=5)

# === Feedback labels ===
feedback_frame = tk.Frame(root)
feedback_frame.pack(pady=10)

tk.Label(feedback_frame, textvariable=feedback_var, font=("Arial", 14), fg="blue").pack()
tk.Label(feedback_frame, textvariable=feedback_dc_var, font=("Arial", 14), fg="blue").pack()

# Start de GUI
root.mainloop()
