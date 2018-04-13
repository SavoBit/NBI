from service.model.db.dao.abstract import ABSDao
from service.model.db.db_parser import DBLoader


class PhysicalDAO(ABSDao):
    """
    Physical DAO abstraction to create physical machine messages.
    """
    TABLE = DBLoader().get_table(ABSDao.DATABASE_NAME.get('physical_machine'))
    CLASS = DBLoader().get_base_class(ABSDao.DATABASE_NAME.get('physical_machine'))

    EVENT_TYPE = 'compute_event'
    INNER_OBJ = 'compute_node'
    DB_MAP = dict(hostname='hostname', location='location', ip='ip', network_id='networkId')
