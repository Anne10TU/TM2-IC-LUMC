import tkinter as tk
from tkinter import messagebox
import serial
import time

# Probeer de seriële verbinding te openen met de Arduino via Bluetooth
ser = None
is_ready = True  # Flag die aangeeft of de Arduino klaar is om een commando te ontvangen

try:
    # Zorg ervoor dat je de juiste poort opgeeft voor de Bluetooth verbinding (bijv. /dev/rfcomm0)
    ser = serial.Serial("/dev/rfcomm0", 9600, timeout=1)  # Timeout toegevoegd
    messagebox.showinfo("Verbonden", "Arduino succesvol verbonden via Bluetooth!")
except serial.SerialException:
    messagebox.showerror("Fout",
                         "Kan geen verbinding maken met de Arduino. Zorg ervoor dat de Arduino is aangesloten en Bluetooth werkt.")


def receive_feedback():
    """Lees de seriële berichten van de Arduino en update de feedback in de GUI."""
    global is_ready  # Correcte plaatsing van de global declaratie
    if ser:
        try:
            while ser.in_waiting > 0:
                message = ser.readline().decode('utf-8').strip()  # Lees een bericht van de Arduino
                print(f"Ontvangen van Arduino: {message}")
                feedback_var.set(f"Arduino zegt: {message}")  # Update de feedback in de GUI
                if message == "READY":  # Controleer of de Arduino klaar is voor een nieuw commando
                    is_ready = True  # Markeer de Arduino als klaar
        except serial.SerialException as e:
            print(f"Fout bij het ontvangen van feedback: {e}")

    root.after(100, receive_feedback)  # Roep deze functie elke 100 ms opnieuw aan om continue feedback te krijgen


def send_command(command):
    """Verstuur het geselecteerde scenario naar de Arduino, als verbonden en klaar."""
    global is_ready  # Voeg de global declaratie hier toe
    if is_ready:
        if ser:
            try:
                ser.write(command.encode())
                print(f"Verstuurd naar Arduino: {command}")
                feedback_var.set(f"Huidig scenario: {command}")
                is_ready = False  # Markeer de Arduino als niet klaar
            except serial.SerialException as e:
                print(f"Fout bij het versturen van commando: {e}")
                messagebox.showerror("Fout", f"Fout bij het versturen van commando: {e}")
        else:
            print(f"Simulatie: zou {command} naar Arduino sturen.")
    else:
        messagebox.showwarning("Wachten op Arduino", "De Arduino is momenteel bezig, probeer het later opnieuw.")


def update_dc_values(*args):
    """Update de feedback voor de duty cycles en pas de tekst aan naar 'Handmatig'."""
    feedback_dc_var.set(f"Arterieel DC: {arterial_dc.get()}% | Veneus DC: {venous_dc.get()}%")
    feedback_var.set("Huidig scenario: Handmatig")  # Update scenario naar 'Handmatig'

    if is_ready:
        send_command(f"DC-Arterieel-{arterial_dc.get()}-Veneus-{venous_dc.get()}")
    else:
        messagebox.showwarning("Wachten op Arduino", "De Arduino is momenteel bezig, probeer het later opnieuw.")


def set_scenario(scenario_name, dc_art, dc_ven):
    """Verstuur het scenario naar de Arduino en update de GUI."""
    send_command(scenario_name)  # Scenario naar Arduino sturen
    feedback_var.set(f"Huidig scenario: {scenario_name}")

    # Update de duty cycles in de GUI (en de blauwe tekst)
    arterial_dc.set(dc_art)
    venous_dc.set(dc_ven)
    feedback_dc_var.set(f"Arterieel DC: {arterial_dc.get()}% | Veneus DC: {venous_dc.get()}%")

    # Zet de schuifregelaars weer aan na selectie van een scenario
    arterial_slider.config(state="normal")
    venous_slider.config(state="normal")


def reset_gui():
    """Reset de GUI na een scenario, zet de sliders terug aan."""
    arterial_slider.config(state="normal")
    venous_slider.config(state="normal")
    feedback_var.set("Huidig scenario: Geen")
    feedback_dc_var.set(f"Arterieel DC: {arterial_dc.get()}% | Veneus DC: {venous_dc.get()}%")


