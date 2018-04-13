import logging

from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker, scoped_session, Session

from service.conf_reader import ConfReader
from service.utils import Singleton
from service.error import handle_topology_exception


class DBLoader(metaclass=Singleton):
    """
    Class responsible to load the DB and map it's tables.
    This classes uses SQLAlchemy automap features to map all DB tables.
    It can provide all the tables and creates the sessions to read from them.
    """

    logger = logging.getLogger(__name__)

    def __init__(self):
        self.__load_db__()

    @handle_topology_exception
    def __load_db__(self):
        """
        Function to set the DB connection and tables.
        This uses the sqlalchemy automap to populate the needed tables.
        It is intended to keep maximum abstraction from DB to lower schema changes impact.
        NOTE: This not create models it only refers tables
        :raise EnvironmentError: Whenever the ini file doesn't contain the url on the Database section
        """
        connection = ConfReader().get('TOPOLOGY_DATABASE', 'url')

        if not connection:
            raise EnvironmentError('Missing Database URL connection')
        self.engine = create_engine(connection, pool_recycle=1800, connect_args={'connect_timeout': 15})

        # Create model based on DB
        # http://docs.sqlalchemy.org/en/latest/orm/extensions/automap.html
        self.base = automap_base()
        self.base.prepare(self.engine, reflect=True)

        # Load tables
        # Keep maximum abstraction to lower the impact of schema changes
        self.tables = self.base.metadata.tables

    def get_mapped_tables(self):
        """
        :return: List with all columns of a table.
        """
        return list(self.tables.keys())

    def get_table(self, name):
        """
        Get an SQLAlchemy table object
        :param name: The name of the table to search for
        :return: SQLAlchemy table object
        :raise ValueError: When the provided name has no correspondence on the DB
        """
        table = self.tables.get(name, None)
        if table is not None:
            return table
        raise ValueError('No table with name {} was found'.format(name))

    def get_base_class(self, name):
        try:
            return getattr(self.base.classes, name)
        except Exception as e:
            return None

    def create_session(self):
        """
        Crates a new DB session
        :return: Scoped session object
        """
        session_factory = sessionmaker(bind=self.engine)
        return scoped_session(session_factory)
