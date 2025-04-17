import tkinter as tk
from tkinter import messagebox
import serial

# Seriële verbinding
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
                    status_label.config(text="Status: READY", bg="green")
                elif msg == "RUNNING":
                    status_label.config(text="Status: ACTIEF", bg="orange")
                elif msg == "ERROR":
                    status_label.config(text="Status: FOUT", bg="red")
                else:
                    status_label.config(text=f"Status: {msg}", bg="gray")
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
            is_ready = False
        except:
            messagebox.showerror("Fout", "Kon commando niet verzenden.")
    else:
        messagebox.showwarning("Bezig", "Arduino is nog bezig met een scenario.")

def scenario_button(scenario, art, ven):
    arterial_dc.set(art)
    venous_dc.set(ven)
    send_command(scenario)

def manual_adjust(val=None):
    if is_ready:
        cmd = f"DC-Arterieel-{arterial_dc.get()}-Veneus-{venous_dc.get()}"
        send_command(cmd)

# GUI
top_frame = tk.Frame(root)
top_frame.pack(pady=10)

# Scenario-knoppen
button_frame = tk.LabelFrame(top_frame, text="Scenario Selectie", font=("Arial", 12))
button_frame.grid(row=0, column=0, padx=10)

scenario_buttons = [
    ("Hypertensie", "hypertensie", 70, 90),
    ("Hypotensie", "hypotensie", 95, 62),
    ("Occlusie Art. Mild", "occlusie_art-mild", 69, 90),
    ("Occlusie Art. Ernstig", "occlusie_art-ernstig", 66, 90),
    ("Occlusie Ven. Mild", "occlusie_ven-mild", 95, 60),
    ("Occlusie Ven. Ernstig", "occlusie_ven-ernstig", 95, 58),
    ("Stabiel", "stabiel", 95, 90),
]

for i, (label, cmd, art, ven) in enumerate(scenario_buttons):
    r, c = divmod(i, 3)
    tk.Button(button_frame, text=label, width=18, height=2,
              command=lambda c=cmd, a=art, v=ven: scenario_button(c, a, v)).grid(row=r, column=c, padx=5, pady=5)

tk.Button(button_frame, text="RESET", width=56, height=2,
          command=lambda: send_command("reset")).grid(row=3, column=0, columnspan=3, pady=5)

# Sliders (naast knoppen)
slider_frame = tk.LabelFrame(top_frame, text="Handmatige regeling", font=("Arial", 12))
slider_frame.grid(row=0, column=1, padx=10)

arterial_dc = tk.DoubleVar(value=95)
venous_dc = tk.DoubleVar(value=90)

tk.Label(slider_frame, text="Arterieel DC").grid(row=0, column=0, sticky="w")
tk.Scale(slider_frame, from_=0, to=100, variable=arterial_dc,
         orient=tk.HORIZONTAL, length=200, command=manual_adjust).grid(row=0, column=1)

tk.Label(slider_frame, text="Veneus DC").grid(row=1, column=0, sticky="w")
tk.Scale(slider_frame, from_=0, to=100, variable=venous_dc,
         orient=tk.HORIZONTAL, length=200, command=manual_adjust).grid(row=1, column=1)

# Status en feedback onderin
bottom_frame = tk.Frame(root)
bottom_frame.pack(pady=10)

status_label = tk.Label(bottom_frame, text="Status: Onbekend", font=("Arial", 10),
                        bg="gray", fg="white", width=20)
status_label.pack(pady=5)

feedback_var = tk.StringVar()
tk.Label(bottom_frame, textvariable=feedback_var, font=("Arial", 12)).pack()

# Start feedback loop
receive_feedback()

# Start GUI
root.mainloop()
