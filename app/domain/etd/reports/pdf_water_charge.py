from copy import copy
from typing import List, Optional
from itertools import repeat

from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import cm, mm
from reportlab.platypus.flowables import Flowable
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Image, Table, TableStyle

from arrow import Arrow

from app.models.config import Config

from ....lib.formaters import _R, _M
from ...account.constants.service_account import AccountState
from ...account.mixins.service_account import ServiceAccountMixin
from ...etd.mixins.document import DocumentMixin
from ...etd.mixins.document.header import IssuerMixin, ReceptorMixin, TotalsMixin
from ...etd.mixins.document.detail import DetailMixin
from ...etd.constants.document import DocumentType, MeasurementType
from ...finances.mixins.charge import ChargeMixin
from ...users.mixins.user import UserMixin

from .utils import draw_rect_border, get_units, get_logo_image, get_sign_img, consumption_chart
from .constants import SZ_SINGLE, SZ_MULTIPLE, COLOR_PRIMARY, COLOR_WHITE, COLOR_DANGER


class WaterVoucherDocTemplate(BaseDocTemplate):
    """Override BaseDocTemplate for "progress bar" information"""

    def __init__(self, units: tuple[float], config: Optional[Config] = None, multiple: bool = False, *args, **kwargs):
        BaseDocTemplate.__init__(self, *args, **kwargs)
        self.config = config
        self.multiple = multiple
        self.wunit, self.hunit = units        
        
        self.setProgressCallBack(self.__onProgress)

    def __onProgress(self, prog_type, value):
        """Progress monitoring"""
        if self.user:        
            if prog_type == 'SIZE_EST':
                self.__size_est = value            
            elif prog_type == 'PROGRESS':
                self.config.massive_issue['construct-set-progress'] = int((value * 100 / self.__size_est))
                self.config.save()


def on_water_page(canvas: Canvas, doc):
    
    line_width = 1
    wunit = doc.wunit
    hunit = doc.hunit
    total_height = 100*hunit
    # - DOCTYPE FOLIO RECT    
    draw_rect_border(canvas, wunit, total_height-40*hunit, 100*wunit, color=COLOR_PRIMARY, line_width=line_width)
    draw_rect_border(canvas, wunit, total_height-64*hunit, 100*wunit, color=COLOR_PRIMARY, line_width=line_width)
    draw_rect_border(canvas, wunit, total_height-64*hunit, 100*wunit, color=COLOR_PRIMARY, line_width=line_width)
    draw_rect_border(canvas, wunit, total_height-80*hunit, 100*wunit, color=COLOR_PRIMARY, line_width=line_width)

    if doc.multiple:
        X_MOVE = 100*wunit + 1*cm
        draw_rect_border(canvas, X_MOVE+wunit, total_height-40*hunit, 100*wunit, color=COLOR_PRIMARY, line_width=line_width)
        draw_rect_border(canvas, X_MOVE+wunit, total_height-64*hunit, 100*wunit, color=COLOR_PRIMARY, line_width=line_width)
        draw_rect_border(canvas, X_MOVE+wunit, total_height-64*hunit, 100*wunit, color=COLOR_PRIMARY, line_width=line_width)
        draw_rect_border(canvas, X_MOVE+wunit, total_height-80*hunit, 100*wunit, color=COLOR_PRIMARY, line_width=line_width)

def get_frames(units: tuple[float], multiple: bool = False, show_border=0):
    
    # The sum of this must be 92 to have 8/4 spaces between areas.
    # - issuer-doc-id ------ 20
    # - receptor-consumption 18
    # - details ------------ 22
    # - last-13-totals ----- 14
    # - signature-total  --- 18
    
    wunit, hunit = units

    total_height = 100*hunit
    frame_header = Frame(wunit, total_height-20*hunit, 100*wunit, 0, 0, 0, 0, showBoundary=show_border)
    frame_receptor = Frame(wunit, total_height-40*hunit, 100*wunit, 0, 0, 0, 0, showBoundary=show_border)
    frame_details = Frame(wunit, total_height-64*hunit, 100*wunit, 0, 0, 0, 0, showBoundary=show_border)
    frame_last_13 = Frame(wunit, total_height-80*hunit, 100*wunit, 0, 0, 0, 0, showBoundary=show_border)
    frame_signature = Frame(wunit, hunit, 100*wunit, 0, 0, 0, 0, showBoundary=show_border)
    
    list_frames = [frame_header, frame_receptor, 
                   frame_details, frame_last_13, 
                   frame_signature]
    
    if multiple:
        X_MOVE = 100*wunit + 1*cm
        x_moved_frames = copy(list_frames)
        for frame in x_moved_frames:
            frame.x1 += X_MOVE        

        return list_frames + x_moved_frames

    return list_frames

