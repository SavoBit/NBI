from service.model.topology import Topology
from service.model.db.dao.topology.virtual import VirtualMachineDAO, VMNetworkDAO
from service.error import handle_topology_exception


class InventoryRepresentation(object):

    @classmethod
    def build_from_dict(cls, d):
        created = d.get('created_at')
        status = d.get('service_status')
        service_type = d.get('service_type')
        service_id = d.get('service_id')
        return InventoryRepresentation(status, service_type, service_id, created=created)

    def __init__(self, status, obj_type, obj_id, **kwargs):
        self.id = obj_id
        if kwargs and 'created' in kwargs:
            self.created = kwargs.get('created')
        self.status = status
        self.type = obj_type


class Service(InventoryRepresentation):

    @classmethod
    def build_from_dict(cls, d):
        created = d.get('created_at')
        status = d.get('service_status')
        service_type = d.get('service_type')
        service_id = d.get('service_id')
        service_info = d.get('service_info')
        lifecycle_status = d.get('lifecycle_status')
        related_services = d.get('related_services')

        sdn_apps = [
            APP.build_from_dict(app) for app in d.get('apps', {})
            if 'VNF' not in app.get('app_class') and not app.get('ns_instance_id', None)
        ]

        network_services = []
        for ns in d.get('network_services'):
            ns_instance = NetworkService.build_from_dict(ns)
            Service.__build_network_services__(ns_instance, d.get('apps', {}))
            network_services.append(ns_instance)

        return Service(
            status, service_type, service_id, created,
            service_info, lifecycle_status, related_services,
            network_services, sdn_apps
        )

    @classmethod
    def __build_network_services__(cls, ns, apps):
        for app in apps:
            if app.get('ns_instance_id') == ns.id:
                ns.append_app(APP.build_from_dict(app), sdn='VNF' not in app.get('app_class'))

    def __init__(self, status, obj_type, obj_id, created,
                 service_info, lifecycle_status, related_services,
                 network_services, sdn_apps):
        super(Service, self).__init__(status, obj_type, obj_id, created=created)
        self.info = service_info
        self.lifecycle = lifecycle_status
        self.related_services = related_services
        self.network_services = network_services
        self.sdn_apps = sdn_apps


class NetworkService(InventoryRepresentation):

    @classmethod
    def build_from_dict(cls, d_ns):
        ns_status = d_ns.get('ns_status')
        nfvo_id = d_ns.get('nfvo_id')
        ns_instance_id = d_ns.get('ns_instance_id')
        ns_type = d_ns.get('ns_type')
        return NetworkService(ns_status, ns_type, ns_instance_id, nfvo_id)

    def __init__(self, status, obj_type, obj_id, nfvo_id, **kwargs):
        super(NetworkService, self).__init__(status, obj_type, obj_id)
        self.nfvo = nfvo_id

        self.apps = []
        if kwargs and 'apps' in kwargs:
            self.apps = kwargs.get('apps')

        self.sdn_apps = []
        if kwargs and 'sdn_apps' in kwargs:
            self.sdn_apps = kwargs.get('sdn_apps')

    def append_app(self, app, sdn=False):
        self.apps.append(app) if not sdn else self.sdn_apps.append(app)


class APP(InventoryRepresentation):

    @classmethod
    def build_from_dict(cls, d):
        app_class = d.get('app_class')
        app_type = d.get('app_type')
        location = d.get('location')
        app_instance_id = d.get('app_instance_id')
        status = d.get('status')
        vm_ids = None
        if d.get('vm_ids', None):
            vm_ids = [vm.get('vim_vm_id', None) for vm in d.get('vm_ids', None)]
        return APP(status, app_type, app_instance_id, app_class, location, vm_ids)

    @handle_topology_exception
    def __init__(self, status, obj_type, obj_id, app_class, location, vms=None):
        super(APP, self).__init__(status, obj_type, obj_id)
        self.app_class = app_class
        self.location = location
        if vms:
            self.virtual_machines = []
            for vm in vms:
                vm__ = Topology().query_by_multiple_filters(VirtualMachineDAO.TABLE, clean=False, uuid=vm)
                vm__ = vm__[0]
                for key, value in VirtualMachineDAO.DB_MAP.items():
                    if value in vm__.keys():
                        vm__[key] = vm__.pop(value)
                vm__['network'] = []
                for net in Topology().query_by_multiple_filters(VMNetworkDAO.TABLE, clean=False, uuid=vm):
                    for key, value in VMNetworkDAO.DB_MAP.items():
                        if value in net.keys():
                            net[key] = net.pop(value)
                    vm__['network'].append(net)
                self.virtual_machines.append(vm__)
