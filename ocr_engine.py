# FILE: ocr_engine.py
from PIL import ImageGrab, ImageOps, Image, ImageEnhance
import pytesseract
from deep_translator import GoogleTranslator

# TESSERACT CONFIGURATION
# Using the path from your provided file
pytesseract.pytesseract.tesseract_cmd = r'C:\program Files\Tesseract-OCR\tesseract.exe'

def perform_ocr(coordinates):
    """
    Captures screen area and applies high-contrast filters to isolate text.
    Current Logic: Contrast 2.0 + Fixed Threshold 140.
    """
    try:
        # 1. Capture
        img = ImageGrab.grab(bbox=coordinates)
        
        # 2. Upscale (3x Zoom)
        width, height = img.size
        img = img.resize((width * 3, height * 3), Image.Resampling.LANCZOS)

        # 3. Grayscale & Contrast
        img = img.convert('L') 
        
        # STEP A: Boost Contrast (200%)
        # Makes gray text brighter and background darker.
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0) 
        
        # STEP B: Thresholding (Cleaning)
        # 140 is the sweet spot to keep gray text visible while removing background.
        thresh = 140
        fn = lambda x : 255 if x > thresh else 0
        img = img.point(fn, mode='1')

        # 4. Invert (Black text on White background)
        img = ImageOps.invert(img.convert('RGB'))
        img = ImageOps.expand(img, border=20, fill='white')

        # Debug: Save what the robot sees
        img.save("debug_visione.png")

        # 5. OCR Reading
        config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(img, lang='eng', config=config)
        
        # Cleanup
        clean_text = text.strip().replace('\n', ' ').replace('|', 'I')
        return clean_text

    except Exception as e:
        print(f"[OCR Engine] Error: {e}")
        return None

def translate_text(text):
    if not text:
        return None
    try:
        return GoogleTranslator(source='auto', target='it').translate(text)
    except Exception as e:
        print(f"[OCR Engine] Translation Error: {e}")
        return "Connection Error"