from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.colors import Color
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle, StyleSheet1
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, FrameBreak, Image, Table, TableStyle

import os
from io import BytesIO
from pdf417 import render_image, encode
from typing import List, Union

from ....utils.formaters import _R, _M
from ...finance.mixins.charge import ChargeMixin
from ...etd.mixins.etd import ETDMixin

from config import BASEDIR

PROJ_DIR = os.path.join(BASEDIR, 'app')
FONT_DIR = os.path.join(PROJ_DIR, 'static/fonts')
IMG_DIR = os.path.join(PROJ_DIR, 'static/img')

# //////////// COLORS
COLOR_WHITE = (255 / 255, 255 / 255, 255 / 255)
COLOR_BLACK = (0 / 255, 0 / 255, 0 / 255)
COLOR_DARK_GRAY = (68 / 255, 68 / 255, 68 / 255)
COLOR_PRIMARY = (225 / 255, 70 / 255, 86 / 255)

# ////////// OTHER UNIT
OTHER_UNIT = LETTER[0] / 25
DOC_SIZE = (25 * OTHER_UNIT, 32 * OTHER_UNIT)


# /////////// FONT SIZES
OTHER_ISSUER_FONT_SIZE = 9
OTHER_ISSUERNAME_FONT_SIZE = 10
OTHER_SUBHEADER_FONT_SIZE = 8
OTHER_TABLE_TITLE_FONT_SIZE = 8.5
OTHER_TABLE_DATA_FONT_SIZE = 10

# /////////// ALIGNMENTS
ALIGN_HEADER_ISSUER = 0


