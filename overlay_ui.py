# FILE: overlay_ui.py
import tkinter as tk

current_popup = None

class SelectionOverlay:
    """
    Transparent full-screen overlay to select the screen area with the mouse.
    """
    def __init__(self, root, on_selection_callback):
        self.root = root
        self.callback = on_selection_callback
        self.window = None
        self.canvas = None
        self.start_x = 0
        self.start_y = 0
        self.rect = None

    def start(self):
        if self.window: return
        
        self.window = tk.Toplevel(self.root)
        self.window.attributes('-fullscreen', True, '-alpha', 0.3, '-topmost', True)
        self.window.configure(bg='black', cursor="cross")
        
        self.canvas = tk.Canvas(self.window, cursor="cross", bg="grey11")
        self.canvas.pack(fill="both", expand=True)
        
        self.canvas.bind("<ButtonPress-1>", self._on_click)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.window.bind("<Escape>", lambda e: self.close())

    def close(self):
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
        
        self.close()
        
        # Prevent accidental micro-clicks
        if (right - left) > 10 and (bottom - top) > 10:
            self.callback((left, top, right, bottom))

def close_all_popups(event=None):
    global current_popup
    if current_popup:
        try:
            current_popup.destroy()
        except:
            pass
        current_popup = None

def show_popup(root, text, x_ignored, y_ignored):
    """
    Displays the translated text in a Cinema-Style floating window.
    Features: No background (Chroma Key), Black Outline, Widescreen.
    """
    global current_popup
    close_all_popups()
    
    popup = tk.Toplevel(root)
    current_popup = popup 
    popup.overrideredirect(True)
    popup.attributes('-topmost', True)

    # --- CHROMA KEY TRICK ---
    PURE_BLACK = "#000000"
    OUTLINE_COLOR = "#111111" 
    
    popup.configure(bg=PURE_BLACK)
    # Makes Pure Black transparent
    popup.wm_attributes("-transparentcolor", PURE_BLACK)

    canvas = tk.Canvas(popup, bg=PURE_BLACK, highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    # Font Config
    screen_width = root.winfo_screenwidth()
    max_width = 1200
    FONT = ("Segoe UI Black", 16, "bold") 

    # Temporary center
    cx = max_width / 2
    cy = 100 

    # --- DRAW OUTLINE ---
    offsets = [(-2, -2), (-2, 0), (-2, 2), 
               (0, -2),           (0, 2), 
               (2, -2),  (2, 0),  (2, 2)]
    
    items = []
    
    # 1. Draw Outline (Dark Grey/Black)
    for ox, oy in offsets:
        item = canvas.create_text(cx + ox, cy + oy, text=text, font=FONT, 
                                  fill=OUTLINE_COLOR, width=max_width, justify="center")
        items.append(item)

    # 2. Draw Main Text (White)
    text_item = canvas.create_text(cx, cy, text=text, font=FONT, 
                                   fill="white", width=max_width, justify="center")
    items.append(text_item)

    # --- DYNAMIC RESIZING ---
    popup.update_idletasks() 
    bbox = canvas.bbox("all") 

    if bbox:
        text_width = bbox[2] - bbox[0] + 20
        text_height = bbox[3] - bbox[1] + 20
        
        y_offset = 10 - bbox[1] 
        x_offset = 10 - bbox[0]
        for item in items:
            canvas.move(item, x_offset, y_offset)

        # Center horizontally, fixed Y position
        x_pos = (screen_width - text_width) // 2
        y_pos = 60 
        popup.geometry(f"{text_width}x{text_height}+{x_pos}+{y_pos}")

    # Close on click
    canvas.bind("<Button-1>", close_all_popups)