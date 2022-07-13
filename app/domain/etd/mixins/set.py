from dataclasses import dataclass, field
from io import BytesIO
from arrow import Arrow
from typing import Any, Literal, Optional, List, Union


from ...shared.mixins.base import BaseMixin
from .signable import SignableMixin
from .signer import SignerMixin
from .etd import ETDMixin
from ..constants.document import DocumentType, DocSetType, SIIShipmentType

import lxml.etree as ET

@dataclass
class CoverDataMixin(BaseMixin):
    
    rut_issuer: str
    rut_sender: str
    resol_date: Arrow
    resol_number: int
    is_active: bool = True


@dataclass
class DocSetMixin(BaseMixin, SignableMixin):
    
    type: DocSetType
    rut_receptor: str
    date_emited: Arrow
    cover_data: CoverDataMixin = field(repr=False)
    
    xml_data: Optional[bytes] = field(default=None, repr=False)
    etds: List[ETDMixin] = field(default_factory=list, repr=False)

    @property
    def reference_uri(self) -> str:
        return f'SetDTE-{hash(self)}-{self.date_emited.format("DD-MM-YYYY")}'

    def __get_subtotals_elements(self) -> list[ET.Element]:

        doc_types_amount: dict[DocumentType, int] = {}
        elem_list = []

        for etd in self.etds:
            if etd.document.doc_type not in doc_types_amount.keys():
                doc_types_amount[etd.document.doc_type] = 1
            else:
                doc_types_amount[etd.document.doc_type] += 1

        for doc_type, amount in doc_types_amount.items():
            root = ET.Element('SubTotDTE')
            subtotal_type = ET.SubElement(root, 'TpoDTE')
            subtotal_number = ET.SubElement(root, 'NroDTE')

            subtotal_type.text = str(doc_type)
            subtotal_number.text = str(amount)
            elem_list.append(root)

        return elem_list

    def __get_cover_element(self) -> ET.Element:

        root = ET.Element('Caratula', attrib={'version': '1.0'})

        rut_issuer = ET.SubElement(root, 'RutEmisor')
        rut_sender = ET.SubElement(root, 'RutEnvia')
        rut_receptor = ET.SubElement(root, 'RutReceptor')
        resol_date = ET.SubElement(root, 'FchResol')
        resol_number = ET.SubElement(root, 'NroResol')
        timestamp = ET.SubElement(root, 'TmstFirmaEnv')

        rut_issuer.text = self.cover_data.rut_issuer
        rut_sender.text = self.cover_data.rut_sender
        rut_receptor.text = self.rut_receptor
        resol_date.text = self.cover_data.resol_date.format('YYYY-MM-DD')
        resol_number.text = str(self.cover_data.resol_number)
        timestamp.text = self.date_emited.format('YYYY-MM-DDTHH:mm:ss')

        for index, subtotal_element in enumerate(self.__get_subtotals_elements()):
            root.insert(6 + index, subtotal_element)

        return root

    def __get_set_element(self) -> ET.Element:

        root = ET.Element('SetDTE', attrib={'ID': self.reference_uri})
        root.insert(0, self.__get_cover_element())

        for index, etd in enumerate(self.etds):
            root.insert(1 + index, etd.lxml_element())

        return root

    def construct_xml(self, signer: SignerMixin) -> None:

        attr_qname = ET.QName(
            "http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")

        nsmap = {
            None: 'http://www.sii.cl/SiiDte',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        }

        if self.type == DocSetType.ETD:
            element_name = 'EnvioDTE'
            xsd_name = 'EnvioDTE_v10'
            attr_qname_dict = {
                attr_qname: f'http://www.sii.cl/SiiDte {xsd_name}.xsd', 'version': '1.0'}

        else:
            element_name = 'EnvioBOLETA'
            xsd_name = 'EnvioBOLETA_v11'

        attr_qname_dict = {
            attr_qname: f'http://www.sii.cl/SiiDte {xsd_name}.xsd', 'version': '1.0'}

        root = ET.Element(element_name, attr_qname_dict, nsmap=nsmap)
        set_element = self.__get_set_element()
        root.insert(0, set_element)
        root.insert(1, self.get_signature_node(self.reference_uri))

        id_node = '{'+'http://www.sii.cl/SiiDte'+'}' + 'SetDTE'

        signed = signer.sign_element(root, id_node)
        self.xml_data = ET.tostring(ET.fromstring(
            signed), doctype='<?xml version="1.0" encoding="ISO-8859-1"?>')

        return ET.fromstring(signed)

    def lxml_element(self) -> ET.Element:
        return ET.fromstring(self.xml_data)

    def to_xml_file(self, file_path: str, signer: SignerMixin = None) -> None:

        with open(file_path, 'wb') as xml_file:
            xml_file.write(ET.tostring(self.to_xml_element(
                signer), doctype='<?xml version="1.0" encoding="ISO-8859-1"?>'))

    @classmethod
    def from_xml_element(cls, element: ET.Element, prefix: str = '') -> 'DocSetMixin':

        set_etd = cls()
        set_etd.documents = [ETDMixin.from_xml_element(
            etd_element, prefix) for etd_element in element.findall(prefix+'DTE')]

        return set_etd

    @classmethod
    def from_data(cls, data: Union[BytesIO, bytes], prefix: str = '') -> 'DocSetMixin':

        if hasattr(data, 'read'):
            data = data.read()

        element = ET.fromstring(data)
        set_element = element.find(prefix+'SetDTE')

        return cls.from_xml_element(set_element, prefix=prefix)


