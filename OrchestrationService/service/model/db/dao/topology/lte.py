from service.model.db.dao.abstract import ABSDao
from service.model.db.db_parser import DBLoader


class UEDAO(ABSDao):
    """
    UE DAO abstraction to create LTE messages.
    """
    TABLE = TABLE = DBLoader().get_table(ABSDao.DATABASE_NAME.get('ue'))
    CLASS = DBLoader().get_base_class(ABSDao.DATABASE_NAME.get('ue'))

    EVENT_TYPE = 'ue_event'
    INNER_OBJ = 'ue'
    DB_MAP = dict(imsi='IMSI', mcc='MCC', mnc='MNC', ueid='UEId', mme_teid_s11='mmeTeidS11', sgw_teid_s11='sgwTeidS11',
                  eps_bearer_id='epsBearerId', mme_ip='MMEIp', sgw_teid_s1='sgwTeidS1', enb_teid_s1u='enbTeidS1u',
                  sgw_ip_s1u='sgwIPS1U', enb_ip_s1u='enbIPS1U', ue_ip='UEIP')

    @classmethod
    def __create_message__(cls, row):
        """
        Override create message method, since no state is saved on the DB, it must be looked under each attribute set.
        :param row: The DB row to transform in real time message.
        :return: Real time message in dict format
        """
        message = super(UEDAO, cls).__create_message__(row)  # Uses the super method to create message bases
        message['type'] = 'UPDATE' if 'ue_ip' in list(message.get(UEDAO.INNER_OBJ).keys()) else 'CREATE'
        return message
