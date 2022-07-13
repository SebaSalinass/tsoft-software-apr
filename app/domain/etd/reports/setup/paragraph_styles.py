from ..constants import (WATER_HEADER_FONT_SIZE, WATER_SUBHEADER_FONT_SIZE,
                        WATER_TABLE_TITLE_FONT_SIZE, COLOR_DRAK_GRAY, COLOR_BLACK, 
                        COLOR_WHITE)
from reportlab.lib.styles import ParagraphStyle, StyleSheet1

PARA_WATER_CHARGE_STYLE = {
        
        'issuer-name': {
            'spaceBefore': 3,
            'spaceAfter': 3,
            'fontName': 'Roboto Bold',
            'fontSize': WATER_HEADER_FONT_SIZE,
            'leading': WATER_HEADER_FONT_SIZE * 1.2,
            'leftIndent': 0,
            'rightIndent': 0,
            'firstLineIndent': 0,
            'alignment': 0,
            'textColor': COLOR_DRAK_GRAY,
        },
        'business-activity': {
            'fontName': 'Roboto',
            'fontSize': WATER_SUBHEADER_FONT_SIZE,
            'leading': WATER_SUBHEADER_FONT_SIZE * 1.2,
            'leftIndent': 0,
            'rightIndent': 0,
            'firstLineIndent': 0,
            'alignment': 0,
            'textColor': COLOR_DRAK_GRAY,
        },
        'issuer-information': {
            'fontName': 'Roboto Bold',
            'fontSize': WATER_SUBHEADER_FONT_SIZE,
            'leading': WATER_SUBHEADER_FONT_SIZE * 1.2,
            'leftIndent': 0,
            'rightIndent': 0,
            'firstLineIndent': 0,
            'alignment': 0,
            'textColor': COLOR_DRAK_GRAY,
        },
        'doctype-folio': {
            'fontName': 'Roboto Bold',
            'fontSize': WATER_HEADER_FONT_SIZE,
            'leading': WATER_HEADER_FONT_SIZE * 1.2,
            'leftIndent': 0,
            'rightIndent': 0,
            'firstLineIndent': 0,
            'alignment': 1,
            'textColor': COLOR_BLACK,
        },
        'doctype-folio-subline': {
            'fontName': 'Roboto Bold',
            'fontSize': WATER_HEADER_FONT_SIZE - 1.5,
            'leading': (WATER_HEADER_FONT_SIZE - 1.5) * 1.2,
            'leftIndent': 0,
            'rightIndent': 0,
            'firstLineIndent': 0,
            'alignment': 1,
            'textColor': COLOR_BLACK,
        },
        'serviceaccount-label': {
            'fontName': 'Roboto Bold',
            'fontSize': WATER_HEADER_FONT_SIZE - 1.5,
            'leading': (WATER_HEADER_FONT_SIZE - 1.5) * 1.2,
            'leftIndent': 0,
            'rightIndent': 0,
            'firstLineIndent': 0,
            'alignment': 1,
            'textColor': COLOR_WHITE,
        },
        'serviceaccount-data': {
            'fontName': 'Roboto Bold',
            'fontSize': WATER_HEADER_FONT_SIZE - 1,
            'leading': (WATER_HEADER_FONT_SIZE - 1) * 1.2,
            'leftIndent': 0,
            'rightIndent': 6,
            'firstLineIndent': 0,
            'alignment': 1,
            'textColor': COLOR_BLACK,
            'backColor': COLOR_WHITE,
            'borderPadding': 4,
        },
        'table-title': {
            'fontName': 'Roboto Bold',
            'fontSize': WATER_TABLE_TITLE_FONT_SIZE,
            'leading': (WATER_TABLE_TITLE_FONT_SIZE) * 1.2,
            'leftIndent': 0,
            'rightIndent': 0,
            'firstLineIndent': 0,
            'alignment': 0,
            'textColor': COLOR_WHITE,
            'wordWrap': 0,

        },
        'table-data': {
            'fontName': 'Roboto',
            'fontSize': WATER_TABLE_TITLE_FONT_SIZE - 1,
            'leading': WATER_TABLE_TITLE_FONT_SIZE - 1,
            'leftIndent': 0,
            'rightIndent': 0,
            'firstLineIndent': 0,
            'alignment': 0,
            'textColor': COLOR_DRAK_GRAY,
            'wordWrap': 0,

        },
        'sign-footer': {
            'fontName': 'Roboto',
            'fontSize': 6,
            'leading': 6,
            'leftIndent': 0,
            'rightIndent': 0,
            'firstLineIndent': 0,
            'alignment': 1,
            'textColor': COLOR_BLACK,
            'wordWrap': 0,

        }
    }

def get_water_charge_stylesheet() -> StyleSheet1:

    stylesheet = StyleSheet1()
    
    for para_style_name, style_dict in PARA_WATER_CHARGE_STYLE.items():
        paragraph_name = para_style_name.replace('-',' ').title().replace(' ','')
        paragraph_alias = para_style_name.replace('-','_')
        stylesheet.add(ParagraphStyle(paragraph_name, **style_dict), paragraph_alias)

    return stylesheet