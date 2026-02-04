# FILE: ui.py
import tkinter as tk

popup_corrente = None

class OverlaySelezione:
    """(Questa parte rimane identica)"""
    def __init__(self, root, callback_fine_selezione):
        self.root = root
        self.callback = callback_fine_selezione
        self.window = None
        self.canvas = None
        self.start_x = 0
        self.start_y = 0
        self.rect = None

    def avvia(self):
        if self.window: return
        self.window = tk.Toplevel(self.root)
        self.window.attributes('-fullscreen', True, '-alpha', 0.3, '-topmost', True)
        self.window.configure(bg='black', cursor="cross")
        self.canvas = tk.Canvas(self.window, cursor="cross", bg="grey11")
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<ButtonPress-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.window.bind("<Escape>", lambda e: self.chiudi())

    def chiudi(self):
        if self.window:
            self.window.destroy()
            self.window = None

    def _on_click(self, event):
        self.start_x, self.start_y = event.x, event.y
        self.rect = self.canvas.create_rectangle(event.x, event.y, event.x, event.y, outline='red', width=2)

    def _on_drag(self, event):
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def _on_release(self, event):
        x1, y1 = self.start_x, self.start_y
        x2, y2 = event.x, event.y
        left, top = min(x1, x2), min(y1, y2)
        right, bottom = max(x1, x2), max(y1, y2)
        self.chiudi()
        if (right - left) > 10 and (bottom - top) > 10:
            self.callback((left, top, right, bottom))

def chiudi_tutti_i_popup(event=None):
    global popup_corrente
    if popup_corrente:
        try:
            popup_corrente.destroy()
        except:
            pass
        popup_corrente = None

def mostra_popup(root, testo, x_inutile, y_inutile):
    """Mostra testo fluttuante SENZA SFONDO con bordo (Outline)"""
    global popup_corrente
    chiudi_tutti_i_popup()
    
    popup = tk.Toplevel(root)
    popup_corrente = popup 
    popup.overrideredirect(True)
    popup.attributes('-topmost', True)

    # --- IL TRUCCO DEL QUASI NERO ---
    # 1. Impostiamo lo sfondo su Nero Puro
    PURE_BLACK = "#000000"
    # 2. Impostiamo il bordo del testo su un grigio scurissimo (sembra nero all'occhio)
    OUTLINE_COLOR = "#111111" 
    
    popup.configure(bg=PURE_BLACK)
    # 3. Rendiamo trasparente SOLO il Nero Puro. 
    # Il bordo #111111 rimarrà visibile!
    popup.wm_attributes("-transparentcolor", PURE_BLACK)

    # Canvas per disegnare
    canvas = tk.Canvas(popup, bg=PURE_BLACK, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # Configurazione Font
    screen_width = root.winfo_screenwidth()
    max_width = 1200
    FONT = ("Segoe UI Black", 16, "bold") # Font bello cicciotto

    # Calcoliamo il centro provvisorio
    cx = max_width / 2
    cy = 100 # Altezza provvisoria

    # --- DISEGNO DEL BORDO (OUTLINE) ---
    # Disegniamo il testo 8 volte spostato leggermente per fare il bordo spesso
    offsets = [(-2, -2), (-2, 0), (-2, 2), 
               (0, -2),           (0, 2), 
               (2, -2),  (2, 0),  (2, 2)]
    
    # Lista per salvare gli ID degli oggetti disegnati
    items = []
    
    # 1. Disegna l'ombra/bordo
    for ox, oy in offsets:
        item = canvas.create_text(cx + ox, cy + oy, text=testo, font=FONT, 
                                  fill=OUTLINE_COLOR, width=max_width, justify="center")
        items.append(item)

    # 2. Disegna il testo bianco sopra
    text_item = canvas.create_text(cx, cy, text=testo, font=FONT, 
                                   fill="white", width=max_width, justify="center")
    items.append(text_item)

    # --- RIDIMENSIONAMENTO DINAMICO ---
    # Chiediamo al Canvas: "Quanto spazio occupa veramente tutto questo testo?"
    popup.update_idletasks() # Forza il calcolo grafico
    bbox = canvas.bbox("all") # Prende il rettangolo che contiene tutto (x1, y1, x2, y2)

    if bbox:
        # Calcoliamo larghezza e altezza reali + un po' di margine (padding)
        text_width = bbox[2] - bbox[0] + 20
        text_height = bbox[3] - bbox[1] + 20
        
        # Spostiamo tutto il testo in modo che parta bene dall'alto (padding 10px)
        # Calcoliamo di quanto spostare
        y_offset = 10 - bbox[1] 
        x_offset = 10 - bbox[0]
        for item in items:
            canvas.move(item, x_offset, y_offset)

        # Ora ridimensioniamo la finestra esattamente su misura
        x_pos = (screen_width - text_width) // 2
        y_pos = 60 # Distanza dall'alto
        popup.geometry(f"{text_width}x{text_height}+{x_pos}+{y_pos}")

    # Chiudi al click
    canvas.bind("<Button-1>", chiudi_tutti_i_popup)