def table_issuer(issuer: IssuerMixin, wunit:float, logo_image: Image = None) -> Table:
    
    data = [        
            [f'{issuer.name.upper()}'],
            [f'{issuer.business_activity}'],
            [f'DIRECCION: {issuer.address.address}, {issuer.address.commune}'],
            [f'RUT: {_R(issuer.rut)}']
    ]
    
    issuer_table = Table(data, colWidths=60*wunit)
    table_style = TableStyle()     
    issuer_table.setStyle(table_style)
    
    if logo_image:
        data[0].insert(0, [logo_image])
        
    return issuer_table

def table_doctype(doc_type: DocumentType, folio: int, table_account: Table, wunit: float) -> Table:
     
     data = [
          [f'R.U.T.: 65.600.354-7'],
          [f'{doc_type.name.replace("_", " ")}'],
          [f'Nº {str(folio).rjust(9, "0")}'],
          [f'S.I.I. - PUERTO VARAS'],
          [table_account]

     ]
     tablestyle = TableStyle([
          ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
          ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
     ])
     doctype_table = Table(data, colWidths=40*wunit)
     doctype_table.setStyle(tablestyle)
     return doctype_table

def table_account(public_id: str, wunit: float) -> Table:
     
     data = [['CUENTA SERVICIO', public_id]]  
     service_style = TableStyle(
          [('BACKGROUND', (0, 0), (-1, -1)),
           ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
           ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
           ])
                              
     service_table = Table(data,
                             colWidths=[17*wunit, 23*wunit])                                   
     service_table.setStyle(service_style)
                                   
     return service_table

def table_receptor(receptor: ReceptorMixin, units: tuple[float], htitle: float = 5*mm) -> Table:
     
     wunit, hunit = units
    # RECEPTOR HEIGHT 18%
     
     data = [
          ['Datos del receptor', ''],
          ['Razon Social',f': {receptor.name.upper()}'],
          ['R.U.T.', f': {_R(receptor.rut)}'],
          ['Direccion', f': {receptor.address.address.upper()}'],
          ['Comuna', f': {receptor.address.commune.upper()}'],
          ['Giro', f': {receptor.business_activity or ""}'],
          ['Fch Emision', f': {receptor.business_activity or ""}'],
     ]
     DATA_ROW_HEIGHT = (18*hunit - htitle) / (len(data) - 1)
     
     receptor_table = Table(data, 
                      colWidths=[14*wunit, 46*wunit], 
                      rowHeights=[htitle] + list(repeat(DATA_ROW_HEIGHT, len(data) - 1)))
     receptor_style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY),
                              ('SPAN', (0, 0), (-1, 0)),
                              ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                              ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
                                   ])
     receptor_table.setStyle(receptor_style)
     return receptor_table

def table_consumption(charge_payload: dict, units: tuple[float], htitle: float = 5*mm) -> Table:
     
    wunit, hunit = units
    # RECEPTOR HEIGHT 18%
     
    previous_measure, previous_date = f'{charge_payload["previous_reading_value"]}m³', f'{charge_payload["previous_date"]}'
    current_measure, current_date = f'{charge_payload["current_reading_value"]}m³', f'{charge_payload["current_date"]}'
    next_date, consumption = charge_payload['next_date'], f'{charge_payload["consumption"]}m³'
     
    data = [
          [f'Detalles de Consumo: {charge_payload.get("month")}', ''],
          ['Lectura Actual',f': {current_date} - {current_measure}'],
          ['Lectura Anterior', f': {previous_date} - {previous_measure}'],
          ['Consumo', f': {consumption}'],
          ['', ''],
          ['Proxima Lectura', f': {next_date}'],
     ]

    DATA_ROW_HEIGHT =  (18*hunit - htitle) / (len(data) - 1)
    consumption_table = Table(data, 
                         colWidths=[16*wunit, 24*wunit], 
                         rowHeights=[htitle] + list(repeat(DATA_ROW_HEIGHT, len(data) - 1)))
     
    consumption_style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY),
                              ('SPAN', (0, 0), (-1, 0)),
                              ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                              ('VALIGN', (0, 0), (-1, -1), 'TOP')
                                   ])
    consumption_table.setStyle(consumption_style)
     
    return consumption_table

