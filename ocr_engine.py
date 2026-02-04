# FILE: engine.py
from PIL import ImageGrab, ImageOps, Image, ImageEnhance # <--- Aggiunto ImageEnhance
import pytesseract
from deep_translator import GoogleTranslator

# Configurazione Tesseract (Usa il percorso giusto per il tuo PC)
# Se hai seguito la guida automatica, potrebbe essere in AppData/Local/...
# Se non va, prova a rimettere quello di Program Files.
pytesseract.pytesseract.tesseract_cmd = r'C:\program Files\Tesseract-OCR\tesseract.exe'

def esegui_ocr(coordinate):
    """Fa lo screenshot e applica un filtro ad alto contrasto per isolare il testo"""
    try:
        # 1. CATTURA
        img = ImageGrab.grab(bbox=coordinate)
        
        # 2. INGRANDIMENTO (UPSCALE)
        width, height = img.size
        img = img.resize((width * 3, height * 3), Image.Resampling.LANCZOS)

        # 3. FILTRO "SUPERCLEAN" (Combinazione di Contrasto + Soglia)
        img = img.convert('L') # Scala di grigi
        
        # PASSO A: Aumentiamo il contrasto del 200%. 
        # Questo rende il testo grigio -> BIANCO e lo sfondo grigio -> NERO.
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0) 
        
        # PASSO B: Pulizia finale (Soglia)
        # Tutto ciò che è più scuro di 140 diventa Nero Assoluto.
        # Tutto ciò che è più chiaro diventa Bianco Assoluto.
        # 140 è il "punto dolce" per non cancellare il testo grigio chiaro.
        thresh = 140
        fn = lambda x : 255 if x > thresh else 0
        img = img.point(fn, mode='1')

        # 4. INVERSIONE E BORDI
        # Tesseract vuole testo nero su bianco
        img = ImageOps.invert(img.convert('RGB'))
        img = ImageOps.expand(img, border=20, fill='white')

        # Salva debug per controllo (Guardalo sempre se la traduzione è strana!)
        img.save("debug_visione.png")

        # 5. LETTURA (OCR)
        config = r'--oem 3 --psm 6'
        testo = pytesseract.image_to_string(img, lang='eng', config=config)
        
        # Pulizia stringa
        testo_pulito = testo.strip().replace('\n', ' ').replace('|', 'I')
        return testo_pulito

    except Exception as e:
        print(f"[Engine] Errore OCR: {e}")
        return None

def traduci(testo):
    if not testo:
        return None
    try:
        return GoogleTranslator(source='auto', target='it').translate(testo)
    except Exception as e:
        print(f"[Engine] Errore Traduzione: {e}")
        return "Errore connessione"