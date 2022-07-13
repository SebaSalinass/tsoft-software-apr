import base64
from typing import Optional
from dataclasses import dataclass, field

from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Hash import SHA1
import lxml.etree as ET

from ...shared.mixins.base import BaseMixin
from ..constants.document import DocumentType

@dataclass
class FacMixin(BaseMixin):

    doc_type: DocumentType
    range_from: int
    range_to: int
    fac_root_string: bytes = field(repr=False)

    @property
    def fac_root(self) -> ET.Element:
        return ET.fromstring(self.fac_root_string)

    @property
    def fac_element(self) -> ET.Element:
        return self.fac_root.find('CAF')

    def validate(self) -> bool:
        signature = self.sign(b'validating')
        self.verify(signature, b'validating')
        
        return True

    def has_folio(self, folio: int) -> bool:
        return (self.range_from <= folio <= self.range_to)

    def sign(self, data: bytes) -> bytes:

        pv_key = RSA.import_key(self.fac_root.find('RSASK').text)
        digest = SHA1.new()
        digest.update(data)

        signer = pkcs1_15.new(pv_key)
        result = signer.sign(digest)

        return base64.b64encode(result)

    def verify(self, signature: bytes, data:bytes):
        signature = base64.b64decode(signature)
        
        digest = SHA1.new()
        digest.update(data)           
        
        pb_key = RSA.import_key(self.fac_root.find('RSAPUBK').text)
        verifier = pkcs1_15.new(pb_key)
        
        try:
            verifier.verify(digest, signature)
        except ValueError:
            return False
        
        return True


    @classmethod
    def from_fac_file(cls, file: str) -> 'FacMixin':
        if hasattr(file, 'read'):
            data = file.read()
        
        else:
            with open(file, 'rb') as file:
                data = file.read()
        
        return cls.from_data(data)

    @classmethod
    def from_data(cls, data: bytes) -> 'FacMixin':
        parser = ET.XMLParser(remove_blank_text=True)
        root = ET.fromstring(data, parser=parser)

        object_dict = {
            'doc_type': DocumentType(int(root.find('CAF/DA/TD').text)),
            'range_from': int(root.find('CAF/DA/RNG/D').text),
            'range_to': int(root.find('CAF/DA/RNG/H').text),
            'fac_root_string': ET.tostring(root, encoding='iso-8859-1'),
        }

        fac = cls(**object_dict)
        fac.validate()
        return fac


@dataclass
class FacHandlerMixin(BaseMixin):
    
    doc_type: DocumentType
    range_from: Optional[int] = None
    range_to:  Optional[int] = None
    last_used_folio: Optional[int] = field(default=None, repr=False)
    returned_folios: set[int] = field(default_factory=set, repr=False)
    facs: Optional[list[FacMixin]] = field(default_factory=list, repr=False)
    
    @property
    def folios_left(self) -> int:        
        return self.range_to - self.last_used_folio + len(self.returned_folios)
    
    def insert_fac(self, fac: FacMixin) -> Optional[ValueError]:
        # --------- Sanity Checks
        assert self.doc_type == fac.doc_type
        for owned_fac in self.facs:
            if owned_fac == fac:
                raise ValueError('Given Fac Object is already in the facs list.')
        # --------- Seting range from depending on new fac object
        if not self.range_from:
            self.range_from = fac.range_from
        if self.range_from > fac.range_from:
            self.range_from = fac.range_from
        # --------- Seting range from depending on new fac object        
        if not self.range_to:
            self.range_to = fac.range_to
        if self.range_to < fac.range_to:
            self.range_to = fac.range_to
        # --------- Seting range from depending on new fac object   
        if not self.last_used_folio:
            self.last_used_folio = self.range_from - 1
        # --------- Seting range from depending on new fac object   
        self.facs.append(fac)
        
        return
        
    def get_folio(self) -> int:

        if self.returned_folios:
            folio = self.returned_folios.pop()
            return folio
        
        self.last_used_folio += 1
        
        return self.last_used_folio
    
    def return_folio(self, folio: int) -> None:
        
        self.returned_folios.add(folio)
        
        return

    def get_folios_fac_object(self, folio: int) -> FacMixin:
        for fac in self.facs:
            if fac.has_folio(folio):
                return fac
        
        raise AttributeError(f'Fac Object for folio {folio} not found')

    def get_fac_element(self, folio: int) -> ET.Element:
        fac = self.get_folios_fac_object(folio)
        return fac.fac_element
        
    def get_sign(self, folio: int, data: bytes) -> bytes:

        fac = self.get_folios_fac_object(folio)
        return fac.sign(data)

    
        

