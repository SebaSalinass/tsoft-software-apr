from typing import Union, Any
import json

import lxml.etree as ET
import requests

from ..constants.document import DocSetType
from ..mixins.set import DocSetMixin, SIIShipmentMixin
from ..mixins.signer import SignerMixin

from .exceptions import ETDSendingError
from .constants import VOUCHER_TOKEN_SERVERS, VOUCHER_SENDING_SERVERS


def get_voucher_signed_seed(signer: SignerMixin, server: str) -> bytes:

    s = requests.Session()
    url = server + '/recursos/v1/boleta.electronica.semilla'
    headers = {'Accept': 'application/xml'}

    response = s.get(url=url, headers=headers)
    element = ET.fromstring(response.content)

    semilla = element.xpath('//SEMILLA')[0].text

    return signer.sign_seed_lxml_element(semilla)


def get_voucher_token(signer: SignerMixin, development: bool = True) -> Union[bytes, str]:

    server = VOUCHER_TOKEN_SERVERS[development]
    signed_seed = get_voucher_signed_seed(signer, server)

    s = requests.Session()
    url = server + '/recursos/v1/boleta.electronica.token'
    headers = {'Accept': 'application/xml',
               'Content-Type': 'application/xml'}

    response = s.post(url=url, headers=headers, data=signed_seed)
    element = ET.fromstring(response.content)

    if element.xpath('//ESTADO')[0].text == '00':
        return element.xpath('//TOKEN')[0].text
    else:
        return response.content
    
    
def send_voucher_set(doc_set: DocSetMixin, token: str, 
                     development: bool = True) -> Union[SIIShipmentMixin, ETDSendingError]:
    assert doc_set.type == DocSetType.VOUCHER

    rut_sender, dv_sender = doc_set.cover_data.rut_sender.split('-')
    rut_company, dv_company = doc_set.cover_data.rut_issuer.split('-')

    server = VOUCHER_SENDING_SERVERS[development]
    url = server + '/recursos/v1/boleta.electronica.envio'
    cookies = dict(TOKEN=token)
    data = dict(rutSender=rut_sender, dvSender=dv_sender, rutCompany=rut_company, dvCompany=dv_company)
    files = {'file': doc_set.xml_data}
    headers = {'User-Agent': 'Mozilla/4.0 (compatible; PROG 1.0; Windows NT 5.0; YComp 5.0.2.4)^M'}

    s = requests.Session()
    response = s.post(url=url, data=data, cookies=cookies, files=files, headers=headers)

    try:
        return json.loads(response.content)

    except Exception as e:
        raise ETDSendingError('An error occured during VOUCHER sending')
    
    
def get_voucher_upload_state(shipment: SIIShipmentMixin, token: str, development: bool = True) -> dict[str, Any]:

    server = VOUCHER_TOKEN_SERVERS[development]
    
    rut_sender, dv_sender = shipment.doc_set.cover_data.rut_sender.split('-')
    track_id = shipment.trackid

    url = server + f'/recursos/v1/boleta.electronica.envio/{rut_sender}-{dv_sender}-{track_id}'
    headers = {'Accept': 'application/json',
               'Content-Type': 'application/json',
               'User-Agent': 'Mozilla/4.0 (compatible; PROG 1.0; Windows NT 5.0; YComp 5.0.2.4)^M'}
    cookies = dict(TOKEN=token)
    
    s = requests.Session()
    response = s.get(url=url, headers=headers, cookies=cookies)

    return json.loads(response.content)
