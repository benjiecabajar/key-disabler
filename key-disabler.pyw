import ctypes
import sys
import os
import customtkinter as ctk
import keyboard
import winreg
from tkinter import messagebox

# Hide console window (Windows only)
if sys.platform == "win32":
    ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

# Setup default theme (fixed to dark)
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

SAVE_FILE = "disabled_keys.txt"
disabled_keys = set()

def load_disabled_keys():
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r") as f:
                for key in f.read().splitlines():
                    if key:
                        disabled_keys.add(key)
                        keyboard.block_key(key)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load disabled keys:\n{e}")

def save_disabled_keys():
    try:
        with open(SAVE_FILE, "w") as f:
            for key in disabled_keys:
                f.write(key + "\n")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save disabled keys:\n{e}")

def update_disabled_keys_display():
    display = ", ".join(sorted(disabled_keys)) if disabled_keys else "No disabled keys."
    disabled_keys_text.configure(state="normal")
    disabled_keys_text.delete("1.0", ctk.END)
    disabled_keys_text.insert(ctk.END, display)
    disabled_keys_text.configure(state="disabled")

def valid_key(key):
    # Simple validation: check if keyboard module recognizes the key
    try:
        return keyboard.key_to_scan_codes(key) != []
    except:
        return False

def add_or_toggle_key():
    key = input_key.get().strip().lower()
    if not key:
        messagebox.showinfo("Input Error", "Please enter a key name.")
        return

    if not valid_key(key):
        messagebox.showerror("Invalid Key", f"'{key}' is not a recognized key.")
        return

    if key in disabled_keys:
        # toggle: enable it
        keyboard.unblock_key(key)
        disabled_keys.remove(key)
        messagebox.showinfo("Key Enabled", f"'{key}' is now enabled.")
    else:
        # disable key
        disabled_keys.add(key)
        keyboard.block_key(key)
        messagebox.showinfo("Key Disabled", f"'{key}' has been disabled.")

    input_key.delete(0, ctk.END)
    update_disabled_keys_display()
    save_disabled_keys()

def remove_key():
    key = input_key.get().strip().lower()
    if not key:
        messagebox.showinfo("Input Error", "Please enter a key name to remove.")
        return
    if key in disabled_keys:
        keyboard.unblock_key(key)
        disabled_keys.remove(key)
        messagebox.showinfo("Key Removed", f"'{key}' removed from disabled keys.")
        update_disabled_keys_display()
        save_disabled_keys()
    else:
        messagebox.showinfo("Not Found", f"'{key}' is not in the disabled keys list.")
    input_key.delete(0, ctk.END)

def reset_all_keys():
    if messagebox.askyesno("Confirm Reset", "Are you sure you want to enable all keys?"):
        for key in disabled_keys:
            keyboard.unblock_key(key)
        disabled_keys.clear()
        update_disabled_keys_display()
        save_disabled_keys()

def disable_page_keys():
    for key in ['page up', 'page down']:
        if key not in disabled_keys:
            disabled_keys.add(key)
            keyboard.block_key(key)
    update_disabled_keys_display()
    save_disabled_keys()
    messagebox.showinfo("Keys Disabled", "Page Up and Page Down keys disabled.")

def set_run_at_startup():
    if sys.platform == "win32":
        try:
            exe_path = os.path.abspath(sys.argv[0])
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Run",
                                 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "GlobalKeyDisabler", 0, winreg.REG_SZ, exe_path)
            winreg.CloseKey(key)
            messagebox.showinfo("Success", "Application set to run at startup.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set run at startup:\n{e}")

def hide_window():
    app.withdraw()

# Load keys on start
load_disabled_keys()

# === UI ===
app = ctk.CTk()
app.title("🔒 Key Disabler by: BenDev")
app.geometry("370x420")
app.resizable(False, False)

if sys.platform == "win32":
    app.wm_attributes("-toolwindow", True)
    app.wm_attributes("-topmost", True)

title_label = ctk.CTkLabel(
    app,
    text="🔒 Global Key Disabler",
    font=ctk.CTkFont(size=20, weight="bold"),
    pady=10
)
title_label.pack()

input_frame = ctk.CTkFrame(app, fg_color="#1e1e1e", corner_radius=12)
input_frame.pack(padx=20, pady=(5,15), fill="x")

input_key = ctk.CTkEntry(
    input_frame,
    placeholder_text="Enter key to disable/enable",
    font=ctk.CTkFont(size=14),
    height=32
)
input_key.pack(side="left", padx=(15, 10), pady=10, fill="x", expand=True)

add_toggle_btn = ctk.CTkButton(
    input_frame,
    text="Toggle Disable",
    command=add_or_toggle_key,
    fg_color="#3a86ff",
    hover_color="#5a9bff",
    corner_radius=12,
    width=110,
    font=ctk.CTkFont(size=14, weight="bold")
)
add_toggle_btn.pack(side="right", padx=(5, 5), pady=10)

remove_btn = ctk.CTkButton(
    input_frame,
    text="Remove Key",
    command=remove_key,
    fg_color="#ff4b5c",
    hover_color="#ff6f7e",
    corner_radius=12,
    width=90,
    font=ctk.CTkFont(size=14, weight="bold")
)
remove_btn.pack(side="right", padx=(5, 15), pady=10)

button_params = dict(corner_radius=12, height=38, font=ctk.CTkFont(size=14, weight="bold"))

disable_page_btn = ctk.CTkButton(
    app,
    text="Disable Page Up / Down",
    command=disable_page_keys,
    fg_color="#ff6f61",
    hover_color="#ff8a75",
    **button_params
)
disable_page_btn.pack(fill="x", padx=20, pady=(0, 10))

reset_btn = ctk.CTkButton(
    app,
    text="Enable All Keys",
    command=reset_all_keys,
    fg_color="#ff3b3b",
    hover_color="#ff5c5c",
    **button_params
)
reset_btn.pack(fill="x", padx=20, pady=(0, 10))

startup_btn = ctk.CTkButton(
    app,
    text="Run on Startup",
    command=set_run_at_startup,
    fg_color="#4caf50",
    hover_color="#66bb6a",
    **button_params
)
startup_btn.pack(fill="x", padx=20, pady=(0, 10))

hide_btn = ctk.CTkButton(
    app,
    text="Hide Window",
    command=hide_window,
    fg_color="#666666",
    hover_color="#888888",
    **button_params
)
hide_btn.pack(fill="x", padx=20, pady=(0, 10))

disabled_label = ctk.CTkLabel(
    app,
    text="Disabled Keys:",
    font=ctk.CTkFont(size=15, weight="bold"),
    anchor="w"
)
disabled_label.pack(fill="x", padx=20)

disabled_keys_text = ctk.CTkTextbox(
    app,
    height=80,
    fg_color="#2a2a2a",
    corner_radius=12,
    font=ctk.CTkFont(size=13),
    border_width=0,
    state="disabled"
)
disabled_keys_text.pack(padx=20, pady=(5, 15), fill="x")

dev_label = ctk.CTkLabel(
    app,
    text="Developer: BenDev",
    font=ctk.CTkFont(size=11, weight="normal"),
    text_color="#888888"
)
dev_label.pack(side="bottom", pady=(0, 8))

update_disabled_keys_display()
app.mainloop()
