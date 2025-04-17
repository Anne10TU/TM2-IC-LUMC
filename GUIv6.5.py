import tkinter as tk
from tkinter import messagebox
import serial
import time  # Importeren van de time module voor vertraging

# Initialiseer seriële verbinding
try:
    ser = serial.Serial("/dev/rfcomm0", 9600, timeout=1)
    print("Arduino verbonden via Bluetooth")
except serial.SerialException:
    messagebox.showerror("Fout", "Bluetooth-verbinding met Arduino mislukt.")
    ser = None

root = tk.Tk()
root.title("ECMO Scenario Controller")
root.geometry("800x480")

is_ready = True

def receive_feedback():
    global is_ready
    if ser:
        while ser.in_waiting > 0:
            try:
                msg = ser.readline().decode().strip()
                print(f"Ontvangen: {msg}")
                feedback_var.set(f"Arduino zegt: {msg}")
                if msg == "READY":
                    is_ready = True
                elif "occlusie" in msg:  # Check of de Arduino om input vraagt
                    if "ven" in msg:
                        show_occlusie_choice("occlusie_ven")
                    elif "art" in msg:
                        show_occlusie_choice("occlusie_art")
            except:
                pass
    root.after(100, receive_feedback)

def send_command(cmd):
    global is_ready
    if is_ready and ser:
        try:
            ser.write((cmd + "\n").encode())
            print(f"Verzonden: {cmd}")
            feedback_var.set(f"Scenario: {cmd}")
            is_ready = False  # Zeg dat de Arduino nu bezig is
        except:
            messagebox.showerror("Fout", "Kon commando niet verzenden.")
    else:
        messagebox.showwarning("Bezig", "Arduino is nog bezig met een scenario.")

def scenario_button(scenario, art, ven):
    arterial_dc.set(art)
    venous_dc.set(ven)
    send_command(scenario)  # Scenario wordt eerst verzonden
    # Wacht een korte tijd zodat Arduino het scenario heeft ontvangen
    time.sleep(0.5)
    if "occlusie" in scenario:
        # Nadat het scenario is verzonden, roep de pop-up voor de ernst op
        show_occlusie_choice(scenario)

def manual_adjust(val=None):
    if is_ready:
        cmd = f"DC-Arterieel-{arterial_dc.get()}-Veneus-{venous_dc.get()}"
        send_command(cmd)

def show_occlusie_choice(scenario):
    popup = tk.Toplevel(root)
    popup.title("Kies ernst")

    tk.Label(popup, text="Kies de ernst van de occlusie:", font=("Arial", 12)).pack(pady=10)

    def handle_choice(choice):
        popup.destroy()
        # Stuur nu de keuze voor mild/ernstig naar de Arduino
        send_command(choice)

    tk.Button(popup, text="Mild", font=("Arial", 12), width=10,
              command=lambda: handle_choice("mild")).pack(pady=5)
    tk.Button(popup, text="Ernstig", font=("Arial", 12), width=10,
              command=lambda: handle_choice("ernstig")).pack(pady=5)

# GUI-elementen
tk.Label(root, text="Scenario Selectie", font=("Arial", 18)).pack(pady=10)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Hypertensie", width=15, height=2,
          command=lambda: scenario_button("hypertensie", 70, 90)).grid(row=0, column=0, padx=5)
tk.Button(button_frame, text="Hypotensie", width=15, height=2,
          command=lambda: scenario_button("hypotensie", 95, 62)).grid(row=0, column=1, padx=5)
tk.Button(button_frame, text="Occlusie Art.", width=15, height=2,
          command=lambda: scenario_button("occlusie_art", 95, 62)).grid(row=1, column=0, pady=5)
tk.Button(button_frame, text="Occlusie Ven.", width=15, height=2,
          command=lambda: scenario_button("occlusie_ven", 95, 62)).grid(row=1, column=1, pady=5)
tk.Button(button_frame, text="Stabiel", width=15, height=2,
          command=lambda: scenario_button("stabiel", 95, 90)).grid(row=2, column=0, columnspan=2, pady=10)

# Sliders voor handmatige regeling
tk.Label(root, text="Handmatige regeling", font=("Arial", 14)).pack(pady=10)

sliders_frame = tk.Frame(root)
sliders_frame.pack()

arterial_dc = tk.DoubleVar(value=95)
venous_dc = tk.DoubleVar(value=90)

tk.Label(sliders_frame, text="Arterieel DC").grid(row=0, column=0)
tk.Scale(sliders_frame, from_=0, to=100, variable=arterial_dc,
         orient=tk.HORIZONTAL, command=manual_adjust).grid(row=0, column=1)

tk.Label(sliders_frame, text="Veneus DC").grid(row=1, column=0)
tk.Scale(sliders_frame, from_=0, to=100, variable=venous_dc,
         orient=tk.HORIZONTAL, command=manual_adjust).grid(row=1, column=1)

feedback_var = tk.StringVar()
tk.Label(root, textvariable=feedback_var, font=("Arial", 12)).pack(pady=10)

# Start de feedback loop
receive_feedback()

# Start GUI
root.mainloop()
