import tkinter as tk
from tkinter import ttk, colorchooser
import keyboard
import pyperclip
import pyautogui
import pystray
from PIL import Image, ImageDraw, ImageTk
import threading
import os
from translations import translations

class MacroTool:
    def __init__(self, root):
        # Make window
        self.root = root
        self.root.title("Macro Tool")
        self.root.geometry("750x800")
        
        # Save text, enter function and settings
        self.macro_texts = {}
        self.enter_after = {}
        self.bg_color = "#0080C0"
        self.text_color = "#000000"
        self.entry_bg = "#f0f0f0"
        
        # Save all the keys and buttons
        self.key_bindings = {}
        self.key_buttons = {}
        self.original_keys = {}
        for i in range(1, 13):
            self.key_bindings[f"f{i}"] = f"f{i}"
            self.original_keys[f"f{i}"] = f"F{i}"
        
        # For changing keys
        self.waiting_for_key = False
        self.current_key_binding = None
        
        # Language settings
        self.language = "en"
        self.translations = translations
        
        # Make tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Make tabs for macros and settings
        self.main_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.main_tab, text=self.translations[self.language]["macros_tab"])
        
        self.settings_tab = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.settings_tab, text=self.translations[self.language]["settings_tab"])
        
        # Make main area
        self.main_frame = ttk.Frame(self.main_tab)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Make titles
        ttk.Label(self.main_frame, text=self.translations[self.language]["key_header"]).grid(row=0, column=0, sticky=tk.EW, pady=10)
        ttk.Label(self.main_frame, text=self.translations[self.language]["text_header"]).grid(row=0, column=1, sticky=tk.EW, pady=10)
        ttk.Label(self.main_frame, text=self.translations[self.language]["with_enter"]).grid(row=0, column=2, sticky=tk.EW, pady=10)
        
        # Make input fields look nice
        style = ttk.Style()
        style.configure("Custom.TEntry",
                       fieldbackground=self.entry_bg,
                       borderwidth=2,
                       relief="solid",
                       padding=5)
        
        # Make 12 rows for F1-F12
        for i in range(12):
            # Make button
            key_button = ttk.Button(self.main_frame, text=f"F{i+1}", command=lambda k=f"f{i+1}": self.start_key_binding(k))
            key_button.grid(row=i+1, column=0, sticky=tk.W, pady=15)
            self.key_buttons[f"f{i+1}"] = key_button
            
            # Make text field
            entry = ttk.Entry(self.main_frame, width=50, style="Custom.TEntry")
            entry.grid(row=i+1, column=1, sticky=(tk.W, tk.E), pady=15, padx=(5, 25))
            self.macro_texts[f"f{i+1}"] = entry
            
            # Make checkbox
            var = tk.BooleanVar()
            checkbox = ttk.Checkbutton(self.main_frame, variable=var)
            checkbox.grid(row=i+1, column=2, sticky=tk.W, pady=15, padx=5)
            self.enter_after[f"f{i+1}"] = var
        
        # Make columns right size
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=3)
        self.main_frame.columnconfigure(2, weight=1)
        
        # Make settings tab
        settings_frame = ttk.Frame(self.settings_tab)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Make color buttons
        ttk.Label(settings_frame, text=self.translations[self.language]["color_settings"], font=("Arial", 12, "bold"), style="Settings.TLabel", anchor="center").pack(pady=(0, 20))
        
        color_buttons_frame = ttk.Frame(settings_frame)
        color_buttons_frame.pack(fill=tk.X, pady=10)
        
        # Make color change buttons
        ttk.Button(color_buttons_frame, text=self.translations[self.language]["bg_color"], command=self.choose_bg_color, style="Settings.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(color_buttons_frame, text=self.translations[self.language]["text_color"], command=self.choose_text_color, style="Settings.TButton").pack(side=tk.LEFT, padx=5)
        
        # Make language selection
        ttk.Label(settings_frame, text=self.translations[self.language]["language_settings"], font=("Arial", 12, "bold"), style="Settings.TLabel", anchor="center").pack(pady=(30, 20))
        
        language_frame = ttk.Frame(settings_frame)
        language_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(language_frame, text="", style="Settings.TLabel").pack(side=tk.LEFT, padx=5)
        
        # Make language buttons
        language_var = tk.StringVar(value=self.language)
        ttk.Radiobutton(language_frame, text=self.translations[self.language]["english"], variable=language_var, value="en", command=lambda: self.change_language("en"), style="Settings.TRadiobutton").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(language_frame, text=self.translations[self.language]["german"], variable=language_var, value="de", command=lambda: self.change_language("de"), style="Settings.TRadiobutton").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(language_frame, text=self.translations[self.language]["spanish"], variable=language_var, value="es", command=lambda: self.change_language("es"), style="Settings.TRadiobutton").pack(side=tk.LEFT, padx=10)
        
        # Start keyboard
        self.setup_keyboard_hooks()
        
        # Set colors
        self.apply_colors()
        
        # Make system tray
        self.setup_system_tray()
        
        # Make close button work
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Check if program runs
        self.running = True
    
    def setup_system_tray(self):
        # Make icon
        image = Image.new('RGB', (64, 64), color = 'white')
        dc = ImageDraw.Draw(image)
        dc.rectangle((0, 0, 63, 63), outline='black', width=2)
        dc.text((10, 25), "MACRO", fill='black')
        
        # Make menu
        menu = (
            pystray.MenuItem(self.translations[self.language]["open"], self.show_window),
            pystray.MenuItem(self.translations[self.language]["quit"], self.quit_window)
        )
        
        # Start icon
        self.icon = pystray.Icon("macro_tool", image, self.translations[self.language]["app_title"], menu)
        self.icon_thread = threading.Thread(target=self.run_icon, daemon=True)
        self.icon_thread.start()
    
    def run_icon(self):
        self.icon.run()
    
    def show_window(self):
        self.root.after(0, self._show_window)
    
    def _show_window(self):
        self.root.deiconify()
        self.root.state('normal')
        self.root.lift()
    
    def hide_window(self):
        self.root.withdraw()
    
    def quit_window(self):
        self.running = False
        self.icon.stop()
        self.root.after(0, self.root.destroy)
    
    def on_closing(self):
        self.hide_window()
    
    def choose_bg_color(self):
        # Change background color
        color = colorchooser.askcolor(title=self.translations[self.language]["bg_color"], color=self.bg_color)[1]
        if color:
            self.bg_color = color
            self.apply_colors()
    
    def choose_text_color(self):
        # Change text color
        color = colorchooser.askcolor(title=self.translations[self.language]["text_color"], color=self.text_color)[1]
        if color:
            self.text_color = color
            self.apply_colors()
    
    def change_language(self, lang):
        # Change language
        self.language = lang
        self.update_ui_language()
    
    def update_ui_language(self):
        # Change all text to new language
        self.root.title(self.translations[self.language]["app_title"])
        
        self.notebook.tab(0, text=self.translations[self.language]["macros_tab"])
        self.notebook.tab(1, text=self.translations[self.language]["settings_tab"])
        
        for widget in self.main_frame.grid_slaves():
            if isinstance(widget, ttk.Label) and widget.grid_info()["row"] == 0:
                if widget.grid_info()["column"] == 0:
                    widget.config(text=self.translations[self.language]["key_header"])
                elif widget.grid_info()["column"] == 1:
                    widget.config(text=self.translations[self.language]["text_header"])
                elif widget.grid_info()["column"] == 2:
                    widget.config(text=self.translations[self.language]["with_enter"])
        
        for key, button in self.key_buttons.items():
            if key in self.key_bindings and isinstance(self.key_bindings[key], str):
                button.config(text=self.key_bindings[key].upper())
            else:
                button.config(text=self.original_keys[key])
        
        for widget in self.settings_tab.winfo_children():
            if isinstance(widget, ttk.Frame):
                for child in widget.winfo_children():
                    if isinstance(child, ttk.Label) and ("color_settings" in child.cget("text") or "Colors" in child.cget("text") or "Farben" in child.cget("text") or "Colores" in child.cget("text")):
                        child.config(text=self.translations[self.language]["color_settings"], style="Settings.TLabel", anchor="center")
                    elif isinstance(child, ttk.Label) and ("language_settings" in child.cget("text") or "Language" in child.cget("text") or "Sprache" in child.cget("text") or "Idioma" in child.cget("text")):
                        child.config(text=self.translations[self.language]["language_settings"], style="Settings.TLabel", anchor="center")
                    elif isinstance(child, ttk.Frame):
                        for btn in child.winfo_children():
                            if isinstance(btn, ttk.Button):
                                if "Background" in btn.cget("text") or "Hintergrund" in btn.cget("text") or "Fondo" in btn.cget("text"):
                                    btn.config(text=self.translations[self.language]["bg_color"], style="Settings.TButton")
                                elif "Text" in btn.cget("text"):
                                    btn.config(text=self.translations[self.language]["text_color"], style="Settings.TButton")
                            elif isinstance(btn, ttk.Label) and ("Language" in btn.cget("text") or "Sprache" in btn.cget("text") or "Idioma" in btn.cget("text")):
                                btn.config(text="", style="Settings.TLabel")
                            elif isinstance(btn, ttk.Radiobutton):
                                if "English" in btn.cget("text") or "Englisch" in btn.cget("text") or "Inglés" in btn.cget("text"):
                                    btn.config(text=self.translations[self.language]["english"], style="Settings.TRadiobutton")
                                elif "German" in btn.cget("text") or "Deutsch" in btn.cget("text") or "Alemán" in btn.cget("text"):
                                    btn.config(text=self.translations[self.language]["german"], style="Settings.TRadiobutton")
                                elif "Spanish" in btn.cget("text") or "Spanisch" in btn.cget("text") or "Español" in btn.cget("text"):
                                    btn.config(text=self.translations[self.language]["spanish"], style="Settings.TRadiobutton")
        
        # Change system tray menu
        self.icon.menu = (
            pystray.MenuItem(self.translations[self.language]["open"], self.show_window),
            pystray.MenuItem(self.translations[self.language]["quit"], self.quit_window)
        )
        self.icon.title = self.translations[self.language]["app_title"]
    
    def apply_colors(self):
        # Change all colors
        style = ttk.Style()
        style.configure("TFrame", background=self.bg_color)
        style.configure("TLabel", background=self.bg_color, foreground=self.text_color)
        style.configure("TCheckbutton", background=self.bg_color, foreground=self.text_color)
        style.configure("TButton", background=self.bg_color, foreground=self.text_color)
        style.configure("TNotebook", background=self.bg_color)
        style.configure("TNotebook.Tab", background=self.bg_color, foreground="black")
        style.configure("Custom.TEntry",
                       fieldbackground=self.entry_bg,
                       foreground=self.text_color,
                       borderwidth=2,
                       relief="solid",
                       padding=5)
        
        style.configure("Settings.TLabel", background=self.bg_color, foreground="black")
        style.configure("Tab.TNotebook.Tab", background=self.bg_color, foreground="black")
        style.configure("Settings.TButton", background=self.bg_color, foreground="black")
        style.configure("Settings.TRadiobutton", background=self.bg_color, foreground="black")
        
        self.main_frame.configure(style="TFrame")
        self.settings_tab.configure(style="TFrame")
        self.root.configure(bg=self.bg_color)
    
    def setup_keyboard_hooks(self):
        # Listen for F-keys
        keyboard.unhook_all()
        
        for key, key_name in self.key_bindings.items():
            if isinstance(key_name, str):
                keyboard.on_press_key(key_name, lambda e, k=key: self.handle_key_press(e, k))
    
    def handle_key_press(self, event, macro_key):
        # When F-key is pressed, type text
        text = self.macro_texts[macro_key].get()
        if text:
            # Save old text, put new text, put back old text
            current_clipboard = pyperclip.paste()
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
            pyperclip.copy(current_clipboard)
            
            # Press enter if checked
            if self.enter_after[macro_key].get():
                pyautogui.press('enter')
    
    def start_key_binding(self, key):
        # Start to change key
        if self.waiting_for_key:
            return
        
        self.waiting_for_key = True
        self.current_key_binding = key
        
        self.key_buttons[key].config(text=self.translations[self.language]["press_key"])
        
        keyboard.unhook_all()
        keyboard.on_press(self.capture_key_press, suppress=True)
    
    def capture_key_press(self, event):
        # Get new key
        if not self.waiting_for_key or not self.current_key_binding:
            return
        
        key_name = event.name
        
        # Check if key is used
        if key_name.lower() in [binding.lower() for binding in self.key_bindings.values()]:
            self.key_buttons[self.current_key_binding].config(text=self.original_keys[self.current_key_binding])
        else:
            # Set new key
            self.key_buttons[self.current_key_binding].config(text=key_name.upper())
            self.key_bindings[self.current_key_binding] = key_name
            self.show_key_assigned_message()
        
        self.waiting_for_key = False
        self.current_key_binding = None
        
        keyboard.unhook_all()
        self.setup_keyboard_hooks()
    
    def show_key_assigned_message(self):
        # Show message when key is set
        message = tk.Toplevel(self.root)
        message.title("")
        message.geometry("200x50")
        message.transient(self.root)
        message.grab_set()
        
        # Put message in middle
        x = self.root.winfo_x() + (self.root.winfo_width() - 200) // 2
        y = self.root.winfo_y() + (self.root.winfo_height() - 50) // 2
        message.geometry(f"+{x}+{y}")
        
        ttk.Label(message, text=self.translations[self.language]["key_assigned"], font=("Arial", 12)).pack(expand=True, fill=tk.BOTH)
        
        # Make message go away
        self.root.after(1000, message.destroy)

# Start program
if __name__ == "__main__":
    root = tk.Tk()
    app = MacroTool(root)
    root.mainloop() 