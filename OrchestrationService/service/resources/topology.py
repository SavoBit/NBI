from falcon import HTTP_NOT_IMPLEMENTED, HTTPError, before

from service.model.topology import Topology
from service.resources import BaseResource
from service.utils import parse_multiple_parameters
from service.model.db.dao.topology.virtual import VirtualMachineDAO, VMNetworkDAO
from service.model.db.dao.topology.lte import UEDAO


SERVICE_NAME = 'Topology'


class Snapshot(BaseResource):

    ROUTES = [
        '/topology/snapshot',
        '/topology/snapshot/'
    ]

    def on_get(self, req, resp):
        topology = Topology.get_topology()
        resp.body = self.format_body(topology, from_dict=True)


class TopologyLTEUser(BaseResource):

    ROUTES = [
        '/topology/lte/ue/ip/{ip}',
        '/topology/lte/ue/ip/{ip}/'
    ]

    def on_get(self, req, resp, ip):
        ues = Topology().query_by_multiple_filters(
            UEDAO.TABLE,
            clean=False,
            UEIP=ip
        )
        ue = [TopologyVM.translate_db_to_dao(ue, UEDAO.DB_MAP) for ue in ues]
        resp.body = self.format_body(ue, from_dict=True)


class ENB(BaseResource):

    ROUTES = [
        '/topology/lte/ue/enb',
        '/topology/lte/ue/enb/'
    ]

    def on_get(self, req, resp):
        resp.body = self.format_body(dict(enb=Topology().get_enb()), from_dict=True)


class TopologyVM(BaseResource):

    ROUTES = [
        '/topology/vm/',
        '/topology/vm'
    ]

    @before(parse_multiple_parameters)
    def on_get(self, req, resp, **kwargs):

        # Create the filter fields
        vm_columns = []
        network_columns = []

        # Create the search dictionaries
        search_vm = dict()
        search_network = dict()

        # Translates the search criteria to DB fields
        for key in req.query_context.get('search_by').keys():

            if key in VirtualMachineDAO.DB_MAP.keys():
                new_key = VirtualMachineDAO.DB_MAP.get(key)
                search_vm[new_key] = req.query_context.get('search_by').get(key)
            elif key in VMNetworkDAO.DB_MAP.keys():
                new_key = VMNetworkDAO.DB_MAP.get(key)
                search_network[new_key] = req.query_context.get('search_by').get(key)

        # Translates the filter criteria to DB fields
        for filter_ in req.query_context.get('filter'):
            if filter_ in VirtualMachineDAO.DB_MAP.keys():
                vm_columns.append(VirtualMachineDAO.DB_MAP.get(filter_))
            elif filter_ in VMNetworkDAO.DB_MAP.keys():
                network_columns.append(VMNetworkDAO.DB_MAP.get(filter_))
            elif filter_ == 'network':
                vm_columns.append('network')

        if len(search_network.keys()) > 0 and len(search_vm.keys()) == 0:
            self.__search_vm_by_network(req, resp, vm_columns, network_columns, search_vm, search_network)
        else:
            self.__search_vm__(req, resp, vm_columns, network_columns, search_vm, search_network)

    def __search_vm__(self, req, resp, vm_columns, network_columns, search_vm, search_network):

        foreign_key = VirtualMachineDAO.DB_MAP.get(VirtualMachineDAO.FOREIGN_KEY)

        # Append the foreign_key (uuid) if not already provided
        if foreign_key not in vm_columns:
            vm_columns.append(foreign_key)

        # Check if the result must be filtered
        clean = len(vm_columns) > 1 or len(network_columns) > 0

        # Search VMs
        vms = Topology().query_by_multiple_filters(
            VirtualMachineDAO.TABLE,
            *vm_columns,
            clean=clean,
            **search_vm
        )

        # Check if network result must be filtered
        clean = len(network_columns) > 0
        to_remove = []

        # Translates the DB fields to DAO fields
        vms = [TopologyVM.translate_db_to_dao(vm, VirtualMachineDAO.DB_MAP) for vm in vms]

        for idx, vm in enumerate(vms):
            search_network[foreign_key] = vm.get(VirtualMachineDAO.FOREIGN_KEY)  # Append the foreign key
            networks = Topology().query_by_multiple_filters(
                VMNetworkDAO.TABLE,
                *network_columns,
                clean=clean,
                **search_network
            )

            # Remove the VM if network criteria don't match
            if len(networks) == 0 and len(network_columns) > 0:
                to_remove.append(idx)
                continue

            # Append the network if the network was requested
            if len(networks) == 0\
                    or len(vm_columns) > 1 and 'network' not in vm_columns and len(network_columns) == 0:
                continue

            vm['network'] = []
            for n in networks:
                # Translates the DB fields to DAO fields
                n = TopologyVM.translate_db_to_dao(n, VMNetworkDAO.DB_MAP)
                n.pop('uuid', None)
                vm['network'].append(n)

        vms = [i for j, i in enumerate(vms) if j not in to_remove]  # Clean empty network VMs
        resp.body = self.format_body(vms, from_dict=True)

    def __search_vm_by_network(self, req, resp, vm_columns, network_columns, search_vm, search_network):

        vms = []

        foreign_key = VirtualMachineDAO.DB_MAP.get(VirtualMachineDAO.FOREIGN_KEY)

        # Append the foreign_key (uuid) if not already provided
        network_columns.append(foreign_key)
        if foreign_key not in vm_columns:
            vm_columns.append(foreign_key)

        clean = len(network_columns) > 1  # Check if the network result must be filtered

        networks = Topology().query_by_multiple_filters(
            VMNetworkDAO.TABLE,
            *network_columns,
            clean=clean,
            **search_network
        )

        clean = len(vm_columns) > 1 or len(network_columns) > 1  # Check if the result must be filtered
        for n in networks:
            vm = Topology().query_by_multiple_filters(
                VirtualMachineDAO.TABLE,
                *vm_columns,
                clean=clean,
                uuid=n.get('uuid')
            )

            if vm:
                vm = vm[0]
            else:
                continue

            # Translates the DB fields to DAO fields
            n = TopologyVM.translate_db_to_dao(n, VMNetworkDAO.DB_MAP)

            # Search if the VM already existis
            __vm__ = next((item for item in vms if item['uuid'] == n.get('uuid')), None)

            # Create the VM if don't exist
            if not __vm__:
                vm['network'] = []
                __vm__ = vm

                # Translates the DB fields to DAO fields
                vm = TopologyVM.translate_db_to_dao(vm, VirtualMachineDAO.DB_MAP)
                vms.append(vm)
                n.pop('uuid')

            if 'network' in vm_columns \
                    or len(network_columns) > 1 \
                    or len(network_columns) == 1 and len(vm_columns) == 1:
                __vm__['network'].append(n)
            else:
                __vm__.pop('network', None)

        resp.body = self.format_body(vms, from_dict=True)

    @staticmethod
    def translate_db_to_dao(item, dictionary):
        for key, value in dictionary.items():
            if value in item.keys():
                item[key] = item.pop(value)
        return item


class Location(BaseResource):

    ROUTES = [
        '/topology/locations',
        '/topology/locations/'
    ]

    def on_get(self, req, resp):
        resp.body = self.format_body(dict(locations=Topology().get_all_locations()), from_dict=True)
