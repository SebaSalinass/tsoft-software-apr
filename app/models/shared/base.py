from dataclasses import dataclass, field
from math import ceil
from uuid import uuid4
from typing import Optional, Iterator

from flask import request, abort, url_for
from arrow import utcnow
from sqlalchemy import select
from sqlalchemy.sql import Select
from sqlalchemy_utils import UUIDType, ArrowType
from sqlalchemy.ext.declarative import declared_attr

from ...db import db
from ..mixins.query import QueryMixin


@dataclass
class Pagination:
    
    model: 'Model'
    page: int
    per_page: int
    total: int
    items: list['Model']
    select_stmt: Optional[Select] = None
    endpoint: Optional[str] = None
    extra_params: Optional[dict] = field(default_factory=dict)
    at: Optional[str] = ''
    page_arg: str = 'page'
    per_page_arg: str = 'per_page'
    max_per_page: Optional[int] = None
   
    @property
    def showing_from(self):
        return (self.page - 1) * self.per_page + 1
    
    @property
    def showing_to(self):
        return  self.showing_from + len(self.items) - 1

    @property
    def pages(self) -> int:
        """The total number of pages"""
        if self.per_page == 0:
            pages = 0
        else:
            pages = ceil(self.total / self.per_page)        
        return pages

    def prev(self, error_out: bool = False) -> Optional['Pagination']:
        """Returns a :class:`Pagination` object for the previous page."""
        if not self.has_prev:
            return
        return self.model.paginate(self.select_stmt, self.page - 1, self.per_page,
                                   self.page_arg, self.per_page_arg,
                                   error_out, self.max_per_page)
    
    @property
    def prev_num(self) -> Optional[int]:
        """Number of the previous page."""
        if not self.has_prev:
            return None
        return self.page - 1

    @property
    def has_prev(self) -> bool:
        """True if a previous page exists"""
        return self.page > 1

    def next(self, error_out: bool = False) -> Optional['Pagination']:
        if not self.has_next:
            return
        """Returns a :class:`Pagination` object for the next page."""
        return self.model.paginate(self.select_stmt, self.page + 1, self.per_page,
                                   self.page_arg, self.per_page_arg,
                                   error_out, self.max_per_page)

    @property
    def has_next(self) -> bool:
        """True if a next page exists."""
        return self.page < self.pages

    @property
    def next_num(self) -> Optional[int]:
        """Number of the next page"""
        if not self.has_next:
            return None
        return self.page + 1

    def url_for_page(self, page: int) -> str:
        
        if request:
            if not self.endpoint:
                self.endpoint = request.endpoint
                self.extra_params = request.args.copy()
                self.extra_params.pop(self.page_arg, None)

        params = {self.page_arg: page}
        url = url_for(self.endpoint, **params, **self.extra_params)
        return url + f'#{self.at}' if self.at else url

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2) -> Iterator[Optional[int]]:
        """Iterates over the page numbers in the pagination.  The four
        parameters control the thresholds how many numbers should be produced
        from the sides.  Skipped page numbers are represented as `None`.
        This is how you could render such a pagination in the templates:

        .. sourcecode:: html+jinja

            {% macro render_pagination(pagination, endpoint) %}
              <div class=pagination>
              {%- for page in pagination.iter_pages() %}
                {% if page %}
                  {% if page != pagination.page %}
                    <a href="{{ url_for(endpoint, page=page) }}">{{ page }}</a>
                  {% else %}
                    <strong>{{ page }}</strong>
                  {% endif %}
                {% else %}
                  <span class=ellipsis>…</span>
                {% endif %}
              {%- endfor %}
              </div>
            {% endmacro %}
        """
        last = 0
        for num in range(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num


class Model(db.Model, QueryMixin):
    """
    Abstract base class for all app models.
    Provides a `id`, `created_at` column to every model.

    To define models, follow this example:

        from .base import Model

        class MyModel(Model):
            # model definition
    """
    __abstract__ = True

    id = db.Column(UUIDType, primary_key=True, default=uuid4)

    @declared_attr
    def created_at(cls):
        return db.Column(ArrowType, default=utcnow, index=True)

    @declared_attr
    def updated_at(cls):
        return db.Column(ArrowType, default=None, index=True, onupdate=utcnow)

    @property
    def class_name(self) -> str:
        """
        Shortcut for returning class name.
        """
        return self.__class__.__name__

    @classmethod
    def __ignore__(cls) -> bool:
        """Custom class attr that lets us control which models get ignored.

        We are using this because knowing whether or not we're actually dealing
        with an abstract base class is only possible late in the class's init
        lifecycle.

        This is used by the dynamic model loader to know if it should ignore.
        """
        return cls.__name__ in ('Model', 'Activable')  # can add more abstract base classes here

    def __repr__(self) -> str:
        """"Returns a string representation of every object.

        Useful for logging & error reporting.
        Example:

            >>> obj = MyModel()
            >>> print obj
            <MyModel-ec7639c9-d2d2-429e-91fe-5a3975d66787>

        Can be overridden by subclasses to customize string representation.
        """
        return f"<{self.class_name}-{self.id}>"
    
    @classmethod
    def paginate(cls, select_stmt: Optional[Select] = None, page: Optional[int] = None, 
                 per_page: Optional[int] = None, page_arg: str = 'page', 
                 per_page_arg: str = 'per_page', error_out: bool = True, 
                 max_per_page=None) -> Pagination:
    
        if request:
            page = page or request.args.get(page_arg, 1, int)
            per_page = per_page or request.args.get(per_page_arg, 20, int)
                                
        else:
            if page is None:
                page = 1
            if per_page is None:
                per_page = 20

        if max_per_page is not None:
            per_page = min(per_page, max_per_page)

        if page < 1:
            if error_out:
                abort(404)
            else:
                page = 1

        if per_page < 0:
            if error_out:
                abort(404)
            else:
                per_page = 20
                
        
        total = cls.count(select_stmt)
        select_stmt = select_stmt if isinstance(select_stmt, Select) else select(cls)
        
        
        start = (page - 1) * per_page
        items = db.session.execute(select_stmt.slice(start, start + per_page)).scalars().all()

        if not items and page != 1 and error_out:
            abort(404)
    

        return Pagination(cls, page, per_page, total, items, select_stmt=select_stmt, page_arg=page_arg, per_page_arg=per_page_arg)
