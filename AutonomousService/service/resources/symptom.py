import logging
import re

from falcon import before, HTTPBadRequest

from service.model.symptom import SymptomActionCase
from service.resources import BaseResource
from service.utils import parse_multiple_parameters

logger = logging.getLogger(__name__)

QUERY_DATE_RANGE = {
    'created':
        [{'created_since': 'start'}, {'created_to': 'end'}],
    'updated':
        [{'updated_since': 'start'}, {'updated_to': 'end'}]
}

SIMPLE_OBJECT = ['created', 'updated', 'symptom_id', 'symptom', 'hash']


def prepare_query(req):
    """
    Prepares query with date fields and collects the offset and limit for query parameters
    :param req: The request object with query string dictionary.
    :raises ValueError when limit contains non numeric values
    :return: Offset, limit and query
    """

    offset = req.query_context.get('offset', None)
    try:
        limit = int(req.query_context.get('limit', 9999))
    except ValueError:
        logger.error('Invalid limit provided')
        raise HTTPBadRequest(title='Invalid Parameter', description='Limit must be an int value', code='202')

    query = {}

    for key, value in QUERY_DATE_RANGE.items():
        for obj in value:
            for inner_key, inner_value in obj.items():
                if inner_key in req.context['query_parameters']:
                    SymptomActionCase.objects.create_range_date(
                        query, key, **{inner_value: req.context['query_parameters'].get(inner_key)})
    return offset, limit, query


class SymptomService(BaseResource):
    ROUTES = [
        '/symptom/{symptom_type}/{hash}',
        '/symptom/{symptom_type}/{hash}/',
        '/symptom/{symptom_type}',
        '/symptom/{symptom_type}/',
        '/symptom/',
        '/symptom'
    ]

    @before(parse_multiple_parameters)
    def on_get(self, req, resp, **kwargs):
        """
        Method to list symptoms

        :param req: Request parameter it accepts the following query parameters:
        limit: Numeric value of the analysed symptoms
        offset: MongoDB ID of the last symptom analysed
        :param resp:
        :param kwargs:
                symptom_type: The symptom type to be used
                hash: The hash that uniquely identifies the symptom
        :return:
                200 OK
                400 Bad Request - When invalid limit provided
                408 Time Out - When no connection to the database
        """
        offset, limit, query = prepare_query(req)

        if not kwargs:
            value, offset = SymptomActionCase.objects.find(*SIMPLE_OBJECT, query=query, limit=limit,
                                                           offset=offset)
        elif 'hash' not in kwargs:
            query['symptom_id'] = kwargs.get('symptom_type')
            value, offset = SymptomActionCase.objects.find(*SIMPLE_OBJECT,
                                                           query=query,
                                                           limit=limit, offset=offset)
        else:
            query['symptom_id'] = kwargs.get('symptom_type')
            query['hash'] = kwargs.get('hash')
            value, offset = SymptomActionCase.objects.find(
                query=query,
                limit=limit, offset=offset)
            if value:
                SymptomService.__convert_action_report__(value[0])

        # REMOVE THE ID and convert datetime
        for v in value:
            for key in QUERY_DATE_RANGE.keys():
                v[key] = v.get(key).strftime("%Y-%m-%d %H:%M:%S")
            v.pop('id', None)
            v.pop('_id', None)

        response = dict(symptoms=value)
        if offset:
            response['offset'] = offset
        resp.body = self.format_body(response, from_dict=True, paginate=True, req=req)

    @staticmethod
    def __convert_action_report__(value):
        # Put the Action status on the tactic
        for key, obj in value.get('actions').items():
            actions = list(filter(
                lambda inner_action:
                inner_action.get('actionOption').get('id') == key,
                value.get('tactic').get('action')))

            if actions:
                action = actions[0]
                action['status'] = obj.get('status')
        value.pop('actions')


class SymptomAffectedIPs(BaseResource):
    """
    Class to collect the list of IPs that are associated with symptoms
    """

    ROUTES = [
        '/symptom/affected/{symptom_type}',
        '/symptom/affected/{symptom_type}/',
        '/symptom/affected',
        '/symptom/affected/'
    ]

    SIMPLE_OBJECT = ['symptom_id', 'symptom', 'hash']

    @before(parse_multiple_parameters)
    def on_get(self, req, resp, **kwargs):
        """
        Method to list IPs associated with a symptom.

        It returns a list of dicts with the IPs as the key and the values
        being the type of association with the symptom, the hash
        and the symptom type to query the symptom.

        :param req: Request parameter it accepts the following query parameters:
                limit: Numeric value of the analysed symptoms
                offset: MongoDB ID of the last symptom analysed
        :param resp:
        :param kwargs:
                symptom_type: The symptom type to be used
        :return:
                200 OK
                400 Bad Request - When invalid limit provided
        """
        offset, limit, query = prepare_query(req)
        if 'symptom_id' in kwargs:
            query['symptom_id'] = kwargs.get('symptom_type')

        value, offset = SymptomActionCase.objects.find(*SymptomAffectedIPs.SIMPLE_OBJECT,
                                                       query=query,
                                                       limit=limit, offset=offset)
        affected = dict()
        for v in value:
            for key, value in v.get('symptom').items():
                if isinstance(value, str) and re.match('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', value):
                    if value not in affected.keys():
                        affected[value] = list()
                    symptom = dict(hash=v.get('hash'), symptom_id=v.get('symptom_id'), parameter=key)
                    affected[value].append(symptom)

        response = dict(affected_ips=affected)
        if offset:
            response['offset'] = offset
        resp.body = self.format_body(response, from_dict=True, paginate=True, req=req)
