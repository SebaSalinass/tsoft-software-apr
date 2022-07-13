from typing import Union

from suds.client import Client
import lxml.etree as ET
import requests

from ..constants.document import DocSetType
from ..mixins.set import DocSetMixin, FolioUsageMixin, SIIShipmentMixin
from ..mixins.signer import SignerMixin

from .constants import ETD_SERVERS, PREFIX
from .exceptions import ETDSendingError


def get_etd_signed_seed(signer: SignerMixin, server: str) -> bytes:

    client = Client(server + '/DTEWS/CrSeed.jws?WSDL')
    client.set_options(prettyxml=False)
    response = client.service.getSeed()
    response_element = ET.fromstring(response.encode('utf-8'))
    seed = response_element.find(f'{PREFIX}RESP_BODY/SEMILLA').text

    return signer.sign_seed_lxml_element(seed)


def get_etd_token(signer: SignerMixin, development: bool = True) -> str:

    server = ETD_SERVERS[development]
    signed_seed = get_etd_signed_seed(signer, server)

    url = server + '/DTEWS/GetTokenFromSeed.jws?WSDL'
    client = Client(url)
    client.set_options(prettyxml=False)
    response = client.service.getToken(signed_seed)
    response_element = ET.fromstring(response.encode('utf-8'))

    return response_element.find(f'{PREFIX}RESP_BODY/TOKEN').text


def send_etd_set(doc_set: Union[DocSetMixin, FolioUsageMixin], token: str,  
                 development: bool = True) -> Union[SIIShipmentMixin, ETDSendingError]:
    '''Returns the response dict including track id '''
    assert doc_set.type == DocSetType.ETD


    rut_company, dv_company = doc_set.cover_data.rut_issuer.split('-')
    rut_sender, dv_sender = doc_set.cover_data.rut_sender.split('-')
    
    server = ETD_SERVERS[development]
    url = server + ':443/cgi_dte/UPL/DTEUpload'
    cookies = dict(TOKEN=token)
    data = dict(rutSender=rut_sender, dvSender=dv_sender, rutCompany=rut_company, dvCompany=dv_company)
    files = {'file': doc_set.xml_data}
    headers = {'User-Agent': 'Mozilla/4.0 (compatible; PROG 1.0; Windows NT 5.0; YComp 5.0.2.4)^M'}
    
    s = requests.Session()
    response = s.post(url=url, data=data, cookies=cookies, files=files, headers=headers)
    response_element = ET.fromstring(response.content)

    if response_element.find('TRACKID') is not None:
        
        return {
            'rut_emisor': response_element.find('RUTCOMPANY').text,
            'rut_envia': response_element.find('RUTSENDER').text,
            'trackid': response_element.find('TRACKID').text,
            'fecha_recepcion': response_element.find('TIMESTAMP').text,
            'estado': response_element.find('STATUS').text,
            'file': response_element.find('FILE').text,
        }

    raise ETDSendingError('An error occured during ETD sending')


def get_etd_upload_state(shipment: SIIShipmentMixin, token: str, development: bool = True) -> bytes:
    
    server = ETD_SERVERS[development]
    
    rut_sender, dv_sender = shipment.doc_set.cover_data.rut_sender.split('-')
    track_id = shipment.trackid
    
    client = Client(server + '/DTEWS/QueryEstUp.jws?WSDL')
    response = bytes(client.service.getEstUp(rut_sender, dv_sender, track_id, token), encoding='utf-8')
    response_element = ET.fromstring(response)
    return response
