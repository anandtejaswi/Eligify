from io import BytesIO
from pdfminer.high_level import extract_text

def parse_pdf(input):
    if isinstance(input, (bytes, bytearray)):
        return extract_text(BytesIO(input))
    if hasattr(input, 'read'):
        return extract_text(input)
    if isinstance(input, str):
        with open(input, 'rb') as f:
            return extract_text(f)
    raise ValueError('Unsupported input')