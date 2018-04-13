import json

from service.tests.functional import IntelligenceTestCase


class TestNBIIntelligenceModels(IntelligenceTestCase):
    ROUTE = '/nbi/autonomous/api/intelligence/model/'

    def __login_user__(self, username, password, tenant):
        auth = dict(username=username, password=password, tenant=tenant)
        result = self.app.post('/nbi/auth/api/login', params=json.dumps(dict(auth=auth)))
        return result.header_dict.get('x-subject-token')

    def test_get_model(self):
        """
        Test that the intelligence models can be collected on the database.
        It asserts the response code 200 and the response body:
            intelligence_models:
                meta: the meta data referenced by the models
                computation: the model representation
        :return:
        """
        result = self.app.get(TestNBIIntelligenceModels.ROUTE, headers={'X-Auth-Token': self.cloud_admin})
        self.assertEqual(result.status, 200)
        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('intelligence_models' in data)
        data = data.get('intelligence_models')[0]
        self.assertTrue('meta' in data)

    def test_get_model_unauth(self):
        """
        Test that the intelligence models can't be collected on the database by unauthenticated users.
        It asserts the response code 401:
        :return:
        """
        result = self.app.get(TestNBIIntelligenceModels.ROUTE, status=401)
        self.assertEqual(result.status, 401)
