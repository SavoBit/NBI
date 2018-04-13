import logging

from mongoengine import connect, DEFAULT_CONNECTION_NAME

from service.error import handle_mongodb_exception

logger = logging.getLogger(__name__)


@handle_mongodb_exception
def connect_db(db_config):
    """
    Configure the database connection. This function doesn't contemplate replica sets. It is only prepared to use
    one instance of mongodb.
    :return:
    """
    logger.debug('Connecting to the database')
    if db_config:
        connect(db=db_config.pop('db_name'),
                host=db_config.pop('host'), port=db_config.pop('port'),
                **db_config)
    else:
        raise Exception('Missing db connection parameters')
