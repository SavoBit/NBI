import logging
from collections import OrderedDict

from service.model.db.dao.topology.lte import UEDAO
from service.model.db.dao.topology.virtual import VirtualMachineDAO
from service.model.db.dao.topology.physical import PhysicalDAO
from service.model.db.db_parser import DBLoader
from service.utils import Singleton
from service.error import handle_topology_exception

logger = logging.getLogger(__name__)


class Topology(metaclass=Singleton):
    """
    Class that represents the current topology. It is only instantiated once and it stores a
    dictionary to return the current topology without queering the DB. This topology can be
    invalidated forcing to query a new one.
    """

    LOADER = OrderedDict()
    LOADER['physical'] = PhysicalDAO
    LOADER['virtual'] = VirtualMachineDAO
    LOADER['ue'] = UEDAO

    @staticmethod
    def get_topology():
        """
        Creates the current topology.
        If topology dict is empty it queries the DB otherwise it will be returned as is.
        Because object references are used, a copy of the topology is sent in case the object is being read by a
        client and invalidated during the operation,
        allowing the client to keep the messages and receive the new ones only.
        :return: A dict with the current topology.
        """
        DBLoader().get_table('pm')
        return Topology.__load_topology__()

    @staticmethod
    def __load_topology__():
        """
        Loads the topology into the dictionary.
        It uses the class mapping with the key to use and the DAO to obtain the snapshot.
        The topology must be saved in an ordered dict to send the messages as they were introduced in the system.
        :return: Ordered Dict with the topology.
        """
        topology = OrderedDict()
        for key, obj in Topology.LOADER.items():
            try:
                session = DBLoader().create_session()
                topology[key] = obj(session).snapshot()
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()
        return topology

    @handle_topology_exception
    def query_by_multiple_filters(self, table, *filter_by, clean=True, **kwargs):
        session = DBLoader().create_session()
        try:
            objs = session.query(table).filter_by(**kwargs).all()
            response = []
            for row in objs:
                r = dict(zip(table.columns.keys(), row))
                if clean:
                    self.__clean_filter__(r, table, *filter_by)
                response.append(r)
            return response
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def __clean_filter__(self, r, table, *filter_by):
        for f in table.columns.keys():
            if f not in filter_by:
                r.pop(f)

    @handle_topology_exception
    def get_all_locations(self):
        session = DBLoader().create_session()
        try:
            locations_ = session.query(VirtualMachineDAO.CLASS.location).distinct().all()
            locations = []
            for l in locations_:
                locations.append(l[0])
            return locations
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @handle_topology_exception
    def get_enb(self):
        session = DBLoader().create_session()
        try:
            enb_ = session.query(UEDAO.CLASS.enbIPS1U).distinct().all()
            enb = []
            for ip in enb_:
                enb.append(ip[0])
            return enb
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
