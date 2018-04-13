import logging

from service.error import handle_topology_exception
from service.conf_reader import ConfReader


class ABSDao(object):
    """
    Abstract object to access DB models. This class only handles tables and do not map DB models.
    It implements methods that can be used to create messages coming from the database.
    """

    logger = logging.getLogger(__name__)
    DATABASE_NAME = ConfReader().get_section_dict('TOPOLOGY_DATABASE')  # The DB name equals across all tables.

    @staticmethod
    def __clean_dict__(obj):
        """
        Remove keys from dict where the value is None
        :param obj: Dict to clean
        :return: Dict without None values
        """
        return {k: v for k, v in obj.items() if v is not None}

    @classmethod
    def __create_message__(cls, row):
        """
        Creates a message like the real time, with the same structure.
        It also creates the message's inner object.
        :param row: The DB row to transform in real time message.
        :return: Real time message in dict format
        """
        message = dict()
        message['eventtype'] = cls.EVENT_TYPE
        message['type'] = row.pop('state', None)
        inner_obj = dict()
        for key, value in cls.DB_MAP.items():
            inner_obj[key] = row.pop(value)

        message[cls.INNER_OBJ] = cls.__clean_dict__(inner_obj)
        message = cls.__clean_dict__(message)
        return message

    def __init__(self, session):
        """
        Creates an instance of ABSDao
        :param session: The DB connection to use in the queries.
        """
        self.session = session
        self.messages = list()
        self.rows = list()

    def snapshot(self):
        """
        Current topology by the time of the request.
        :return: dict with queried type messages
        """
        # Query the database
        rows = self.query_all()
        self.rows = list()
        for row in rows:
            self.rows.append(dict(zip(type(self).TABLE.columns.keys(), row)))
        # Create the messages
        return [type(self).__create_message__(row) for row in self.rows]

    @handle_topology_exception
    def query_all(self):
        """
        Query all rows from a table.
        :return: Query result as dict object
        """
        return self.session.query(type(self).TABLE).all()

    @handle_topology_exception
    def query_by_filer(self, column_name, value):
        """
        Query a table by a specific filter. This method only filters by a single value in a single column.
        :param column_name: The name of the column to search for
        :param value: The value to search for
        :return: All query result as dict object
        """
        column = getattr(type(self).TABLE.c, column_name)
        return self.session.query(type(self).TABLE).filter(column == value).all()
