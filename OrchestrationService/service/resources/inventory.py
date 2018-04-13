from falcon import HTTP_200, HTTPNotFound

from service.resources import BaseResource
from service.conf_reader import ConfReader
from service.requester import request
from service.model.inventory import InventoryRepresentation, Service
from service.model.topology import Topology
from service.model.db.dao.topology.virtual import VirtualMachineDAO, VMNetworkDAO

SERVICE_NAME = 'Service Inventory'


class Services(BaseResource):
    ROUTES = [
        "/services",
        "/services/{s_id}"
    ]

    @staticmethod
    def __request_service__(s_id):
        endpoint = '{}/{}'.format(ConfReader().get('SERVICE_INVENTORY', 'url'), s_id)
        r = request(endpoint, service_name=SERVICE_NAME)
        return Service.build_from_dict(r.json())

    def on_get(self, req, resp, **kwargs):
        if kwargs and 's_id' in kwargs:
            return self.get_instance(req, resp, kwargs.pop('s_id'), **kwargs)
        else:
            self.get_all(req, resp, **kwargs)

    def get_all(self, req, resp, **kwargs):
        r = request(ConfReader().get('SERVICE_INVENTORY', 'url'), service_name=SERVICE_NAME)
        services = []
        for service in r.json():
            services.append(InventoryRepresentation.build_from_dict(service).__dict__)

        resp.status = HTTP_200
        resp.body = self.format_body(services)

    def get_instance(self, req, resp, s_id, **kwargs):
        resp.body = self.format_body(
            Services.__request_service__(s_id)
        )


class NetworkServices(BaseResource):
    ROUTES = [
        "/services/{s_id}/network-services",
        "/services/{s_id}/network-services/{ns_id}"
    ]

    def on_get(self, req, resp, **kwargs):
        if kwargs and 'ns_id' in kwargs:
            return self.get_instance(req, resp, kwargs.pop('ns_id'), **kwargs)
        else:
            self.get_all(req, resp, **kwargs)

    def get_all(self, req, resp, **kwargs):
        s = Services.__request_service__(kwargs.get('s_id'))
        resp.body = self.format_body(s.network_services)

    def get_instance(self, req, resp, ns_id, **kwargs):
        s = Services.__request_service__(kwargs.get('s_id'))
        for ns in s.network_services:
            if ns.id == ns_id:
                resp.body = self.format_body(ns)
                return
        raise HTTPNotFound()


class SDNAPPs(BaseResource):
    ROUTES = [
        "/services/{s_id}/sdn-apps",
        "/services/{s_id}/sdn-apps/{app_id}"
    ]

    def on_get(self, req, resp, **kwargs):
        if kwargs and 'app_id' in kwargs:
            return self.get_instance(req, resp, kwargs.pop('app_id'), **kwargs)
        else:
            self.get_all(req, resp, **kwargs)

    def get_all(self, req, resp, **kwargs):
        s = Services.__request_service__(kwargs.get('s_id'))
        resp.body = self.format_body(s.sdn_apps)

    def get_instance(self, req, resp, app_id, **kwargs):
        s = Services.__request_service__(kwargs.get('s_id'))
        for app in s.sdn_apps:
            if app.id == app_id:
                resp.body = self.format_body(app)
                return
        raise HTTPNotFound()


class VNFAPPs(BaseResource):
    ROUTES = [
        "/services/{s_id}/network-services/{ns_id}/apps",
        "/services/{s_id}/network-services/{ns_id}/apps/{app_id}"
    ]

    @staticmethod
    def __get_apps__(service, ns_id):
        for ns in service.network_services:
            if ns.id == ns_id:
                return ns.apps
        raise HTTPNotFound

    def on_get(self, req, resp, **kwargs):
        if kwargs and 'app_id' in kwargs:
            return self.get_instance(req, resp, kwargs.pop('app_id'), **kwargs)
        else:
            self.get_all(req, resp, **kwargs)

    def get_all(self, req, resp, **kwargs):
        s = Services.__request_service__(kwargs.get('s_id'))
        resp.body = self.format_body(VNFAPPs.__get_apps__(s, kwargs.get('ns_id')))

    def get_instance(self, req, resp, app_id, **kwargs):
        s = Services.__request_service__(kwargs.get('s_id'))
        apps = VNFAPPs.__get_apps__(s, kwargs.get('ns_id'))
        for app in apps:
            if app.id == app_id:
                resp.body = self.format_body(app)
                return
        raise HTTPNotFound


class VMs(BaseResource):
    ROUTES = [
        "/services/{s_id}/network-services/{ns_id}/apps/{app_id}/virtual-machines",
        "/services/{s_id}/network-services/{ns_id}/apps/{app_id}/virtual-machines/{vm_id}"
    ]

    @staticmethod
    def __get_vms__(service, ns_id, app_id):
        apps = VNFAPPs.__get_apps__(service, ns_id)
        for app in apps:
            if app.id == app_id:
                return app.vm_ids
        raise HTTPNotFound

    def on_get(self, req, resp, **kwargs):
        if kwargs and 'vm_id' in kwargs:
            self.get_instance(req, resp, **kwargs)
        else:
            self.get_all(req, resp, **kwargs)

    def get_all(self, req, resp, **kwargs):
        s = Services.__request_service__(kwargs.get('s_id'))
        vms = self.__get_vms__(s, kwargs.get('ns_id'), kwargs.get('app_id'))
        virtual_machines = []
        for vm in vms:
            vm__ = Topology().query_by_multiple_filters(VirtualMachineDAO.TABLE, clean=False, uuid=vm)[0]
            vm__['network'] = []
            for net in Topology().query_by_multiple_filters(VMNetworkDAO.TABLE, clean=False, uuid=vm):
                vm__['network'].append(net)
            virtual_machines.append(vm__)
            resp.body = self.format_body(dict(vms=virtual_machines), from_dict=True)

    def get_instance(self, req, resp, **kwargs):
        s = Services.__request_service__(kwargs.get('s_id'))
        vms = self.__get_vms__(s, kwargs.get('ns_id'), kwargs.get('app_id'))
        for vm in vms:
            if vm == kwargs.get('vm_id'):
                vm__ = Topology().query_by_multiple_filters(VirtualMachineDAO.TABLE, clean=False, uuid=vm)[0]
                vm__['network'] = []
                for net in Topology().query_by_multiple_filters(VMNetworkDAO.TABLE, clean=False, uuid=vm):
                    vm__['network'].append(net)
        resp.body = self.format_body(vm__, from_dict=True)