# FILE: main.py
import ctypes
import time
import threading
import tkinter as tk
import keyboard
import ocr_engine as engine  
import overlay_ui as ui      

# DPI Awareness Fix
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Store two separate areas now
        self.saved_dialogue_area = None
        self.saved_name_area = None
        
        self.auto_mode = False
        self.last_text_read = ""
        self.active_threshold = 150 
        
        # Initialize Overlay (Callback will be dynamic)
        self.selector = ui.SelectionOverlay(self.root, None)

        print("--- ZZZ OVERLAY TRANSLATOR (Name & Dialogue) ---")
        print("CTRL+ALT+S -> START SETUP (Select Name -> Then Dialogue)")
        print("CTRL+ALT+T -> Translate (Manual)")
        print("CTRL+ALT+A -> Toggle Auto-Mode")
        print("CTRL+ALT+D -> Switch Threshold Mode")

        keyboard.add_hotkey('ctrl+alt+s', self.start_selection_sequence)
        keyboard.add_hotkey('ctrl+alt+t', lambda: self.run_in_thread(self.translate_single))
        keyboard.add_hotkey('ctrl+alt+a', self.toggle_auto_mode)
        keyboard.add_hotkey('ctrl+alt+d', self.switch_mode)
        
        self.root.mainloop()

    def run_in_thread(self, func):
        threading.Thread(target=func, daemon=True).start()

    def switch_mode(self):
        if self.active_threshold == 150:
            self.active_threshold = 215
            print("\n>>> HIGH CONTRAST (215)")
        else:
            self.active_threshold = 150
            print("\n>>> STANDARD (150)")
        self.last_text_read = ""

    # --- SELECTION LOGIC (CHAINED) ---
    def start_selection_sequence(self):
        print("\n>>> STEP 1: Select CHARACTER NAME Area...")
        self.selector.callback = self.on_name_selected
        self.run_in_thread(lambda: self.selector.start("1. SELECT CHARACTER NAME"))

    def on_name_selected(self, coords):
        self.saved_name_area = coords
        print(f"Name Area Saved: {coords}")
        # Immediately start step 2
        print(">>> STEP 2: Select DIALOGUE TEXT Area...")
        self.selector.callback = self.on_dialogue_selected
        # Small delay to prevent accidental clicks
        time.sleep(0.5)
        self.run_in_thread(lambda: self.selector.start("2. SELECT DIALOGUE TEXT"))

    def on_dialogue_selected(self, coords):
        self.saved_dialogue_area = coords
        print(f"Dialogue Area Saved: {coords}")
        print(">>> SETUP COMPLETE! You can now use Auto-Mode.")
        self.last_text_read = "" 
        self.run_in_thread(self.translate_single)

    # --- MAIN LOGIC ---
    def toggle_auto_mode(self):
        self.auto_mode = not self.auto_mode
        if self.auto_mode:
            print("\n--- 🤖 AUTO-MODE ON ---")
            self.run_in_thread(self.auto_loop)
        else:
            print("\n--- 🛑 AUTO-MODE OFF ---")

    def auto_loop(self):
        while self.auto_mode:
            if self.saved_dialogue_area:
                try:
                    # 1. Read Dialogue (To detect changes)
                    new_text = engine.perform_ocr(self.saved_dialogue_area, self.active_threshold)
                    
                    if (new_text and 
                        len(new_text) > 5 and 
                        new_text != self.last_text_read):
                        
                        # 2. Read Name (Only when dialogue changes)
                        name_text = ""
                        if self.saved_name_area:
                            name_text = engine.perform_ocr(self.saved_name_area, self.active_threshold)
                            if name_text: 
                                name_text = name_text.replace('\n', ' ').strip()
                        
                        print(f"[{name_text}] Says: {new_text[:15]}...")
                        self.last_text_read = new_text
                        
                        # 3. Translate Dialogue ONLY
                        translated_text = engine.translate_text(new_text)
                        
                        # 4. Show UI (Pass Name + Translated Text)
                        self.root.after(0, lambda: ui.show_popup(self.root, translated_text, name_header=name_text))
                        
                except Exception as e:
                    print(f"Loop Error: {e}")
            
            time.sleep(1.0) 

    def translate_single(self):
        if not self.saved_dialogue_area:
            print("⚠️ Setup not complete. Press CTRL+ALT+S")
            return

        print("Manual Translation...")
        
        # Read Name
        name_text = ""
        if self.saved_name_area:
            name_text = engine.perform_ocr(self.saved_name_area, self.active_threshold)
        
        # Read & Translate Text
        text = engine.perform_ocr(self.saved_dialogue_area, self.active_threshold)
        
        if text:
            self.last_text_read = text 
            translation = engine.translate_text(text)
            self.root.after(0, lambda: ui.show_popup(self.root, translation, name_header=name_text))
        else:
            print("No text found.")

if __name__ == "__main__":
    App()