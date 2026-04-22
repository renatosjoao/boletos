import pytesseract
from PIL import Image
from pdf2image import convert_from_path

def ocr_image(path):
    img = Image.open(path)
    return pytesseract.image_to_string(img)

def ocr_pdf(path):
    images = convert_from_path(path)
    texto = ""

    for img in images:
        texto += pytesseract.image_to_string(img)

    return texto