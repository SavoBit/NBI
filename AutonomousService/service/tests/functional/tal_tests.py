import json
import xml.etree.ElementTree as ET

from pkg_resources import resource_filename as rf

from service.tests.functional import IntelligenceTestCase


class TALTest(IntelligenceTestCase):
    ENDPOINT = '/nbi/autonomous/api/tal'

    def test_get_all_tal(self):
        """
        Test that validates if user can collect all TAL objects
        It asserts the response code 200 and the status in each result
        :return:
        """
        result = self.app.get(TALTest.ENDPOINT, headers={'X-Auth-Token': self.cloud_admin})
        self.assertEqual(result.status, 200)
        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('links' in data)
        self.assertTrue('tal' in data)
        for obj in data.get('tal'):
            self.assertTrue('status' in obj.keys())

    def test_get_tal(self):
        """
        Test that validates if user can collect a single TAL object
        It asserts the response code 200 and the links, tal and reaction in response body
        :return:
        """
        endpoint = TALTest.ENDPOINT + '/SP_LOOP_I'
        result = self.app.get(endpoint, headers={'X-Auth-Token': self.cloud_admin})
        self.assertEqual(result.status, 200)
        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('links' in data)
        self.assertTrue('tal' in data)
        self.assertTrue('reaction' in data.get('tal'))

    def test_crud_tal(self):
        """
        Test that validates the complete cycle of a TAL
        1 - Create TAL, it asserts the response code 201
        2 - Collect TAL, it asserts the response code 200
        3 - Delete TAL, it asserts the response code 204
        :return:
        """
        self.create_tal()
        self.get_tal('NBI_TEST')
        self.delete_tal('NBI_TEST')

    def create_tal(self):
        # Load file
        tal_script = ET.parse(rf(__name__, 'etc/tal.xml'))
        result = self.app.post(TALTest.ENDPOINT,
                               headers={'X-Auth-Token': self.cloud_admin},
                               params=ET.tostring(tal_script.getroot(), encoding='utf8', method='xml'))
        self.assertEqual(result.status, 201)

    def get_tal(self, tal_id):
        result = self.app.get(TALTest.ENDPOINT + '/' + tal_id, headers={'X-Auth-Token': self.cloud_admin})
        self.assertEqual(result.status, 200)

    def delete_tal(self, tal_id):
        result = self.app.delete(TALTest.ENDPOINT + '/' + tal_id, headers={'X-Auth-Token': self.cloud_admin})
        self.assertEqual(result.status, 204)
