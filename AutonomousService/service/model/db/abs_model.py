import logging

from dateutil import parser
from mongoengine import QuerySet

from service.error import handle_mongodb_exception


class DefaultQuerySet(QuerySet):
    """Default queryset for TAL DB offering offset by ID"""

    logger = logging.getLogger(__name__)

    def create_range_date(self, query, field, **kwargs):
        """
        Creates a Greater then and lower then query given start and end as parameters,
        both parameters inclusive.
        :param query: Dictionary to add the new mongo fields
        :param field: the field name to be queried
        :param kwargs:
                start: parameter that will have __gte
                end: parameter that will have __lte
        """
        if 'start' in kwargs:
            query[field + '__gte'] = parser.parse(kwargs.get('start'))
        if 'end' in kwargs:
            query[field + '__lte'] = parser.parse(kwargs.get('end'))

    @handle_mongodb_exception
    def find(self, *args, query={}, unique=False, offset=None, limit=999):
        """
        Search for a field on a given collection.

        :param args: the fields to include on the result
        :param query: dictionary with the query to use
        :param unique: remove repeated results
        :param offset: mongo id to limit the start of the search
        :param limit: the number of results to be returned
        :return:
                List or set with the values
                mongo id as offset
        """
        # Pagination
        if offset:
            query['id__lt'] = offset

        values, count = self.__find_filter__(args, query=query, unique=unique, limit=limit)\
            if args \
            else self.__find_all__(query=query, unique=unique, limit=limit)

        # Get the offset and remove _id
        if values and 0 < count >= limit + 1:
            offset = str(values[-1].get('id'))
        else:
            offset = None

        return values, offset

    def __find_filter__(self, args, query={}, unique=False, limit=999):
        """
        Apply a filter to the results, returning only part of the document
        :param args: the fields to include on the result
        :param query: dictionary with the query to use
        :param unique: remove repeated results
        :param limit: the number of results to be returned
        :return:
                List or set with the values
                count as the number of results
        """
        args = args + ('id',)

        # Query Results
        if query:
            values = self.filter(**query).values_list(*args).order_by('-id').limit(limit)
            count = self.filter(**query).values_list(*args).count()
        else:
            values = self.filter().values_list(*args).order_by('-id').limit(limit)
            count = self.filter().values_list(*args).count()

        values = set(values) if unique else list(values)
        values = list(map(lambda value: dict(zip(args, value)), values))
        return values, count

    def __find_all__(self, query={}, unique=False, limit=999):
        """
        Search for the complete object.
        :param query: dictionary with the query to use
        :param unique: remove repeated results
        :param limit: the number of results to be returned
        :return:
                List or set with the values
                count as the number of results
        """
        if query:
            values = self.filter(**query).values_list().order_by('-id').limit(limit)
            count = self.filter(**query).values_list().count()
        else:
            values = self.filter().order_by('id').limit(limit)
            count = self.filter().count()

        values = set(values) if unique else list(values)
        values = list(map(lambda _value_: _value_.to_mongo(use_db_field=False).to_dict(), values))
        for value in values:
            value.pop('_id', None)
            value.pop('id', None)

        return values, count
