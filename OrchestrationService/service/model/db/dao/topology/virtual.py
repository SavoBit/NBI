from service.model.db.dao.abstract import ABSDao
from service.model.db.db_parser import DBLoader


class VirtualMachineDAO(ABSDao):
    """
    Virtual DAO abstraction to create physical machine messages.
    This class also creates the messages based on each network.
    """
    TABLE = DBLoader().get_table(ABSDao.DATABASE_NAME.get('virtual_machine'))
    CLASS = DBLoader().get_base_class(ABSDao.DATABASE_NAME.get('virtual_machine'))

    EVENT_TYPE = 'instance_event'
    FOREIGN_KEY = 'uuid'
    INNER_OBJ = 'vm'
    DB_MAP = dict(location='location', name='name', tenant_id='tenantId', user_id='userId', hostname='hostName',
                  host_ip='hostIp', instance_id='instanceId', uuid='uuid', image_id='imageId',
                  reported_time='reportedTime', resource_id='resourceId', )

    def snapshot(self):
        """
        Override the parent method since it needs to support the inclusion of networks. However paren'ts method is used
        to create the bases of the snapshot.
        :return: dict with queried type messages
        """
        snapshot = super(VirtualMachineDAO, self).snapshot()
        for entry in snapshot:
            vm = entry.get(VirtualMachineDAO.INNER_OBJ)
            vm['network'] = VMNetworkDAO(self.session, vm.get(VirtualMachineDAO.FOREIGN_KEY)).snapshot()
        return snapshot


class VMNetworkDAO(ABSDao):
    """
    VM Network DAO abstraction to create each VM network.
    """
    TABLE = DBLoader().get_table(ABSDao.DATABASE_NAME.get('vm_network'))
    CLASS = DBLoader().get_base_class(ABSDao.DATABASE_NAME.get('vm_network'))

    DB_MAP = dict(mac='mac', iface='iface', dhcp='dhcp', gateway='gateway', dns='dns', ip='vmIp',
                  network_id='networkId', port_id='portId', ovs_id='ovsId', segmentation_id='segmentationId',
                  network_reported_time='reportedTime', network_resource_id='resourceId')

    @staticmethod
    def __create_message__(row):
        """
        Override create message method, since no state, inner object or event type are needed FOR NOW.
        :param row:
        :return:
        """
        network = dict()
        for key, value in VMNetworkDAO.DB_MAP.items():
            network[key] = row.pop(value, None)
        return VMNetworkDAO.__clean_dict__(network)

    def __init__(self, session, vm):
        """
        Overrides ABS init because each Network needs to be related to a VM.
        :param session: The DB connection to use in the queries.
        :param vm: The VM the networks will relate to
        """
        super().__init__(session)
        self.vm = vm

    def snapshot(self):
        """
        Override the parent method since it needs to support the instance id of . However paren'ts method is used
        to create the bases of the snapshot.
        :return: dict with queried type messages
        """
        rows = self.query_by_filer(VirtualMachineDAO.DB_MAP.get(VirtualMachineDAO.DB_MAP.get(VirtualMachineDAO.FOREIGN_KEY)), self.vm)
        self.rows = list()
        for row in rows:
            self.rows.append(dict(zip(VMNetworkDAO.TABLE.columns.keys(), row)))
        return [VMNetworkDAO.__create_message__(row) for row in self.rows]
