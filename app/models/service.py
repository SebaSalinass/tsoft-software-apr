from sqlalchemy_utils import UUIDType
from sqlalchemy.ext.mutable import MutableDict

from ..domain.service.mixins.service import ServiceMixin, ServiceTypeMixin
from ..db import db
from .shared.base import Model
from .shared.activable import Activable


__all__ = ('Service', 'ServiceType',)


class ServiceType(Model, ServiceTypeMixin):

    __tablename__ = 'service_types'

    code = db.Column(db.String(4), nullable=False, index=True, unique=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300))
    water_service = db.Column(db.Boolean, default=False)

    # ---------- SQLAlchemy relationships
    services = db.relationship('Service', backref='service_type', uselist=True)
        
    @staticmethod
    def insert_service_types() -> None:

        service_types_list = [
            {
                'code': 'S001',  # DONT YOU NEVER CHANGE IT
                'name': 'Agua potable domiciliaria',
                'description': 'Servicio de agua potable rural domiciliaria',
                'water_service': True
            },
            {
                'code': 'S002',  # DONT YOU NEVER CHANGE IT
                'name': 'Incorporacion',
                'description': 'Servicio de incorporacion de usuario a libro de socios.',

            },
            {
                'code': 'S003',  # DONT YOU NEVER CHANGE IT
                'name': 'Arranque',
                'description': 'Servicio de arranque y conexion a red (Instalacion de Medidor).',
            },
            {
                'code': 'S004',  # DONT YOU NEVER CHANGE IT
                'name': 'Reposicion de servicio',
                'description': 'Servicio de reposicion despues de corte de agua potable.',
            },
            {
                'code': 'S005',  # DONT YOU NEVER CHANGE IT
                'name': 'Reemplazo de medidor',
                'description': 'Servicio de reemplazo de medidor por uso mal uso.',
            },
            {
                'code': 'S006',  # DONT YOU NEVER CHANGE IT
                'name': 'Deuda Anterior',
                'description': 'Servicio ficticio que combina deudas por \
                                diferentes conceptos previa instalacion de servicio.',
            },
        ]

        for obj_dict in service_types_list:
            service_type = ServiceType.exists(name=obj_dict['name'])
            if not service_type:
                service_type = ServiceType(**obj_dict)
                service_type.is_water_service = obj_dict['is_water_service']
                db.session.add(service_type)
        return


class Service(Model, Activable, ServiceMixin):

    __tablename__ = 'services'

    service_type_id = db.Column(UUIDType, db.ForeignKey('service_types.id'))
    payload = db.Column(MutableDict.as_mutable(db.JSON), nullable=False)


    @classmethod
    def new(cls, payload: dict[str, str], service_type: ServiceType) -> 'Service':
        """_summary_

        Args:
            payload (dict[str, str]): Data describing the charging method and prices
            service_type (ServiceType): The ServiceType of this Service.

        Returns:
            Service: The new Service
        """
        return cls(payload=payload, service_type=service_type)