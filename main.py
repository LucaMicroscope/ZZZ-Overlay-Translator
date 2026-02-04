# FILE: main.py
import ctypes
import time
import threading
import tkinter as tk
import keyboard

# Updated imports to match new filenames
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
        
        self.saved_area = None
        self.auto_mode = False
        self.last_text_read = ""
        
        self.selector = ui.SelectionOverlay(self.root, self.on_area_selected)

        print("--- ZZZ OVERLAY TRANSLATOR (Cinema Mode) ---")
        print("CTRL+ALT+S -> Select Dialogue Area")
        print("CTRL+ALT+T -> Translate (Manual)")
        print("CTRL+ALT+A -> Toggle Auto-Mode")

        keyboard.add_hotkey('ctrl+alt+s', lambda: self.run_in_thread(self.selector.start))
        keyboard.add_hotkey('ctrl+alt+t', lambda: self.run_in_thread(self.translate_single))
        keyboard.add_hotkey('ctrl+alt+a', self.toggle_auto_mode)
        
        self.root.mainloop()

    def run_in_thread(self, func):
        threading.Thread(target=func, daemon=True).start()

    def on_area_selected(self, coordinates):
        self.saved_area = coordinates
        print(f"Area saved: {coordinates}")
        self.last_text_read = "" 
        self.run_in_thread(self.translate_single)

    def toggle_auto_mode(self):
        self.auto_mode = not self.auto_mode
        if self.auto_mode:
            print("\n--- 🤖 AUTO-MODE ON ---")
            self.run_in_thread(self.auto_loop)
        else:
            print("\n--- 🛑 AUTO-MODE OFF ---")

    def auto_loop(self):
        while self.auto_mode:
            if self.saved_area:
                try:
                    # OCR Check
                    new_text = engine.perform_ocr(self.saved_area)
                    
                    if (new_text and 
                        len(new_text) > 5 and 
                        new_text != self.last_text_read):
                        
                        print(f"Change detected: {new_text[:20]}...")
                        self.last_text_read = new_text
                        
                        translated_text = engine.translate_text(new_text)
                        
                        # Show popup (coordinates passed but ignored by UI for fixed position)
                        x, y = self.saved_area[0], self.saved_area[1]
                        self.root.after(0, lambda: ui.show_popup(self.root, translated_text, x, y))
                        
                except Exception as e:
                    print(f"Loop Error: {e}")
            
            time.sleep(1.0) 

    def translate_single(self):
        if not self.saved_area:
            print("⚠️ Please select an area first!")
            return

        print("Manual Translation...")
        text = engine.perform_ocr(self.saved_area)
        
        if text:
            self.last_text_read = text 
            translation = engine.translate_text(text)
            x, y = self.saved_area[0], self.saved_area[1]
            self.root.after(0, lambda: ui.show_popup(self.root, translation, x, y))
        else:
            print("No text found.")

if __name__ == "__main__":
    App()