@dataclass
class FolioUsageMixin(BaseMixin, SignableMixin):

    timestamp: Arrow
    date_initial: Arrow
    date_final: Arrow
    cover_data: CoverDataMixin = field(repr=False)
    doc_type: Literal[DocumentType.BOLETA_ELECTRÓNICA,
                      DocumentType.BOLETA_ELECTRÓNICA_EXENTA]
    correlative: int = field(repr=False, default=1)
    sequence: int = field(repr=False, default=1)

    doc_set: Optional[DocSetMixin] = field(repr=False, default=None)
    xml_data: Optional[bytes] = field(repr=False, default=None)

    @property
    def reference_uri(self) -> str:
        return f'FOLIOS-{self.timestamp.format("DD-MM-YYYY")}'

    def __get_cover_xml(self) -> ET.Element:

        root = ET.Element('Caratula', attrib={'version': '1.0'})

        rut_issuer = ET.SubElement(root, 'RutEmisor')
        rut_sender = ET.SubElement(root, 'RutEnvia')
        resol_date = ET.SubElement(root, 'FchResol')
        resol_number = ET.SubElement(root, 'NroResol')
        date_initial = ET.SubElement(root, 'FchInicio')
        date_final = ET.SubElement(root, 'FchFinal')
        correlative = ET.SubElement(root, 'Correlativo')
        sequence = ET.SubElement(root, 'SecEnvio')
        timestamp = ET.SubElement(root, 'TmstFirmaEnv')

        rut_issuer.text = self.cover_data.rut_issuer
        rut_sender.text = self.cover_data.rut_sender
        resol_date.text = self.cover_data.resol_date.format('YYYY-MM-DD')
        resol_number.text = str(self.cover_data.resol_number)
        date_initial.text = self.date_initial.format('YYYY-MM-DD')
        date_final.text = self.date_final.format('YYYY-MM-DD')
        correlative.text = str(self.correlative)
        sequence.text = str(self.sequence)
        timestamp.text = self.timestamp.format('YYYY-MM-DDTHH:mm:ss')

        return root

    def __get_summary(self) -> ET.Element:

        info = self.__get_info()

        root = ET.Element('DocumentoConsumoFolios', attrib={
                          'ID': self.reference_uri})
        root.insert(0, self.__get_cover_xml())

        summary = ET.SubElement(root, 'Resumen')

        doc_type = ET.SubElement(summary, 'TipoDocumento')
        doc_type.text = str(self.doc_type)

        if info['net_amount']:
            net_amount = ET.SubElement(summary, 'MntNeto')
            net_amount.text = str(info['net_amount'])

        if info['tax_amount']:
            tax_amount = ET.SubElement(summary, 'MntIva')
            tax_amount.text = str(info['tax_amount'])

        if info['net_amount']:
            tax_pct = ET.SubElement(summary, 'TasaIVA')
            tax_pct.text = str(info['tax_pct'])

        if info['exe_amount']:
            exe_amount = ET.SubElement(summary, 'MntExento')
            exe_amount.text = str(info['exe_amount'])

        total_amount = ET.SubElement(summary, 'MntTotal')
        total_amount.text = str(info['total_amount'])

        emited_folios = ET.SubElement(summary, 'FoliosEmitidos')
        emited_folios.text = str(info['doc_count'])
        nulled_folios = ET.SubElement(summary, 'FoliosAnulados')
        nulled_folios.text = str(0)
        used_folios = ET.SubElement(summary, 'FoliosUtilizados')
        used_folios.text = str(info['doc_count'])

        if info['ranges']:
            for usage_range in info['ranges']:
                used_range = ET.SubElement(summary, 'RangoUtilizados')
                initial = ET.SubElement(used_range, 'Inicial')
                initial.text = str(usage_range[0])
                final = ET.SubElement(used_range, 'Final')
                final.text = str(usage_range[1])

        return root

    def __get_info(self) -> dict[str, Any]:

        info_dict = {
            'ranges': [],
            'doc_count': 0,
            'net_amount': 0,
            'tax_amount': 0,
            'exe_amount': 0,
            'total_amount': 0,
            'tax_pct': 19.0,
        }

        def sort_docs(etd: ETDMixin) -> int:
            return etd.document.folio

        if self.doc_set:

            sorted_documents = sorted(self.doc_set.etds, key=sort_docs)

            for document in sorted_documents:
                info_dict['doc_count'] += 1  # type: ignore
                totals = document.document.header.totals
                info_dict['net_amount'] += totals.net_amount  # type: ignore
                info_dict['tax_amount'] += totals.tax_amount  # type: ignore
                info_dict['exe_amount'] += totals.exent_amount  # type: ignore
                # type: ignore
                info_dict['total_amount'] += totals.total_amount

                folio = document.document.folio

                if not info_dict['ranges']:
                    info_dict['ranges'].append([folio, folio])  # type: ignore

                elif folio == info_dict['ranges'][-1][1] + 1:  # type: ignore
                    info_dict['ranges'][-1][1] += 1  # type: ignore

                elif folio > info_dict['ranges'][-1][1] + 1:  # type: ignore
                    info_dict['ranges'].append([folio, folio])  # type: ignore

        return info_dict

    def construct_xml(self, signer: SignerMixin) -> None:

        attr_qname = ET.QName(
            "http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")
        nsmap = {
            None: 'http://www.sii.cl/SiiDte',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }

        element_name = 'ConsumoFolios'
        xsd_name = 'ConsumoFolio_v10'

        root = ET.Element(element_name, {
                          attr_qname: f'http://www.sii.cl/SiiDte {xsd_name}.xsd', 'version': '1.0'}, nsmap=nsmap)
        summary_element = self.__get_summary()
        root.insert(0, summary_element)
        root.insert(1, self.get_signature_node(self.reference_uri))

        id_node = '{'+'http://www.sii.cl/SiiDte'+'}' + 'DocumentoConsumoFolios'

        et_signed = ET.fromstring(signer.sign_element(root, id_node))
        self.xml_data = ET.tostring(
            et_signed, doctype='<?xml version="1.0" encoding="ISO-8859-1"?>')

        return

    def lxml_element(self) -> ET.Element:
        return ET.fromstring(self.xml_data)

    def to_xml_file(self, file_path: str, signer: SignerMixin = None) -> None:

        with open(file_path, 'wb') as xml_file:
            xml_file.write(ET.tostring(self.to_xml_element(
                signer), doctype='<?xml version="1.0" encoding="ISO-8859-1"?>'))


class SIIShipmentMixin:

    payload: dict[str: Any]
    type: SIIShipmentType
    status: str
    trackid: str
    doc_set: DocSetMixin