def set_fonts():

    pdfmetrics.registerFont(TTFont('Roboto', os.path.join(FONT_DIR, 'Roboto-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('Roboto Bold', os.path.join(FONT_DIR, 'Roboto-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('Roboto Italic', os.path.join(FONT_DIR, 'Roboto-Italic.ttf')))
    pdfmetrics.registerFont(TTFont('Roboto BoldItalic', os.path.join(FONT_DIR, 'Roboto-BoldItalic.ttf')))
    pdfmetrics.registerFontFamily('Roboto', 'Roboto', 'Roboto Bold', 'Roboto Italic', 'Roboto BoldItalic')

def other_stylesheet(unit: float, ):

    para_style = {
        'header-issuer-name': {
            'fontName': 'Roboto Bold',
            'fontSize': OTHER_ISSUERNAME_FONT_SIZE,
            'leading': OTHER_ISSUERNAME_FONT_SIZE*1.2,
            'leftIndent': 0,
            'rightIndent': 0,
            'firstLineIndent': 0,
            'alignment': ALIGN_HEADER_ISSUER,
            'textColor': Color(*COLOR_DARK_GRAY),
            'spaceBefore': 10,

        },
        'header-issuer': {
            'fontName': 'Roboto',
            'fontSize': OTHER_ISSUER_FONT_SIZE,
            'leading': OTHER_ISSUER_FONT_SIZE*1.2,
            'leftIndent': 0,
            'rightIndent': 0,
            'firstLineIndent': 0,
            'alignment': ALIGN_HEADER_ISSUER,
            'textColor': Color(*COLOR_DARK_GRAY),
        },
        'doctype-folio': {
            'fontName': 'Roboto Bold',
            'fontSize': (OTHER_ISSUER_FONT_SIZE+1),
            'leading': (OTHER_ISSUER_FONT_SIZE+1)*1.2,
            'leftIndent': 0,
            'rightIndent': 0,
            'firstLineIndent': 0,
            'alignment': 1,
            'textColor': Color(*COLOR_BLACK),
        },
        'doctype-folio-subline': {
            'fontName': 'Roboto Bold',
            'fontSize': OTHER_ISSUER_FONT_SIZE-1.5,
            'leading': (OTHER_ISSUER_FONT_SIZE-1.5)*1.2,
            'leftIndent': 0,
            'rightIndent': 0,
            'firstLineIndent': 0,
            'alignment': 1,
            'textColor': Color(*COLOR_BLACK),
        },
        'table-title': {
            'fontName': 'Roboto Bold',
            'fontSize': (OTHER_ISSUER_FONT_SIZE),
            'leading': (OTHER_ISSUER_FONT_SIZE)*1.2,
            'leftIndent': 0,
            'rightIndent': 0,
            'firstLineIndent': 0,
            'alignment': 0,
            'textColor': Color(*COLOR_WHITE),
            'wordWrap': 0,

        },
        'table-data': {
            'fontName': 'Roboto',
            'fontSize': OTHER_TABLE_DATA_FONT_SIZE-1,
            'leading': OTHER_TABLE_DATA_FONT_SIZE-1,
            'leftIndent': 0,
            'rightIndent': 0,
            'firstLineIndent': 0,
            'alignment': 0,
            'textColor': Color(*COLOR_DARK_GRAY),
            'wordWrap': 0,

        },
        'header-account': {
            'fontName': 'Roboto Bold',
            'fontSize': 11.2,
            'leading': 11.2*1.2,
            'spaceBefore': 0,
            'spaceAfter': unit/2,
            'leftIndent': 0,
            'rightIndent': 5,
            'firstLineIndent': 0,
            'alignment': 2,
            'textColor': Color(*COLOR_BLACK),
        },
        'sign-footer': {
            'fontName': 'Roboto',
            'fontSize': 6,
            'leading': 6,
            'leftIndent': 0,
            'rightIndent': 0,
            'firstLineIndent': 0,
            'alignment': 1,
            'textColor': Color(*COLOR_BLACK),
            'wordWrap': 0,

        },
    }

    stylesheet = StyleSheet1()
    stylesheet.add(ParagraphStyle('HeaderIssuerName', **para_style['header-issuer-name']), 'header_issuer_name')
    stylesheet.add(ParagraphStyle('HeaderIssuer', **para_style['header-issuer']), 'header_issuer')
    stylesheet.add(ParagraphStyle('DoctypeFolio', **para_style['doctype-folio']), 'doctype_folio')
    stylesheet.add(ParagraphStyle('DoctypeFolioSubline', **para_style['doctype-folio-subline']), 'doctype_folio_subline')
    stylesheet.add(ParagraphStyle('TableTitle', **para_style['table-title']), 'table_title')
    stylesheet.add(ParagraphStyle('TableData', **para_style['table-data']), 'table_data')
    stylesheet.add(ParagraphStyle('SignFooter', **para_style['sign-footer']), 'sign_footer')

    return stylesheet

def draw_rect_border(canvas: Canvas, x: float, y: float, width: float, height: float, line_width: float=0.14*cm, color: Color = None):
        canvas.saveState()

        if color:
            canvas.setStrokeColorRGB(color)

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
        canvas.setStrokeColorRGB(0, 0, 0)
        canvas.saveState()

def logo_image(path: str = None, image_width: float = None, align: str = 'LEFT'):

    image = Image(path, hAlign=align)

    factor = image.imageWidth / image_width
    image.drawWidth = image.imageWidth / factor
    image.drawHeight = image.imageHeight / factor

    return image

def get_sign_img(etd: ETDMixin, image_width: float, align: str = 'CENTER'):
        
    secret = etd.document.xml_stamp

    data = encode(secret, 15, 4)
    img = render_image(data, scale=10, ratio=3, padding=0)
    data = BytesIO()
    img.save(data, format='png')
    data.seek(0)
    
    image = Image(data, hAlign=align)

    factor = image.imageWidth / image_width
    image.drawWidth = image.imageWidth / factor
    image.drawHeight = image.imageHeight / factor

    return image

def get_frames(unit: float, show_border=0):

    frame_issuer = Frame(unit, 26*unit, 15*unit, 5*unit, 0, 0, 0, 0, 'frame_issuer', show_border, overlapAttachedSpace=True)
    frame_doctype_folio = Frame(16*unit, 27*unit, 8*unit, 4*unit, 0, 0, 0, 0, 'frame_doctype_folio', show_border, overlapAttachedSpace=True)   
    frame_office = Frame(16*unit, 26*unit, 8*unit, 1*unit, 0, 0, 0, 0, 'frame_doctype_folio', show_border, overlapAttachedSpace=True)   

    frame_receptor = Frame(unit, 22*unit, 23*unit, 3*unit, 0, 0, 0, 0, 'frame_receptor', show_border, overlapAttachedSpace=True)    

    frame_details = Frame(unit, 13*unit, 23*unit, 8*unit, 0, 0, 0, 0, 'frame_details', show_border, overlapAttachedSpace=True)
    frame_references = Frame(unit, 9*unit, 23*unit, 3*unit, 0, 0, 0, 0, 'frame_references', show_border, overlapAttachedSpace=True)

    frame_sign = Frame(unit, 4*unit, 8*unit, 4*unit, 0, 0, 0, 7, 'frame_sign', show_border, overlapAttachedSpace=True)
    frame_assign = Frame(9*unit, 4*unit, 8*unit, 4*unit, 5, 5, 5, 5, 'frame_assign', show_border, overlapAttachedSpace=True)
    frame_total_amount = Frame(17*unit, 4*unit, 7*unit, 4*unit, 0, 0, 0, 0, 'frame_total_amount', show_border, overlapAttachedSpace=True)

    frame_footer = Frame(unit, 0, 23*unit, unit, 0, 0, 0, 0, 'frame_footer', show_border, overlapAttachedSpace=True)

    frame_details_title = Frame(unit, 21*unit, 23*unit, unit, 0, 0, 0, 0, 'frame_details_title', show_border, overlapAttachedSpace=True)
    frame_references_title = Frame(unit, 12*unit, 23*unit, unit, 0, 0, 0, 0, 'frame_details_title', show_border, overlapAttachedSpace=True)

    return [frame_issuer, frame_doctype_folio, frame_office, frame_receptor, 
        frame_details_title, frame_details, frame_references_title,
        frame_references, frame_sign, frame_assign, frame_total_amount, 
        frame_footer]

def get_charge_content(charge: Union[ChargeMixin, ETDMixin], stylesheet: StyleSheet1, unit: float, logo_image: Image = None, office='puerto varas',
                        resol_number: int = 0, resol_year: int = 2021, assignable: bool = False):
    if isinstance(charge, ETDMixin):
        etd = charge
    else:
        etd = charge.etd
    
    document = etd.document
    issuer = document.header.issuer
    receptor = document.header.receptor
    content_list = []

    # ---- LOGO IMAGE
    if logo_image:
        content_list.append(logo_image)

    # ---- ISSUER INFORMATION
    para_1 = Paragraph(f'{issuer.name.upper()}', style=stylesheet['header_issuer_name'])
    para_2 = Paragraph(f'GIRO: {issuer.business_activity.upper()}', style=stylesheet['header_issuer'])
    para_4 = Paragraph(f'RUT: {_R(issuer.rut)}', style=stylesheet['header_issuer'])
    para_3 = Paragraph(f'DIRECCION: {issuer.address.address.upper()}, {issuer.address.commune.upper()}', style=stylesheet['header_issuer'])

    content_list.extend([para_1, para_2, para_3, para_4, FrameBreak()])

    # ---- DOCTYPE FOLIO
    doctype_folio_data = [
        [Paragraph(f'R.U.T.: {_R(issuer.rut)}', style=stylesheet['doctype_folio'])],
        [Paragraph(f'{document.doc_type.name.replace("_", " ")}', style=stylesheet['doctype_folio'])],
        [Paragraph(f'Nº {str(document.folio).rjust(9, "0")}', style=stylesheet['doctype_folio'])],
    ]
    doctype_folio_table = Table(doctype_folio_data, colWidths=8*unit, rowHeights=4*unit/3)
    doctype_folio_style = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('VALIGN', (0, -1), (0, -1), 'TOP')
    ])

    doctype_folio_table.setStyle(doctype_folio_style)
    content_list.extend([doctype_folio_table, FrameBreak()])

    office_table = Table([[Paragraph(f'S.I.I. - {office.upper()}', style=stylesheet['doctype_folio_subline'])]], colWidths=8*unit, rowHeights=unit)
    office_table_style = TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    office_table.setStyle(office_table_style)
    content_list.extend([office_table, FrameBreak()])

    # ---- RECEPTOR INFORMATION
    row_heights = [unit/1.5, unit/2, unit/2, unit/2,unit/2]
    if receptor.address:
        address, commune, city = receptor.address.address, receptor.address.commune, receptor.address.city
    else:
        address, commune, city = '', '', ''


    receptor_data = [
        ['Detalles del receptor'],
        [Paragraph('Sr(es)', style=stylesheet['table_data']), Paragraph(f': {receptor.name.upper()}', style=stylesheet['table_data']),
        Paragraph('Direccion', style=stylesheet['table_data']), Paragraph(f': {address.upper()}', style=stylesheet['table_data'])],
        [Paragraph('R.U.T.', style=stylesheet['table_data']), Paragraph(f': {_R(receptor.rut.upper())}', style=stylesheet['table_data']),
        Paragraph('Ciudad', style=stylesheet['table_data']), Paragraph(f': {city.upper()}', style=stylesheet['table_data'])],
        [Paragraph('Giro', style=stylesheet['table_data']), Paragraph(f': {receptor.business_activity.upper() if receptor.business_activity else ""}', style=stylesheet['table_data']),
        Paragraph('Comuna', style=stylesheet['table_data']), Paragraph(f': {commune.upper()}', style=stylesheet['table_data'])],
        [Paragraph('Fecha Emisión', style=stylesheet['table_data']), Paragraph(f': {document.timestamp.format("DD-MM-YYYY")}', style=stylesheet['table_data']),'',''],        
    ]

    receptor_table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), Color(*COLOR_DARK_GRAY)),
        ('TEXTCOLOR', (0, 0), (-1, 0), Color(*COLOR_WHITE)),
        ('FONT', (0, 0), (-1, -1), 'Roboto Bold', 8.5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])

    receptor_table = Table(receptor_data, colWidths=[4*unit, 8*unit, 4*unit, 7*unit], rowHeights=row_heights)    
    receptor_table.setStyle(receptor_table_style)
    content_list.extend([receptor_table])

    # ---- DETAILS TITLE
    titles_style = TableStyle([        
        ('TEXTCOLOR', (0, 0), (-1, -1), Color(*COLOR_DARK_GRAY)),
        ('FONT', (0, 0), (-1, -1), 'Roboto Bold', 9.5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ])
    details_title_table = Table([['Detalles']], colWidths=23*unit, rowHeights=unit)
    details_title_table.setStyle(titles_style)
    content_list.extend([details_title_table, FrameBreak()])

    # ---- DETAILS DATA
    data_row_height = unit/2
    column_width = [7*unit, 3*unit, 3*unit, 3*unit, 3*unit, 4*unit]
    row_height = [unit/1.5]
    details_table_data = [['Detalle Facturacion','Unidades', 'Precio Un.', 'REC.', 'DESC.', 'Total Parcial']]

    for detail in document.details:
        row_height.append(data_row_height)

        quantity = f'{int(detail.item_quantity)}'
        surcharge = _M(int(detail.surcharge_amount)) if detail.surcharge_amount else ''
        discount = _M(int(detail.discount_amount)) if detail.discount_amount else ''

        details_table_data.append([Paragraph(f'{detail.item_name}', style=stylesheet['table_data']),
                            Paragraph(f'{quantity}', style=stylesheet['table_data']),
                            Paragraph(f'{_M(int(detail.item_unit_price))}', style=stylesheet['table_data']),
                            Paragraph(f'{surcharge}', style=stylesheet['table_data']),
                            Paragraph(f'{discount}', style=stylesheet['table_data']),
                            Paragraph(f'<para align="right">{_M(int(detail.item_amount))}</para>', style=stylesheet['table_data'])
                            ])
    
    details_table_data.append([Paragraph(f'<para size="9"><b>SubTotal</b></para>', style=stylesheet['table_data']), '', '', '', '',
                        Paragraph(f'<para size="9" align="right"><b>{_M(document.header.totals.total_amount)}</b></para>', style=stylesheet['table_data'])])
    row_height.append(data_row_height)

    details_table = Table(details_table_data, colWidths=column_width)
    details_table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), Color(*COLOR_DARK_GRAY)),
        ('TEXTCOLOR', (0, 0), (-1, 0), Color(*COLOR_WHITE)),
        ('FONT', (0, 0), (-1, -1), 'Roboto Bold', 8.5),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])

    details_table.setStyle(details_table_style)
    content_list.extend([details_table, FrameBreak()])

    # ---- REFERENCES TITLEE
    references_title_table = Table([['Referencias']], colWidths=23*unit, rowHeights=unit)
    references_title_table.setStyle(titles_style)
    content_list.extend([references_title_table, FrameBreak()])

    # ---- REFERENCES
    table_references_data = [['N', 'Tipo Documento', 'Folio', 'Fch. Emision', 'Razon']]
    for reference in document.references:
        table_references_data.append(
            [reference.line, reference.doc_type.name.replace('_', ' '), reference.folio_ref,
            reference.date_ref.format('DD-MM-YYYY'), reference.reason_ref.upper()])

    table_references_style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), Color(*COLOR_DARK_GRAY)),
                    ('TEXTCOLOR', (0, 0), (-1, 0), Color(*COLOR_WHITE)),
                    ('FONT', (0, 0), (-1, -1), 'Roboto Bold', 8.5),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER')])

    table_references = Table(table_references_data, colWidths=[unit, 10*unit, 3*unit, 3*unit, 6*unit])   
    table_references.setStyle(table_references_style)
    content_list.extend([table_references, FrameBreak()])


    # ---- SIGN
    sign_image = get_sign_img(etd, 7*unit)
    sign_para_1 = Paragraph('<para spacebefore="3">Timbre Electrónico SII</para>', style=stylesheet['sign_footer'])
    sign_para_2 = Paragraph(f'Res. {resol_number} de {resol_year} - Verifique documento en www.sii.cl', style=stylesheet['sign_footer'])
    
    content_list.extend([sign_image, sign_para_1, sign_para_2, FrameBreak()])

    # ---- ASSING
    if assignable:
        para_assgn_1 = Paragraph('NOMBRE:__________________________', style=stylesheet['header_issuer'])
        para_assgn_2 = Paragraph('RUT:_____________ FECHA:_________', style=stylesheet['header_issuer'])
        para_assgn_3 = Paragraph('RECINTO:_________ FIRMA:_________', style=stylesheet['header_issuer'])
        para_assgn_4 = Paragraph('''
                        El acuse de recibo que se declara en este acto, de acuerdo 
                        a lo dispuesto en la letra b) del Art. 4° y la letra c) del Art. 5° 
                        de la Ley 19.983, acredita que la entrega de mercadería(s) o servicio(s)''',
                            style=stylesheet['sign_footer'])
        para_assgn_5 = Paragraph('CEDIBLE', style=stylesheet['header_issuer_name'])

        content_list.extend([para_assgn_1, para_assgn_2, para_assgn_3, para_assgn_4, para_assgn_5, FrameBreak()])
    
    else:
        content_list.append(FrameBreak())
    
    # ---- TOTALS
    row_heights = [unit/1.5]
    totals_data = [[Paragraph('Totales', style=stylesheet['table_title']), '']]
    if document.header.totals.exent_amount:
        totals_data.append(['MONTO EXENTO', _M(document.header.totals.exent_amount)])
        row_heights.append(unit/1.5)
    if document.header.totals.net_amount:
        ['MONTO NETO', _M(document.header.totals.net_amount)]
        ['IVA (19.0%)', _M(document.header.totals.tax_amount)]
        row_heights.extend([unit/1.5, unit/1.5])
    
    totals_data.append(['MONTO TOTAL', _M(document.header.totals.total_amount)])
    row_heights.append(unit/1.5)

    totals_table = Table(totals_data, colWidths=[4*unit, 3*unit], rowHeights=row_heights)

    totals_table_style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), Color(*COLOR_DARK_GRAY)),
                            ('SPAN', (0, 0), (-1, 0)),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                            ('FONT', (0, 1), (-1, -1), 'Roboto', 8.3),
                            ('FONT', (0, -1), (-1, -1), 'Roboto Bold', 9.3),

                                ])
    totals_table.setStyle(totals_table_style)
    content_list.extend([totals_table, FrameBreak()])
    # ---- FOOTER
    footer = Paragraph('- Una solucion de <b>thonder-softwares</b> -', style=stylesheet['sign_footer'])
    content_list.extend([footer, FrameBreak()])

    return content_list

