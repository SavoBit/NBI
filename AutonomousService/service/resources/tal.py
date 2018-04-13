from falcon import before, HTTPNotFound, HTTP_201, HTTP_204

from service.conf_reader import ConfReader
from service.model.tal import Tal
from service.requester import request_post_patch, request
from service.resources import BaseResource
from service.resources.symptom import prepare_query
from service.utils import parse_multiple_parameters


class TALService(BaseResource):
    ROUTES = [
        '/tal/{tal_id}',
        '/tal/{tal_id}/',
        '/tal/',
        '/tal',
    ]

    @before(parse_multiple_parameters)
    def on_get(self, req, resp, **kwargs):
        """
        diagnosis.symptom.oid

        :param req:
        :param resp:
        :param kwargs:
        :return:
        """

        offset, limit, query = prepare_query(req)

        value, offset = Tal.objects.find(query=query, limit=limit,
                                         offset=offset)
        if not kwargs:
            tal = self._get_tal_list_(req, resp, value)
        else:
            for _tal_ in value:
                if kwargs.get('tal_id') == _tal_.get('reaction')[0].get('diagnosis').get('symptom').get('oid'):
                    _tal_.pop('className')
                    tal = _tal_
                    break

        if not tal:
            raise HTTPNotFound()

        response = dict(tal=tal)
        if offset:
            response['offset'] = offset
        resp.body = self.format_body(response, from_dict=True, paginate=True, req=req)

    def _get_tal_list_(self, req, resp, value):
        _tal_ = list(
            map(lambda _value_: _value_.get('reaction')[0].get('diagnosis').get('symptom').get('oid'), value))

        # Collect symptom status
        status = request(ConfReader().get('TAL_WP4_ENGINE', 'url')).json()

        tal_list = []
        for symptom in _tal_:
            symptom_status = status.get(symptom, 'disabled')
            tal_list.append(dict(symptom=symptom, status=symptom_status))
        return tal_list

    def on_post(self, req, resp, **kwargs):
        """

        :param req:
        :param resp:
        :param kwargs:
        :return:
        """
        tal_script = req.stream.read().decode('utf-8')
        tal_script = tal_script.replace("encoding='utf8'", 'encoding="UTF-8"')
        request_post_patch(ConfReader().get('TAL_SERVICE', 'url'), method='POST',
                           headers={'Content-Type': 'application/xml'},
                           data=tal_script)
        resp.status = HTTP_201

    def on_delete(self, req, resp, tal_id):
        """

        :param req:
        :param resp:
        :param tal_id:
        :return:
        """
        request(ConfReader().get('TAL_SERVICE', 'url') + tal_id, method='DELETE')
        resp.status = HTTP_204
