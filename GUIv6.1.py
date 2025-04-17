import tkinter as tk
from tkinter import messagebox
import serial
import threading
import time

# Seriële verbinding instellen (pas de poort en baudrate aan indien nodig)
ser = serial.Serial('/dev/rfcomm0', 9600, timeout=1)
time.sleep(2)  # Geef tijd voor verbinding

# Scenario's die verzonden kunnen worden
scenarios = [
    "normaal", "hypertensie", "hypotensie", "occlusie ven.",
    "occlusie art.", "lucht", "leeg"
]

class ScenarioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Scenario Selectie")
        self.ready_for_command = True

        # Status label
        self.status_label = tk.Label(root, text="Status: Wachtend op selectie", font=("Arial", 12))
        self.status_label.pack(pady=10)

        # Buttons voor elk scenario
        for scenario in scenarios:
            button = tk.Button(root, text=scenario, font=("Arial", 14), width=20,
                               command=lambda s=scenario: self.send_scenario(s))
            button.pack(pady=5)

        # Start thread om berichten van Arduino te ontvangen
        self.receive_thread = threading.Thread(target=self.receive_from_arduino)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def send_scenario(self, scenario):
        if self.ready_for_command:
            ser.write(f"{scenario}\n".encode())
            print(f"Verzonden: {scenario}")
            self.status_label.config(text=f"Scenario verzonden: {scenario}")
            self.ready_for_command = False  # Wacht op reactie Arduino

    def send_choice(self, keuze):
        ser.write(f"{keuze}\n".encode())
        print(f"Keuze verzonden: {keuze}")
        self.status_label.config(text=f"Keuze verzonden: {keuze}")
        self.ready_for_command = True

    def show_choice_popup(self):
        popup = tk.Toplevel(self.root)
        popup.title("Kies ernst")

        tk.Label(popup, text="Kies de ernst van de occlusie:", font=("Arial", 12)).pack(pady=10)

        tk.Button(popup, text="Mild", font=("Arial", 12), width=10,
                  command=lambda: self.handle_choice(popup, "mild")).pack(pady=5)
        tk.Button(popup, text="Ernstig", font=("Arial", 12), width=10,
                  command=lambda: self.handle_choice(popup, "ernstig")).pack(pady=5)

    def handle_choice(self, popup, choice):
        popup.destroy()
        self.send_choice(choice)

    def receive_from_arduino(self):
        while True:
            if ser.in_waiting > 0:
                data = ser.readline().decode().strip()
                print(f"Ontvangen van Arduino: {data}")
                if data.lower() == "mild of ernstig?":
                    self.root.after(0, self.show_choice_popup)
                else:
                    self.root.after(0, self.update_status, data)
                    self.ready_for_command = True

    def update_status(self, message):
        self.status_label.config(text=f"Arduino zegt: {message}")

# Start de GUI
root = tk.Tk()
app = ScenarioApp(root)
root.mainloop()