def select_occlusion():
    """Toon het pop-up venster voor het selecteren van arterieel/veneus en mild/ernstig."""
    occlusion_window = tk.Toplevel(root)
    occlusion_window.title("Selecteer Occlusie Type en Ernst")
    occlusion_window.geometry("300x250")

    def send_occlusion(occlusie_type, severity):
        """Stuur het geselecteerde scenario naar de Arduino met de juiste naamgeving."""
        if occlusie_type == "arterieel":
            set_scenario(f"occlusie_art-{severity}", 40, 90)  # Voorbeeld waarden voor arterieel
        elif occlusie_type == "veneus":
            set_scenario(f"occlusie_ven-{severity}", 95, 50)  # Voorbeeld waarden voor veneus
        occlusion_window.destroy()

    # Selecteer arterieel of veneus
    tk.Label(occlusion_window, text="Selecteer type occlusie:", font=("Arial", 12)).pack(pady=10)
    tk.Button(occlusion_window, text="Arterieel", command=lambda: select_severity("arterieel")).pack(fill="x", pady=5)
    tk.Button(occlusion_window, text="Veneus", command=lambda: select_severity("veneus")).pack(fill="x", pady=5)

    def select_severity(occlusie_type):
        """Selecteer de ernst van de occlusie (Mild of Ernstig)."""
        severity_window = tk.Toplevel(occlusion_window)
        severity_window.title(f"Selecteer ernst van {occlusie_type} occlusie")
        severity_window.geometry("200x150")

        def send_severity(severity):
            send_occlusion(occlusie_type, severity)

        tk.Label(severity_window, text="Selecteer ernst:", font=("Arial", 12)).pack(pady=10)
        tk.Button(severity_window, text="Mild", command=lambda: send_severity("Mild")).pack(fill="x", pady=5)
        tk.Button(severity_window, text="Ernstig", command=lambda: send_severity("Ernstig")).pack(fill="x", pady=5)


# GUI Setup
root = tk.Tk()
root.title("Scenario Selectie")
root.geometry("800x480")  # Geschikt voor een 7-inch display

# Label
tk.Label(root, text="Selecteer een scenario:", font=("Arial", 16)).pack(pady=10)

# Frame voor schuifregelaars (left side of the screen)
slider_frame = tk.Frame(root)
slider_frame.pack(side="left", padx=20, pady=20)

# Duty cycle variabelen
arterial_dc = tk.IntVar(value=55)
venous_dc = tk.IntVar(value=55)

# Arteriële schuifregelaar en labels
tk.Label(slider_frame, text="Arteriële Duty Cycle:", font=("Arial", 14)).pack(pady=(10, 5))
arterial_value_label = tk.Label(slider_frame, text=f"{arterial_dc.get()}%", font=("Arial", 12))
arterial_value_label.pack()

arterial_slider = tk.Scale(slider_frame, from_=55, to_=95, orient="horizontal", variable=arterial_dc,
                           command=update_dc_values)
arterial_slider.pack()

# Veneuze schuifregelaar en labels
tk.Label(slider_frame, text="Veneuze Duty Cycle:", font=("Arial", 14)).pack(pady=(20, 5))
venous_value_label = tk.Label(slider_frame, text=f"{venous_dc.get()}%", font=("Arial", 12))
venous_value_label.pack()

venous_slider = tk.Scale(slider_frame, from_=55, to_=95, orient="horizontal", variable=venous_dc,
                         command=update_dc_values)
venous_slider.pack()

# Frame voor scenario knoppen (right side of the screen)
button_frame = tk.Frame(root)
button_frame.pack(side="right", padx=20, pady=20)

# Scenario-knoppen
scenarios = {
    "Hypertensie": lambda: set_scenario("Hypertensie", 70, 90),
    "Hypotensie": lambda: set_scenario("Hypotensie", 95, 62),
    "Occlusie": select_occlusion,  # Enkele knop voor "Occlusie"
    "Stabiel": lambda: set_scenario("Stabiel", 95, 90),
}

for name, action in scenarios.items():
    tk.Button(button_frame, text=name, command=action, font=("Arial", 14), width=20, height=2).pack(pady=5)

# Feedback voor de huidige duty cycles
feedback_dc_var = tk.StringVar()
feedback_dc_var.set(f"Arterieel DC: {arterial_dc.get()}% | Veneus DC: {venous_dc.get()}%")
feedback_dc_label = tk.Label(root, textvariable=feedback_dc_var, font=("Arial", 14), fg="blue")
feedback_dc_label.pack(pady=10)

# Feedback voor de geselecteerde scenario
feedback_var = tk.StringVar()
feedback_var.set("Huidig scenario: Geen")
feedback_label = tk.Label(root, textvariable=feedback_var, font=("Arial", 16))
feedback_label.pack(pady=10)

# Start feedback-ontvanger
receive_feedback()

# Start de GUI
root.mainloop()
