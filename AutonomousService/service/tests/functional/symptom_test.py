import json
import re

from service.tests.functional import IntelligenceTestCase


class SymptomTest(IntelligenceTestCase):
    ENDPOINT = '/nbi/autonomous/api/symptom'

    def __validate_structure__(self, symptom):
        for field in ['hash', 'created', 'symptom', 'updated', 'symptom_id']:
            self.assertTrue(field in symptom)

    def test_get_symptoms(self):
        """
        Test that SELFNET symptoms are all collected.
        It asserts the response code 200 and the response body:
            symptoms
                hash: Unique hash to identify symptoms
                created: Symptom creation datetime
                symptom: The multiple triggers that trigger the symptom, it also includes the AlarmID
                updated: Updated date time
                symptom_id: Symptom type
        :return:
        """
        result = self.app.get(SymptomTest.ENDPOINT, headers={'X-Auth-Token': self.cloud_admin})
        self.assertEqual(result.status, 200)
        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('symptoms' in data)
        self.__validate_structure__(data.get('symptoms')[0])

    def test_get_symptoms_invalid_users(self):
        """
        Test that unauthorized users can't collect SELFNET symptoms.
        It asserts the response code 401.
        :return:
        """
        result = self.app.get(SymptomTest.ENDPOINT, status=401)
        self.assertEqual(result.status, 401)

    def test_get_symptom_by_type(self):
        """
        Test that User can Collect a given SELFNET symptom type
        It asserts the response code 200,
        validates that every response has the same type and the response body:
            symptoms
                hash: Unique hash to identify symptoms
                created: Symptom creation datetime
                symptom: The multiple triggers that trigger the symptom, it also includes the AlarmID
                updated: Updated date time
                symptom_id: Symptom type
        :return:
        """
        endpoint = SymptomTest.ENDPOINT + '/SP_LOOP_I'
        result = self.app.get(endpoint, headers={'X-Auth-Token': self.cloud_admin})
        self.assertEqual(result.status, 200)
        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('symptoms' in data)
        for symptom in data.get('symptoms'):
            self.assertEqual(symptom.get('symptom_id'), 'SP_LOOP_I')
        self.__validate_structure__(data.get('symptoms')[0])

    def test_get_symptom_by_type_hash(self):
        """
        Test that User can Collect a given SELFNET symptom type by its hash
        It asserts the response code 200,
        validates that every response has the same type and hash and the response body:
            symptoms
                hash: Unique hash to identify symptoms
                created: Symptom creation datetime
                symptom: The multiple triggers that trigger the symptom, it also includes the AlarmID
                updated: Updated date time
                symptom_id: Symptom type
        :return:
        """
        endpoint = SymptomTest.ENDPOINT + '/SP_LOOP_I/47b2635bcf776'
        result = self.app.get(endpoint, headers={'X-Auth-Token': self.cloud_admin})
        self.assertEqual(result.status, 200)
        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('symptoms' in data)
        for symptom in data.get('symptoms'):
            self.assertEqual(symptom.get('hash'), '47b2635bcf776')
            self.__validate_structure__(symptom)

    def test_get_symptom_by_filter(self):
        """
        Test that User can Collect a given SELFNET symptom using a filter
        It asserts the response code 200,
        validates that every response fulfill the specified filter and the response body:
            symptoms
                hash: Unique hash to identify symptoms
                created: Symptom creation datetime
                symptom: The multiple triggers that trigger the symptom, it also includes the AlarmID
                updated: Updated date time
                symptom_id: Symptom type
        :return:
        """
        result = self.app.get(SymptomTest.ENDPOINT, params={'created_since': '2018-03-01'},
                              headers={'X-Auth-Token': self.cloud_admin})
        self.assertEqual(result.status, 200)
        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('symptoms' in data)
        for symptom in data.get('symptoms'):
            self.assertTrue(symptom.get('created') > '2018-03-01')
            self.__validate_structure__(symptom)

    def test_limit(self):
        """
        Test that User can Collect a given SELFNET symptom using a filter limiting results
        It asserts the response code 200,
        validates that the response respects the limit and the response body:
            symptoms
                hash: Unique hash to identify symptoms
                created: Symptom creation datetime
                symptom: The multiple triggers that trigger the symptom, it also includes the AlarmID
                updated: Updated date time
                symptom_id: Symptom type
        :return:
        """
        result = self.app.get(SymptomTest.ENDPOINT, params={'limit': 5},
                              headers={'X-Auth-Token': self.cloud_admin})

        self.assertEqual(result.status, 200)
        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('symptoms' in data)
        self.assertTrue('offset' in data)
        self.assertTrue(len(data.get('symptoms')), 5)

        for symptom in data.get('symptoms'):
            self.__validate_structure__(symptom)

    def test_offset(self):
        """
        Test that User can Collect a given SELFNET symptom using a filter with an offset
        It asserts the response code 200,
        validates that the response respects the offset and the response body:
            symptoms
                hash: Unique hash to identify symptoms
                created: Symptom creation datetime
                symptom: The multiple triggers that trigger the symptom, it also includes the AlarmID
                updated: Updated date time
                symptom_id: Symptom type
        :return:
        """
        result = self.app.get(SymptomTest.ENDPOINT, params={'limit': 5, 'offset': '5a9f25faba3f842ec18e44cd'},
                              headers={'X-Auth-Token': self.cloud_admin})

        self.assertEqual(result.status, 200)
        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('symptoms' in data)
        self.assertTrue('offset' in data)
        self.assertTrue(len(data.get('symptoms')), 5)

        for symptom in data.get('symptoms'):
            self.__validate_structure__(symptom)


class AffectedIPsTest(IntelligenceTestCase):
    ENDPOINT = '/nbi/autonomous/api/symptom/affected'

    def __validate_body__(self, affected_ips):
        for key, value in affected_ips.items():
            self.assertTrue(re.match('^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', key))
            for symptom in value:
                for field in ['hash', 'parameter', 'symptom_id']:
                    self.assertTrue(field in symptom)

    def test_valid_affected_ips(self):
        """
        Test that user can collect the list of symptoms an IP is associated with.
        It asserts the response code 200 and the response body:
            affected_ips
                IP - Asserts if the key is an IPv4 address
                    List with Symptom Information
                        symptom_id - the type of symptom
                        parameter - the parameter the IP is associated with
                        hash - the unique symptom identifier
        :return:
        """
        result = self.app.get(AffectedIPsTest.ENDPOINT,
                              headers={'X-Auth-Token': self.cloud_admin})

        self.assertEqual(result.status, 200)
        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('affected_ips' in data)
        self.__validate_body__(data.get('affected_ips'))

    def test_valid_affected_ips_filter(self):
        """
        Test that user can collect the list of symptoms an IP is associated with filtering the symptom type.
        It asserts the response code 200 and the response body:
            affected_ips
                IP - Asserts if the key is an IPv4 address
                    List with Symptom Information
                        symptom_id - the type of symptom
                        parameter - the parameter the IP is associated with
                        hash - the unique symptom identifier
        :return:
        """
        result = self.app.get(AffectedIPsTest.ENDPOINT + '/SP_LOOP_I',
                              headers={'X-Auth-Token': self.cloud_admin})
        self.assertEqual(result.status, 200)
        data = json.loads(result.body.decode('utf-8'))
        self.assertTrue('affected_ips' in data)
        self.__validate_body__(data.get('affected_ips'))
