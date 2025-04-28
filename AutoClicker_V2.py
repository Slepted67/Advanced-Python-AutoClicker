import tkinter as tk
from tkinter import ttk
import pyautogui
import threading
import time
import keyboard


class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        root.title("Slepted's Autoclicker")

        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(fill="both", expand=True)

        # Title
        ttk.Label(main_frame, text="Click Interval", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Interval inputs
        ttk.Label(main_frame, text="Minutes:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.minutes = tk.Entry(main_frame, width=10)
        self.minutes.grid(row=1, column=1, sticky="w", padx=5)

        ttk.Label(main_frame, text="Seconds:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.seconds = tk.Entry(main_frame, width=10)
        self.seconds.grid(row=2, column=1, sticky="w", padx=5)

        ttk.Label(main_frame, text="Milliseconds:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.milliseconds = tk.Entry(main_frame, width=10)
        self.milliseconds.grid(row=3, column=1, sticky="w", padx=5)

        # Click Mode
        ttk.Label(main_frame, text="Click Mode", font=("Segoe UI", 12, "bold")).grid(row=4, column=0, columnspan=2, pady=(20, 10))

        self.mode = tk.StringVar(value="infinite")
        ttk.Radiobutton(main_frame, text="Infinite Clicks", variable=self.mode, value="infinite").grid(row=5, column=0, columnspan=2, pady=2)
        ttk.Radiobutton(main_frame, text="Set Number of Clicks", variable=self.mode, value="limited").grid(row=6, column=0, columnspan=2, pady=2)

        ttk.Label(main_frame, text="Number of Clicks:").grid(row=7, column=0, sticky="e", padx=5, pady=5)
        self.click_count_entry = tk.Entry(main_frame, width=10)
        self.click_count_entry.grid(row=7, column=1, sticky="w", padx=5)

        # Mouse Button Choice
        ttk.Label(main_frame, text="Mouse Button", font=("Segoe UI", 12, "bold")).grid(row=8, column=0, columnspan=2, pady=(20, 10))
        self.click_button = tk.StringVar(value="left")
        ttk.Radiobutton(main_frame, text="Left Click", variable=self.click_button, value="left").grid(row=9, column=0, sticky="w")
        ttk.Radiobutton(main_frame, text="Right Click", variable=self.click_button, value="right").grid(row=9, column=1, sticky="w")

        # Hotkey
        ttk.Label(main_frame, text="Toggle Hotkey", font=("Segoe UI", 12, "bold")).grid(row=10, column=0, columnspan=2, pady=(20, 10))
        self.set_hotkey_btn = ttk.Button(main_frame, text="Set Hotkey (F6)", command=self.wait_for_hotkey)
        self.set_hotkey_btn.grid(row=11, column=0, columnspan=2, pady=5)

        # Start/Stop Buttons
        self.start_btn = ttk.Button(main_frame, text="Start Clicking", command=self.start_clicking)
        self.start_btn.grid(row=12, column=0, pady=20)

        self.stop_btn = ttk.Button(main_frame, text="Stop", command=self.stop_clicking)
        self.stop_btn.grid(row=12, column=1, pady=20)

        # Status label
        self.status_label = ttk.Label(main_frame, text="Clicking: OFF", font=("Segoe UI", 12, "bold"), foreground="red")
        self.status_label.grid(row=13, column=0, columnspan=2, pady=10)

        self.hotkey_prompt = ttk.Label(main_frame, text="", font=("Segoe UI", 10, "italic"), foreground="blue")
        self.hotkey_prompt.grid(row=14, column=0, columnspan=2)

        # Initial State
        self.running = False
        self.hotkey = "f6"
        self.hotkey_remover = keyboard.add_hotkey(self.hotkey, self.toggle_clicking)

    def get_interval(self):
        mins = int(self.minutes.get() or 0)
        secs = int(self.seconds.get() or 0)
        millis = int(self.milliseconds.get() or 0)
        return mins * 60 + secs + millis / 1000.0

    def click_loop(self):
        interval = self.get_interval()
        button_type = self.click_button.get()

        if self.mode.get() == "limited":
            try:
                total_clicks = int(self.click_count_entry.get())
            except ValueError:
                total_clicks = 0

            for _ in range(total_clicks):
                if not self.running:
                    break
                pyautogui.click(button=button_type)
                time.sleep(interval)
        else:
            while self.running:
                pyautogui.click(button=button_type)
                time.sleep(interval)

    def start_clicking(self):
        if not self.running:
            self.running = True
            self.status_label.config(text="Clicking: ON", foreground="green")
            threading.Thread(target=self.click_loop, daemon=True).start()

    def stop_clicking(self):
        self.running = False
        self.status_label.config(text="Clicking: OFF", foreground="red")

    def toggle_clicking(self):
        if self.running:
            self.stop_clicking()
            print(f"[{self.hotkey}] → Stopped Clicking")
        else:
            self.start_clicking()
            print(f"[{self.hotkey}] → Started Clicking")

    def wait_for_hotkey(self):
        self.hotkey_prompt.config(text="Press any key to set as hotkey...")
        self.set_hotkey_btn.config(state="disabled")

        def listen():
            event = keyboard.read_event()
            while event.event_type != "down":
                event = keyboard.read_event()

            new_key = event.name

            if self.hotkey_remover:
                try:
                    self.hotkey_remover()
                except Exception as e:
                    print(f"Error removing previous hotkey: {e}")

            self.hotkey = new_key
            self.hotkey_remover = keyboard.add_hotkey(self.hotkey, self.toggle_clicking)

            # Update GUI on main thread
            self.root.after(0, lambda: self.set_hotkey_btn.config(text=f"Set Hotkey ({self.hotkey.upper()})", state="normal"))
            self.root.after(0, lambda: self.hotkey_prompt.config(text=f"Hotkey set to {self.hotkey.upper()}"))

        threading.Thread(target=listen, daemon=True).start()


# Run App
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("600x850")
    root.resizable(True, True)
    app = AutoClickerApp(root)
    root.mainloop()
