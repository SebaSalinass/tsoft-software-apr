from io import BytesIO

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import Color
from reportlab.lib.units import cm
from reportlab.platypus import Image
from pdf417 import encode, render_image

from .constants import LOGO_DIR, COLOR_BLACK


def consumption_chart(unit, data: list = None):
    drawing = Drawing(13*unit, 4*unit)
    data_values = [[list(info.values())[0] for info in data]]

    while len(data_values[0]) < 13:
        data_values[0].append(0)

    data_months = [list(info.keys())[0].title() for info in data]

    bc = VerticalBarChart()
    bc.x = unit
    bc.y = unit
    bc.width = (13*unit) - (2*unit)
    bc.height = (4*unit) - (1.5*unit)
    bc.data = data_values
    bc.strokeColor = COLOR_BLACK
    bc.bars.strokeWidth = 0
    bc.bars.strokeColor = None
    bc.barWidth = 3.5
    bc.strokeWidth = 0
    bc.valueAxis.labels.fontName = 'Roboto'
    bc.valueAxis.valueMin = 0
    bc.valueAxis.strokeWidth = .25
    bc.valueAxis.valueMax = max(data_values[0]) if max(data_values[0]) > 0 else 10
    bc.valueAxis.labels.fontSize = 5
    bc.valueAxis.labels.dx = -8
    bc.categoryAxis.strokeWidth = .3
    bc.categoryAxis.labels.fontName = 'Roboto'
    bc.categoryAxis.labels.fontSize = 6
    bc.categoryAxis.labels.boxAnchor = 'ne'
    bc.categoryAxis.labels.dx = 4
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.categoryNames = data_months
    drawing.add(bc)

    for i in range(len(data[0])):
        bc.bars[i].fillColor = COLOR_BLACK

    return drawing

def draw_rect_border(canvas: Canvas, x, y, width, height, line_width=0.07 * cm, color: Color = None) -> None:
    canvas.saveState()

    if color:
        canvas.setStrokeColor(color)

    canvas.setLineWidth(line_width)
    canvas.setLineCap(2)
    path = canvas.beginPath()
    
    path.moveTo(x, y)
    path.lineTo(x, y+height)
    path.lineTo(x+width, y+height)
    path.lineTo(x+width, y)
    path.lineTo(x, y)
    
    canvas.drawPath(path, stroke=1, fill=0)
    canvas.setLineWidth(1)
    
    return

def get_units(size: tuple[float], hmargin: float = 1*cm, vmargin: float = 1*cm,) -> tuple[float]:
    width, height = size
    width_unit = (width - 2*hmargin) / 100
    height_unit = (height - 2*vmargin) / 100    
    
    return (width_unit, height_unit)
    
def get_logo_image(width: float, align='LEFT') -> Image:

    image = Image(LOGO_DIR, hAlign=align)
    factor = image.imageWidth / width
    image.drawWidth = image.imageWidth / factor
    image.drawHeight = image.imageHeight / factor

    return image

def get_sign_img(secret: bytes, wunit: float) -> Image:

    data = encode(secret, 15, 4)
    img = render_image(data, scale=10, ratio=3, padding=0)
    data = BytesIO()
    img.save(data, format='png')
    data.seek(0)

    image_width = 45*wunit
    image = Image(data, hAlign='CENTER')

    factor = image.imageWidth / image_width
    image.drawWidth = image.imageWidth / factor
    image.drawHeight = image.imageHeight / factor

    return image