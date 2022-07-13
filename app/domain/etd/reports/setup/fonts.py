import os

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from ..constants import FONT_DIR

def setup_fonts() -> None:

    pdfmetrics.registerFont(TTFont('Roboto Regular', os.path.join(FONT_DIR, 'Roboto-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('Roboto Bold', os.path.join(FONT_DIR, 'Roboto-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('Roboto Italic', os.path.join(FONT_DIR, 'Roboto-Italic.ttf')))
    pdfmetrics.registerFont(TTFont('Roboto BoldItalic', os.path.join(FONT_DIR, 'Roboto-BoldItalic.ttf')))
    pdfmetrics.registerFontFamily('Roboto', 'Roboto', 'Roboto Bold', 'Roboto Italic', 'Roboto BoldItalic')
    
    return