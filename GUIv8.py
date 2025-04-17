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
tk.Label(root, text="Scenario Selectie", font=("Arial", 18)).pack(pady=10)

button_frame = tk.Frame(root)
button_frame.pack(pady=10)

tk.Button(button_frame, text="Hypertensie", width=18, height=2,
          command=lambda: scenario_button("hypertensie", 70, 90)).grid(row=0, column=0, padx=5, pady=5)
tk.Button(button_frame, text="Hypotensie", width=18, height=2,
          command=lambda: scenario_button("hypotensie", 95, 62)).grid(row=0, column=1, padx=5, pady=5)
tk.Button(button_frame, text="Occlusie Art. Mild", width=18, height=2,
          command=lambda: scenario_button("occlusie_art-mild", 69, 90)).grid(row=1, column=0, padx=5, pady=5)
tk.Button(button_frame, text="Occlusie Art. Ernstig", width=18, height=2,
          command=lambda: scenario_button("occlusie_art-ernstig", 66, 90)).grid(row=1, column=1, padx=5, pady=5)
tk.Button(button_frame, text="Occlusie Ven. Mild", width=18, height=2,
          command=lambda: scenario_button("occlusie_ven-mild", 95, 60)).grid(row=2, column=0, padx=5, pady=5)
tk.Button(button_frame, text="Occlusie Ven. Ernstig", width=18, height=2,
          command=lambda: scenario_button("occlusie_ven-ernstig", 95, 58)).grid(row=2, column=1, padx=5, pady=5)
tk.Button(button_frame, text="Stabiel", width=38, height=2,
          command=lambda: scenario_button("stabiel", 95, 90)).grid(row=3, column=0, columnspan=2, pady=10)
tk.Button(right_frame, text="RESET", **button_style,
          command=lambda: send_command("reset")).pack(pady=5)


# Handmatige regeling
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
status_label = tk.Label(root, text="Status: Onbekend", font=("Arial", 10), bg="gray", fg="white", width=20)
status_label.pack(pady=5)
tk.Label(root, textvariable=feedback_var, font=("Arial", 12)).pack(pady=10)

# Start feedback loop
receive_feedback()

# Start GUI
root.mainloop()