def table_details(details: list[DetailMixin], total_amount: int, units: tuple[float], 
                          htitle: float = 5*mm)-> Table:
     
    wunit, hunit = units
    # RECEPTOR HEIGHT 22%
     
    col_widths = [34*wunit, 13*wunit, 16*wunit, 11*wunit, 11*wunit, 15*wunit]
    data = [['Detalle Facturacion', 'Unidades', 'Precio Un.', 'REC.', 'DESC', 'Total Parcial']]

    for detail in details:
        quantity = f'{int(detail.item_quantity)}m³' if detail.item_measurement == MeasurementType.METRO_CUBICO else str(int(detail.item_quantity))
        surcharge = _M(int(detail.surcharge_amount)) if detail.surcharge_amount else ''
        discount = _M(int(detail.discount_amount)) if detail.discount_amount else ''
          # SIEZE 8
        data.append([detail.item_name, str(quantity), _M(detail.item_unit_price), _M(surcharge), _M(discount), _M(detail.item_amount)])
    # SIZE 9 BOLD
    data.append(['SubTotal', '', '', '', '', _M(total_amount)])

    details_table = Table(data, colWidths=col_widths, rowHeights=htitle)
    datails_style = TableStyle([
          ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY),
          ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

     ])

    details_table.setStyle(datails_style)
    return details_table

def table_last_13(last_13: dict, units: tuple[float],  htitle: float = 5*mm) -> Table:
    # Height 14 
    
    wunit, hunit= units
     
    last_13_chart = consumption_chart(wunit, last_13)
    data = [
        ['Consumo últimos 13 meses'],
        [last_13_chart]
     ]
     
    last_13_table = Table(data, 
                          colWidths=60*wunit, 
                          rowHeights=[htitle, 14*hunit - htitle]
                          )

    last_13_style = TableStyle(
        [
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY),
            ('SPAN', (0, 0), (-1, 0)),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
            ])
    
    last_13_table.setStyle(last_13_style)
     
    return last_13_table

def table_totals(totals: TotalsMixin, expiration: Arrow, units: tuple[float], htitle: float = 5*mm) -> Table:
    # Height 14
    wunit, hunit = units
     
    data = [
        ['Totales', ''],
        ['MONTO EXENTO', _M(totals.exent_amount)],
        ['MONTO TOTAL', _M(totals.total_amount)],
        ['SALDO ANTERIOR', _M(totals.outstanding_balance)],
        ['FCH. VENCIMIENTO', f'{expiration.format("DD-MM-YYYY")}']
    ]
    DATA_ROW_HEIGHT = (14*hunit - htitle) / (len(data) - 1)
    totals_table = Table(data, 
                         colWidths=[22.2*wunit, 17.8*wunit], 
                         rowHeights=[htitle] + list(repeat(DATA_ROW_HEIGHT, (len(data) - 1))))

    totals_style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), COLOR_PRIMARY),
                              ('SPAN', (0, 0), (-1, 0)),
                              ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                              ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                              ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                              ('FONT', (0, 1), (-1, -1), 'Roboto Bold', 8.3),

                                   ])
    totals_table.setStyle(totals_style)
    return totals_table

def table_stamp(stamp: Image, resol_num: int, resol_year: int, units: tuple[float]) -> Table:
    # width 50% height 18
    wunit, hunit = units
    data = [
        [stamp],
        ['Timbre Electrónico SII'],
        [f'Res. {resol_num} de {resol_year} - Verifique documento en www.sii.cl']
        ]
    
    stamp_table = Table(data, colWidths=wunit)
    stamp_style = TableStyle()
    stamp_table.setStyle(stamp_style)
    
    return stamp_table    
    
