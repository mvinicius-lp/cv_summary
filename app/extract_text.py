import io
import cv2
import fitz
import easyocr
import numpy as np

reader = easyocr.Reader(['en', 'pt'])

def extract_text_from_pdf(pdf_file) -> str | dict:
    try:
        pdf_bytes = pdf_file.file.read()
        pdf_document = fitz.open(stream=io.BytesIO(pdf_bytes), filetype="pdf")
        text = ""
        for page in pdf_document:
            text += page.get_text()
        return text
    except Exception as e:
        return {"error": f"An error occurred: {str(e)}"}

def extract_text_from_image(contents: bytes) -> str | dict:
    try:
        np_arr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if image is None:
            return {"error": "Invalid image format"}
        result = reader.readtext(image, detail=0)
        return " ".join(result)
    except Exception as e:
        return {"error": f"An error occurred during OCR: {str(e)}"}