def get_all_content(charges: List[ChargeMixin], unit: float, logo_path: str = None, office: str = 'puerto varas',
                          resol_number: int = 0, resol_year: int = 2021, assignable: bool = False):
    image = None
    if logo_path:
        image = logo_image(logo_path, 8*unit)
    
    set_fonts()
    stylesheet = other_stylesheet(unit)
    content = []
    
    for charge in charges:
        charge_content = get_charge_content(charge, stylesheet, OTHER_UNIT, image, office, resol_number, resol_year, assignable)
        content.extend(charge_content)
            
    return content

def on_other_page(canvas: Canvas, doc):
        draw_rect_border(canvas, 16*OTHER_UNIT, 27*OTHER_UNIT, 8*OTHER_UNIT, 4*OTHER_UNIT) # folio doctype rectangle
        draw_rect_border(canvas, OTHER_UNIT, 22*OTHER_UNIT, 23*OTHER_UNIT, 3*OTHER_UNIT, COLOR_DARK_GRAY) # folio doctype rectangle
        draw_rect_border(canvas, OTHER_UNIT, 13*OTHER_UNIT, 23*OTHER_UNIT, 8*OTHER_UNIT, COLOR_DARK_GRAY) # folio doctype rectangle
        draw_rect_border(canvas, OTHER_UNIT, 9*OTHER_UNIT, 23*OTHER_UNIT, 3*OTHER_UNIT, COLOR_DARK_GRAY) # folio doctype rectangle

        draw_rect_border(canvas, OTHER_UNIT, 4*OTHER_UNIT, 16*OTHER_UNIT, 4*OTHER_UNIT, COLOR_DARK_GRAY) # folio doctype rectangle
        draw_rect_border(canvas, 17*OTHER_UNIT, 4*OTHER_UNIT, 7*OTHER_UNIT, 4*OTHER_UNIT, COLOR_DARK_GRAY) # folio doctype rectangle

def voucher_from_charges(output,  charges: List, user= None, logo_path: str = None, 
                            office: str = 'puerto varas', resol_number: int = 0,
                            resol_year: int = 2021, show_border=0,
                            assignable: bool = False):
    '''Gets pdf like data to given output, could be a file or file like object.'''

    if user:
        user.platform_data = {'other_set_progress': 1}
        user.save()

    doc = MyDocTemplate(user, output, pagesize=DOC_SIZE, leftMargin=0, rightMargin=0, topMargin=0,  bottomMargin=0)
    frames = get_frames(OTHER_UNIT, show_border=show_border)
    page_template = PageTemplate(frames=frames, onPage=on_other_page)
    doc.addPageTemplates(page_template)
       
    content = get_all_content(charges, OTHER_UNIT, logo_path, office, resol_number, resol_year, assignable)
    doc.build(content)


class MyDocTemplate(BaseDocTemplate):
    """Override BaseDocTemplate for "progress bar" information"""

    def __init__(self, user = None, *args, **kwargs):
        BaseDocTemplate.__init__(self, *args, **kwargs)

