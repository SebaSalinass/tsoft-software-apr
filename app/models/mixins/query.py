from typing import Any, Optional

from arrow import Arrow
from flask import abort

from sqlalchemy.sql import Select
from sqlalchemy import delete, func, select, desc, cast, Date
from ...db import db


__all__ = ('QueryMixin',)


class QueryMixin(object):
    """Mixin class for database queries."""

    # CRUD methods
    def save(self) -> None:
        """Save instance to database."""
        db.session.add(self)
        db.session.commit()

    def delete(self) -> None:
        """Delete instance from database."""
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_between(cls, date_from: Arrow = None, date_to: Arrow = None, included: bool = True,
                     select_stmt: Optional[Select] = None) -> Optional[list[Any]]:
        """Finds object created between given dates.

        Args:
            date_from (Arrow, optional): Search for objects created after this date. If not given no `from` limit is applied. Defaults to `None`.
            date_to (Arrow, optional): Search for objects created before this date. If not given no `to` limit is applied. Defaults to `None`.
            included (bool, optional): If `False` Dates will be exclusive. Defaults to `True`.
            select_stmt (Optional[Select], optional): A select statement that will take the dates filter. Defaults to `None`.

        Returns:
            Optional[list[Any]]: List of found objects
        """
        assert (date_from or date_to)
        assert hasattr(cls, 'created_at')
        assert isinstance(select_stmt, (Select, type(None)))
            
        
        stmt = select_stmt or select(cls)
        
        if date_from:
            assert isinstance(date_from, Arrow)
            included_stmt = (cast(cls.created_at, Date) >= date_from.date())
            excluded_stmt = (cast(cls.created_at, Date) > date_from.date())
            stmt = stmt.where([excluded_stmt, included_stmt][included])
        
        if date_to:
            assert isinstance(date_from, Arrow)
            included_stmt = (cast(cls.created_at, Date) <= date_to.date())
            excluded_stmt = (cast(cls.created_at, Date) < date_to.date())
            stmt.where([excluded_stmt, included_stmt][included])
            
        result = db.session.execute(stmt)
        return result.scalars().all()

    @classmethod
    def delete_all_objects(cls) -> int:
        """Attemps to delete all table objects. The total amount of objects deleted is returned
        """ 
        stmt = delete(cls)
        result = db.session.execute(stmt)
        return result
        
    # Query helpers
    @classmethod
    def count(cls, select_stmt: Optional[Select] = None) -> int:
        """Returns the total count for this model or given select_stmt
        """
        assert isinstance(select_stmt, (Select, type(None)))
        stmt = select(func.count(select_stmt.whereclause if select_stmt is not None else None))
        if select_stmt is None:
            stmt = stmt.select_from(cls)

        result = db.session.execute(stmt)

        return result.all()[0][0]
    
    @classmethod
    def last_added(cls) -> Optional[Any]:
        """
        Return the class objects that was last added measured by created_at Arrow attribute
        
        """       
        stmt = select(cls).order_by(desc(cls.created_at))
        result = db.session.execute(stmt)
        
        return result.scalars().first()

    @classmethod
    def exists(cls, **kwargs: dict[str, Any]) -> bool:
        """Checks if record matching kwargs exists in the database.

        Returns True/False.
        """
        stmt = cls._and_query(kwargs).exists().select()
        result = db.session.execute(stmt)
        
        return result.all()[0][0]

    @classmethod
    def find(cls, **kwargs: dict[str, Any]) -> Any:
        """Return filtered AND query results for passed in kwargs.

        Example:

            # find all instances of MyModel for first name 'John' AND last name 'Doe'
            MyModel.find(first_name='John', last_name='Doe')

        Returns result list or None.
        """
        stmt = cls._and_query(kwargs)
        result = db.session.execute(stmt).scalars()
        
        return result

    @classmethod
    def find_or(cls, **kwargs: dict[str, Any]) -> Any:
        """Return filtered OR query results for passed in kwargs.

        Example:

            # find all instances of MyModel for first name 'John' OR last name 'Doe'
            MyModel.find_or(first_name='John', last_name='Doe')

        Returns result list or None.
        """
        stmt = cls._or_query(kwargs)
        result = db.session.execute(stmt).scalars()
        
        return result

    @classmethod
    def find_in(cls, _or: bool = False, **kwargs: dict[str, Any]) -> Any:
        """Return filtered query results for passed in attrs that match a list.

        Query defaults to an AND query. If you want an OR query, pass _or=True.
        """
        if _or:
            stmt = cls._or_in_query(kwargs)
        else:
            stmt = cls._and_in_query(kwargs)
        
        return db.session.execute(stmt).scalars()
    
    @classmethod
    def find_not_in(cls, _or: bool = False, **kwargs: dict[str, Any]) -> list[Any]:
        """Return filtered query results for passed in attrs that do not match
        a list.

        Query defaults to an AND query. If you want an OR query, pass _or=True.
        """
        if _or:
            stmt = cls._or_not_in_query(kwargs)
        else:
            stmt = cls._and_not_in_query(kwargs)
        
        return db.session.execute(stmt).scalars()

    @classmethod
    def find_not_null(cls, *args):
        """Return filtered query results for passed in attrs that are not None.

        Example:

            # find all instances of MyModel where email and phone != null
            MyModel.find_not_null('email', 'phone')

        NOTE: Filtering for JSON types that are not NULL does not work. JSON
        must be cast to at least text to check for a NULL value. You can verify
        this yourself in the `psql` client like so:

            # you will see null results show up
            select * from form where custom_fields is not null;

            # you will not see null results
            select * from form where custom_fields::text != 'null';

        Returns result list or None.
        """
        filters = [getattr(cls, attr) != None for attr in args]
        stmt = select(cls).filter(*filters)
        
        return db.session.execute(stmt).scalars()

    @classmethod
    def first(cls, **kwargs):
        """Return first result for query.

        Returns instance or None.
        """
        stmt = cls._and_query(kwargs)
        return db.session.execute(stmt).scalars().first()

    @classmethod
    def first_or_404(cls, **kwargs):
        """Get first item that matches kwargs or raise 404 error."""
        stmt = cls._and_query(kwargs)
        item = db.session.execute(stmt).scalars().first()
        
        if item is None:
            return abort(404)
        else:
            return item

    @classmethod
    def get(cls, pk):
        """Get item by primary key.

        Returns instance or `None`.
        """
        return db.session.get(cls, pk)
    
    @classmethod
    def get_or_404(cls, pk):
        """Get item by primary key or 404."""
        
        item = cls.get(pk)        
        if item is not None:            
            return item        
        return abort(404)


    ########################################
    # Internal methods; Do not use directly
    ########################################
    @classmethod
    def _filters(cls, filters):
        """Return filter list from kwargs."""
        return [getattr(cls, attr) == filters[attr] for attr in filters]

    @classmethod
    def _filters_in(cls, filters):
        """Return IN filter list from kwargs."""
        return [getattr(cls, attr).in_(filters[attr]) for attr in filters]

    @classmethod
    def _filters_not_in(cls, filters):
        """Return NOT IN filter list from kwargs."""
        return [getattr(cls, attr).notin_(filters[attr]) for attr in filters]

    @classmethod
    def _and_query(cls, filters):
        """Execute AND query.

        Returns BaseQuery.
        """
        return select(cls).where(db.and_(True, *cls._filters(filters)))

    @classmethod
    def _and_in_query(cls, filters):
        """Execute AND query.

        Returns BaseQuery.
        """
        return select(cls).where(db.and_(True, *cls._filters_in(filters)))

    @classmethod
    def _and_not_in_query(cls, filters):
        """Execute AND NOT IN query.

        Returns BaseQuery.
        """
        return select(cls).where(db.and_(True, *cls._filters_not_in(filters)))

    @classmethod
    def _or_query(cls, filters):
        """Execute OR query.

        Returns BaseQuery.
        """
        return select(cls).where(db.or_(*cls._filters(filters)))

    @classmethod
    def _or_in_query(cls, filters):
        """Execute OR IN query.

        Returns BaseQuery.
        """
        return select(cls).where(db.or_(*cls._filters_in(filters)))

    @classmethod
    def _or_not_in_query(cls, filters):
        """Execute OR NOT IN query.

        Returns BaseQuery.
        """
        return select(cls).where(db.or_(*cls._filters_not_in(filters)))
