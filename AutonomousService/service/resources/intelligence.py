from service.model.intelligence import IntelligenceModel
from service.resources import BaseResource

SERVICE_NAME = 'Intelligence'


class IntelligenceModelService(BaseResource):
    ROUTES = [
        "/intelligence/model",
        "/intelligence/model/"
    ]

    def on_get(self, req, resp):
        values, offset = IntelligenceModel.objects.find()
        data = dict(intelligence_models=values)
        if offset:
            data['offset'] = offset
        resp.body = self.format_body(data, from_dict=True, paginate=True, req=req)
