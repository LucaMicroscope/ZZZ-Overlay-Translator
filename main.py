# FILE: main.py
import ctypes
import time
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

import tkinter as tk
import keyboard
import engine
import ui
import threading 

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()
        
        self.area_salvata = None
        self.auto_mode = False
        self.ultimo_testo_letto = ""
        
        self.selettore = ui.OverlaySelezione(self.root, self.on_area_selezionata)

        print("--- TRADUTTORE ZZZ (Cinema Mode) ---")
        print("CTRL+ALT+S -> Seleziona Area Dialogo")
        print("CTRL+ALT+T -> Traduci (Manuale)")
        print("CTRL+ALT+A -> Auto-Mode")

        keyboard.add_hotkey('ctrl+alt+s', lambda: self.lancia_in_thread(self.selettore.avvia))
        keyboard.add_hotkey('ctrl+alt+t', lambda: self.lancia_in_thread(self.traduci_singolo))
        keyboard.add_hotkey('ctrl+alt+a', self.toggle_auto_mode)
        
        self.root.mainloop()

    def lancia_in_thread(self, funzione):
        threading.Thread(target=funzione, daemon=True).start()

    def on_area_selezionata(self, coordinate):
        self.area_salvata = coordinate
        print(f"Area salvata: {coordinate}")
        self.ultimo_testo_letto = "" 
        self.lancia_in_thread(self.traduci_singolo)

    def toggle_auto_mode(self):
        self.auto_mode = not self.auto_mode
        if self.auto_mode:
            print("\n--- 🤖 AUTO-MODE ON ---")
            self.lancia_in_thread(self.loop_automatico)
        else:
            print("\n--- 🛑 AUTO-MODE OFF ---")

    def loop_automatico(self):
        while self.auto_mode:
            if self.area_salvata:
                try:
                    # Non chiudiamo più i popup qui.
                    # Il popup è in alto, l'area è in basso. Nessun conflitto!
                    
                    nuovo_testo = engine.esegui_ocr(self.area_salvata)
                    
                    if (nuovo_testo and 
                        len(nuovo_testo) > 5 and 
                        nuovo_testo != self.ultimo_testo_letto):
                        
                        print(f"Cambio rilevato: {nuovo_testo[:20]}...")
                        self.ultimo_testo_letto = nuovo_testo
                        
                        testo_ita = engine.traduci(nuovo_testo)
                        
                        # Passiamo x, y ma ui.py li ignorerà
                        x, y = self.area_salvata[0], self.area_salvata[1]
                        self.root.after(0, lambda: ui.mostra_popup(self.root, testo_ita, x, y))
                        
                except Exception as e:
                    print(f"Errore loop: {e}")
            
            time.sleep(1.0) 

    def traduci_singolo(self):
        if not self.area_salvata:
            print("⚠️ Seleziona prima un'area!")
            return

        # RIMOSSO: self.root.after(0, ui.chiudi_tutti_i_popup)
        # Non serve più chiudere, perché la traduzione appare in alto
        # e non copre il testo del gioco!

        print("Traduzione manuale...")
        testo = engine.esegui_ocr(self.area_salvata)
        
        if testo:
            self.ultimo_testo_letto = testo 
            trad = engine.traduci(testo)
            x, y = self.area_salvata[0], self.area_salvata[1]
            self.root.after(0, lambda: ui.mostra_popup(self.root, trad, x, y))
        else:
            print("Nessun testo trovato.")

if __name__ == "__main__":
    App()