def table_amount_to_be_paid(amount: int, units: tuple[float], cut_in_process: bool = False) -> Table:
     # width 50% height 18%
    wunit, hunit = units
    
    data = [
        [f'Total a pagar {_M(amount)}']
        ]
    
    if cut_in_process:
        data.append(['CORTE EN TRAMITE'])
    
    DATA_ROW_HEIGHT = (18*hunit) / 3
    amount_to_be_paid_table = Table(data,
                                 rowHeights=DATA_ROW_HEIGHT,
                                 colWidths=50*wunit)

    amount_to_be_paid_style = TableStyle(
        [
            ('BACKGROUND', (0, 0), (-1, 0), COLOR_DANGER),
            ('TEXTCOLOR', (0, 0), (-1, 0), COLOR_WHITE),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONT', (-1, -1), (-1, -1), 'Roboto Bold', 12),
            ])
    amount_to_be_paid_table.setStyle(amount_to_be_paid_style)
     
    return amount_to_be_paid_table

def get_charge_content(charge: ChargeMixin, units: tuple[float], tb_issuer: Table, resol_num: int, resol_year: int) -> list[Flowable]:

    wunit, hunit = units
    htitle = 5*mm
    # ----------- CHARGE DATA
    document: DocumentMixin = charge.etd.document
    receptor: ReceptorMixin = document.header.receptor
    service_account: ServiceAccountMixin = charge.service_account
    # ----------- HEADER - ISSUER DOC ID ACCOUNT
    tb_account = table_account(charge.service_account.public_id, wunit=wunit)
    data_issuer_doc_id = [
        [tb_issuer, 
         table_doctype(document.doctype, document.folio, tb_account, wunit)]
        ]
    tb_issuer_doc_id = Table(data_issuer_doc_id, colWidths=[60*wunit, 40*wunit])
    # --------- RECEPTOR CONSUMPTION DETAILS
    data_receptor_consumption = [
        [table_receptor(receptor, units, htitle), 
         table_consumption(charge.payload, units, htitle)]
        ]
    tb_receptor_consumption = Table(data_receptor_consumption, colWidths=[60*wunit, 40*wunit])
    # ---------- DETAILS
    tb_details = table_details(document.details, document.header.totals.total_amount, units, htitle)
    # ---------- LAST 13 - TOTALS
    data_last_13_totals = [
        [table_last_13(charge.payload.get('last_13'), units, htitle),
         table_totals(document.header.totals, charge.expires_at, units, htitle)]
    ]
    tb_last_13_totals = Table(data_last_13_totals, colWidths=[60*wunit, 40*wunit])
    # ---------- STAMP - AMOUNT TO BE PAID
    stamp = get_sign_img(document.xml_stampl)
    data_stamp_atbp = [
        [table_stamp(stamp, resol_num, resol_year, units),
         table_amount_to_be_paid(document.header.totals.amount_to_be_paid, units, service_account.state == AccountState.CUT_IN_PROCESS)]
    ]
    table_stamp_atbp = Table(data_stamp_atbp, colWidths=[50*wunit, 50*wunit])
    
    return [tb_issuer_doc_id, tb_receptor_consumption, tb_details, tb_last_13_totals, table_stamp_atbp]

async def get_all_content(charges: List[ChargeMixin], units: tuple[float], resol_num: int = 0, resol_year: int = 2021) -> list[Flowable]:
    
    wunit, hunit = units
    image = get_logo_image(48*wunit)
    
    tb_issuer = table_issuer(charges[0].etd.document.header.issuer, image)    
    content = []
    
    for charge in charges:
        charge_content = get_charge_content(charge, units, tb_issuer, resol_num, resol_year)
        content.extend(charge_content)
            
    return content

async def voucher_from_charges(output, charges: list[ChargeMixin], config: Optional[Config] = None, logo_path: str = None, 
                            office: str = 'puerto varas', resol_number: int = 0,
                            resol_year: int = 2021, show_border: int = 0):
    '''Gets pdf like data to given output, could be a file or file like object.'''
    units = get_units(SZ_SINGLE)
    
    if config:
        config.massive_issue['construct-set-progress'] = 0
        config.save()
    
    multiple = len(charges) > 1
    page_size = [SZ_SINGLE, SZ_MULTIPLE][multiple]

    doc = WaterVoucherDocTemplate(units, config, output, pagesize=page_size, leftMargin=0, rightMargin=0, topMargin=0,  bottomMargin=0)
    
    frames = get_frames(units, multiple=multiple, show_border=show_border)
    page_template = PageTemplate(frames=frames, onPage=on_water_page)
    doc.addPageTemplates(page_template)
       
    content = await get_all_content(charges, units, logo_path, office, resol_number, resol_year)
    doc.build(content)


