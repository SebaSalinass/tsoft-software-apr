from dataclasses import dataclass, field
from typing import Optional

from arrow import Arrow
import lxml.etree as ET

from .header import HeaderMixin
from .header.id import IDMixin
from .header.receptor import ReceptorMixin
from .header.issuer import IssuerMixin
from .header.totals import TotalsMixin
from .detail import DetailMixin
from .sub_totals import SubTotalMixin
from .glob_dsc_sur import GlobalDiscountSurchargeMixin
from .references import ReferenceMixin
from .comissions import CommissionsMixin

from ..fac import FacHandlerMixin
from ...constants.document import ReferenceCode, DocumentType


@dataclass
class DocumentMixin:

    header: HeaderMixin
    details: list[DetailMixin] = field(repr=False, default_factory=list)

    # Opcional ----------------------------------------------------------------
    informative_subtotals: list[SubTotalMixin] =  field(repr=False, default_factory=list)
    global_discount_surcharges: list[GlobalDiscountSurchargeMixin] =  field(repr=False, default_factory=list)
    references: list[ReferenceMixin] =  field(repr=False, default_factory=list)
    commission_other_charges: list[CommissionsMixin] =  field(repr=False, default_factory=list)

    xml_stamp: Optional[bytes] = field(repr=False, default=None)
    xml_data: Optional[bytes] = field(repr=False, default=None)

    @property
    def timestamp(self) -> Arrow:
        return self.header.doc_id.date_emited

    @property
    def total_amount(self) -> int:
        return self.header.totals.total_amount

    @property
    def reference_id(self) -> str:
        return f'T{str(self.doc_type)}F{self.folio}'

    @property
    def doc_type(self) -> DocumentType:
        return self.header.doc_id.doc_type

    @property
    def folio(self) -> int:
        return self.header.doc_id.folio

    def __get_xml_stamp(self, fac_handler: FacHandlerMixin) -> ET.Element:

        root = ET.Element('TED', attrib={'version': '1.0'})
        data = ET.SubElement(root, 'DD')
        rut_issuer = ET.SubElement(data, 'RE')
        doc_type = ET.SubElement(data, 'TD')
        folio = ET.SubElement(data, 'F')
        date_emited = ET.SubElement(data, 'FE')
        rut_receptor = ET.SubElement(data, 'RR')
        name_receptor = ET.SubElement(data, 'RSR')
        total_amount = ET.SubElement(data, 'MNT')
        detail_1 = ET.SubElement(data, 'IT1')
        timestamp = ET.SubElement(data, 'TSTED')

        rut_issuer.text = self.header.issuer.rut.upper()
        doc_type.text = str(self.header.doc_id.doc_type)
        folio.text = str(self.header.doc_id.folio)
        date_emited.text = str(
            self.header.doc_id.date_emited.format('YYYY-MM-DD'))
        rut_receptor.text = self.header.receptor.rut.upper()
        name_receptor.text = self.header.receptor.name
        total_amount.text = str(self.header.totals.total_amount)
        detail_1.text = self.details[0].item_name

        fac_element = fac_handler.get_fac_element(self.folio)

        data.insert(8, fac_element)
        timestamp.text = self.timestamp.format('YYYY-MM-DDTHH:mm:ss')

        data = ET.tostring(data)
        sign = fac_handler.get_sign(self.folio, data)

        sign_element = ET.SubElement(
            root, 'FRMT', attrib={'algoritmo': 'SHA1withRSA'})
        sign_element.text = str(sign, encoding='iso-8859-1')

        return root

    def set_outstanding_balance(self, amount: int) -> None:
        assert amount >= 0
        self.header.totals.outstanding_balance = amount

    def calculate_totals(self, tax_inclusive: bool = False) -> None:

        net_amount = 0
        exe_amount = 0

        for detail in self.details:
            if detail.exemption_index:
                exe_amount += detail.item_amount
            else:
                net_amount += detail.item_amount

        for glb_ds in self.global_discount_surcharges:
            if glb_ds.exemption_index:
                exe_amount = glb_ds.apply_discount_surcharge(exe_amount)

            net_amount = glb_ds.apply_discount_surcharge(net_amount)

        self.header.totals.set_net_amount(net_amount, tax_inclusive)
        self.header.totals.exent_amount = exe_amount

    def construct_xml(self, fac_handler: FacHandlerMixin) -> None:

        root = ET.Element('Documento', attrib={'ID': self.reference_id})
        root.insert(0, self.header.lxml_element())

        for index, detail in enumerate(self.details):
            root.insert(index + 1, detail.lxml_element())

        if self.global_discount_surcharges:
            for index, glb_ds in enumerate(self.global_discount_surcharges):
                root.insert(index + len(self.details) +
                            1, glb_ds.lxml_element())

        if self.references:
            for index, reference in enumerate(self.references):
                root.insert(index + len(self.details) +
                            len(self.global_discount_surcharges) + 1, reference.lxml_element())

        xml_stamp = self.__get_xml_stamp(fac_handler=fac_handler)
        root.insert(len(self.details) + len(self.global_discount_surcharges) +
                    len(self.references) + 1, xml_stamp)

        tmst_stamp_element = ET.SubElement(root, 'TmstFirma')
        tmst_stamp_element.text = xml_stamp.find('DD/TSTED').text

        self.xml_stamp = ET.tostring(xml_stamp)
        self.xml_data = ET.tostring(root)

        return

    def lxml_element(self) -> ET.Element:

        return ET.fromstring(self.xml_data)

    @classmethod
    def new_bill(cls, issuer: IssuerMixin, receptor: ReceptorMixin, details: list[DetailMixin],
                 fac_handler: FacHandlerMixin, **kwargs) -> 'DocumentMixin':
        DOC_TYPE = DocumentType.FACTURA_ELECTRÓNICA
        assert fac_handler.doc_type == DOC_TYPE
        
        doc_id = IDMixin(DOC_TYPE, fac_handler.get_folio(), **kwargs)
        header = HeaderMixin(doc_id, issuer, receptor)

        return cls(header=header, details=details or [])

    @classmethod
    def new_exent_bill(cls, issuer: IssuerMixin, receptor: ReceptorMixin, details: list[DetailMixin], 
                       fac_handler: FacHandlerMixin,**kwargs) -> 'DocumentMixin':
       
        DOC_TYPE = DocumentType.FACTURA_NO_AFECTA_O_EXENTA_ELECTRÓNICA
        assert fac_handler.doc_type == DOC_TYPE

        doc_id = IDMixin(DOC_TYPE, fac_handler.get_folio(), **kwargs)
        header = HeaderMixin(doc_id, issuer, receptor)

        return cls(header=header, details=details or [])

    @classmethod
    def new_credit_note(cls, issuer: IssuerMixin, fac_handler: FacHandlerMixin, ref_document: 'DocumentMixin',
                        code_ref: ReferenceCode, reason_ref: str = '', **kwargs) -> 'DocumentMixin':
        DOC_TYPE = DocumentType.NOTA_DE_CRÉDITO_ELECTRÓNICA
        assert fac_handler.doc_type == DOC_TYPE
        
        doc_id = IDMixin(DOC_TYPE,fac_handler.get_folio(), **kwargs)
        header = HeaderMixin(doc_id, issuer, ref_document.header.receptor)

        references = [ReferenceMixin(
            1, ref_document.doc_type, ref_document.folio, ref_document.timestamp, code_ref, reason_ref)]
        details = []

        if code_ref == ReferenceCode.CORRIGE_TEXTO:
            details = [DetailMixin(
                1, 'CORRIGE TEXTO', item_description=reason_ref)]

        elif code_ref == ReferenceCode.ANULA:
            details = ref_document.details

        return cls(header=header, details=details, references=references)


    @classmethod
    def new_debit_note(cls, issuer: IssuerMixin, fac_handler: FacHandlerMixin, ref_document: 'DocumentMixin',
                       code_ref: ReferenceCode, reason_ref: str = '', **kwargs) -> 'DocumentMixin':

        DOC_TYPE = DocumentType.NOTA_DE_DÉBITO_ELECTRÓNICA
        assert fac_handler.doc_type == DOC_TYPE
        
        doc_id = IDMixin(DOC_TYPE, fac_handler.get_folio(), **kwargs)  # type: ignore
        header = HeaderMixin(
            doc_id, issuer, ref_document.header.receptor)

        references = [ReferenceMixin(
            1, ref_document.doc_type, ref_document.folio, ref_document.timestamp, code_ref, reason_ref)]

        details = []

        if code_ref == ReferenceCode.CORRIGE_TEXTO:
            details = [DetailMixin(
                1, 'CORRIGE TEXTO', item_description=reason_ref)]

        elif code_ref == ReferenceCode.ANULA:
            details = ref_document.details

        return cls(header=header, details=details, references=references)

    @classmethod
    def new_voucher(cls, issuer: IssuerMixin, receptor: ReceptorMixin, details: list[DetailMixin], 
                    fac_handler: FacHandlerMixin, **kwargs) -> 'DocumentMixin':

        DOC_TYPE = DocumentType.BOLETA_ELECTRÓNICA
        assert fac_handler.doc_type == DOC_TYPE

        doc_id = IDMixin(DOC_TYPE, fac_handler.get_folio(), **kwargs)
        header = HeaderMixin(doc_id, issuer, receptor)

        return cls(header=header, details=details or [])

    @classmethod
    def new_exent_voucher(cls, issuer: IssuerMixin, receptor: ReceptorMixin, details: list[DetailMixin], 
                          fac_handler: FacHandlerMixin, **kwargs) -> 'DocumentMixin':

        DOC_TYPE = DocumentType.BOLETA_ELECTRÓNICA_EXENTA
        assert fac_handler.doc_type == DOC_TYPE
        
        doc_id = IDMixin(DOC_TYPE, fac_handler.get_folio(), **kwargs)
        header = HeaderMixin(doc_id, issuer, receptor)

        return cls(header=header, details=details or [])

    @classmethod
    def from_xml_element(cls, element: ET.Element, prefix: str = '') -> 'DocumentMixin':

        header = HeaderMixin.from_xml_element(
            element.find(prefix + 'Encabezado'), prefix)

        details = element.findall(prefix + 'Detalle') or []
        gbdissurs = element.findall(prefix + 'DscRcgGlobal') or []
        references = element.findall(prefix + 'Referencia') or []

        details = [DetailMixin.from_xml_element(
            detail_element, prefix) for detail_element in details]
        references = [ReferenceMixin.from_xml_element(
            reference_element, prefix) for reference_element in references]
        global_discount_surcharges = [GlobalDiscountSurchargeMixin.from_xml_element(
            gbdissur_element, prefix) for gbdissur_element in gbdissurs]

        parser = ET.XMLParser(remove_blank_text=True, ns_clean=True)
        stamp_root = ET.XML(ET.tostring(
            element.find(prefix + 'TED')), parser=parser)

        obj = cls(header=header, details=details, references=references,
                  global_discount_surcharges=global_discount_surcharges)
        obj.xml_stamp = ET.tostring(stamp_root)
        obj.xml_data = ET.tostring(element)
        
        return obj
