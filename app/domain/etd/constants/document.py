from enum import IntEnum, Enum


class DocumentType(IntEnum):

    FACTURA = 30
    FACTURA_EXENTA = 32
    BOLETA = 35
    BOLETA_EXENTA = 38
    FACTURA_COMPRA = 45
    NOTA_DEBITO = 55
    NOTA_CREDITO = 60
    LIQUIDACION = 103
    LIQUIDACION_FACTURA = 40

    FACTURA_ELECTRÓNICA = 33
    FACTURA_NO_AFECTA_O_EXENTA_ELECTRÓNICA = 34
    BOLETA_ELECTRÓNICA = 39
    BOLETA_ELECTRÓNICA_EXENTA = 41
    LIQUIDACION_FACTURA_ELECTRONICA = 43
    FACTURA_COMPRA_ELECTRONICA = 46
    GUIDA_DESPACHO_ELECTRONICA = 52
    NOTA_DE_DÉBITO_ELECTRÓNICA = 56
    NOTA_DE_CRÉDITO_ELECTRÓNICA = 61
    
    def __str__(self) -> str:
        return str(self.value)


class ServiceIndex(IntEnum):
    SERVICIOS_PERIODICOS_DOMICILIARIOS = 1
    OTROS_SERVICIOS_PERIODICOS = 2
    FACTURA_SERVICIOS = 3
    SERVICIOS_HOTELERIA = 4
    SERVICIOS_TRANSPORTE_TERRESTRE_INTERNACIONAL = 5
    SERVICIOS_PRESTADOS_Y_UTILIZADOS_TOTALMENTE_EN_EXTRANJERO = 6
    
    def __str__(self) -> str:
        return str(self.value)


class UnrecoverableTaxCode(IntEnum):
    COMPRAS_DESTINADAS_A_IVA_EXENTAS = 1
    FACTURAS_DE_PROVEEDORES_FUERA_DE_PLAZO = 2
    GASTOS_RECHAZADOS = 3
    ENTREGAS_GRATUITAS = 4
    OTROS = 9
    
    def __str__(self) -> str:
        return str(self.value)


class ExemptionIndex(IntEnum):

    NO_AFECTO = 1
    NO_FACTURABLE = 2
    GARANTIA_DEPOSITO_POR_ENVASE = 3
    ITEM_NO_VENTA = 4
    ITEM_A_REBAJAR = 5
    NO_FACTURABLE_NEGATIVO = 6

    def __str__(self) -> str:
        return str(self.value)


class MeasurementType(Enum):
    TONELADA = 'TON'
    KILOGRAMO = 'KG'
    UNIDADES = 'UNID'
    QUINTAL = 'QTAL'
    METRO_CUBICO = 'M3'
    METRO_RUMA = 'MR'
    HORAS = 'Hora'

    def __str__(self) -> str:
        return self.value


class ReferenceCode(IntEnum):
    ANULA = 1
    CORRIGE_TEXTO = 2
    CORRIGE_MONTO = 3
    
    def __str__(self) -> str:
        return str(self.value)


class MovementType(Enum):
    DESCUENTO = 'D'
    RECARGO = 'R'

    def __str__(self) -> str:
        return self.value
    

class ValueType(Enum):
    PORCENTAJE = '%'
    MONTO = '$'

    def __str__(self) -> str:
        return self.value
    
    
class DocSetType:
    ETD = 1
    VOUCHER = 2


class SIIShipmentType(IntEnum):
    VOUCHER = 1
    ETD = 2