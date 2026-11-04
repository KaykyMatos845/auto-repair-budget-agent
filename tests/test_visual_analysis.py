import base64
import copy
import io
import json
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import patch
import urllib.error
import urllib.request
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server

PNG = base64.b64encode(b'\x89PNG\r\n\x1a\n' + b'fixture').decode()


def observation():
    return {'vehicle': {'brand': '', 'model': '', 'year': '', 'color': ''},
            'imageQuality': {'usable': True, 'issues': []}, 'limitations': [],
            'damageAnalysis': {'summary': 'Trinca visível na lente.', 'parts': [
                {'name': 'Lanterna esquerda', 'category': 'Iluminação',
                 'evidence': 'Trinca atravessa a lente vermelha.', 'imageIndex': 0, 'box': [10, 20, 30, 40]}]}}


class VisualContractTests(unittest.TestCase):
    def test_missing_key_does_not_call_provider(self):
        with patch.object(server, 'get_gemini_api_key', return_value=''), patch.object(server.urllib.request, 'urlopen') as remote:
            self.assertEqual(server.call_gemini_vision([PNG]), (None, 'NO_API_KEY'))
            remote.assert_not_called()

    def test_no_synthetic_fallback(self):
        with self.assertRaises(ValueError):
            server.build_analysis_response(None, {})

    def test_evidence_and_image_reference_required(self):
        for changes in [{'evidence': ''}, {'imageIndex': 2}, {'imageIndex': True}, {'box': [90, 20, 10, 40]}]:
            with self.subTest(changes=changes):
                data = observation()
                data['damageAnalysis']['parts'][0].update(changes)
                with self.assertRaises(ValueError):
                    server.build_analysis_response(data, {}, 2)

    def test_model_costs_actions_and_hours_are_not_trusted(self):
        data = observation()
        data['damageAnalysis']['parts'][0].update({'newPrice': {'price': 1}, 'ops': {'mec': 99},
                                                  'actionRequired': 'Substituição', 'reviewed': True})
        result = server.build_analysis_response(data, {}, 1)
        part = result['parts'][0]
        self.assertNotEqual(part['newPrice']['price'], 1)
        self.assertEqual(sum(part['ops'].values()), 0)
        self.assertFalse(part['reviewed'])
        self.assertEqual(part['actionRequired'], 'Avaliação presencial')
        self.assertEqual(part['selectedChoice'], 'repair')
        self.assertEqual(result['vehicle']['year'], '')
        self.assertEqual(part['evidence'], data['damageAnalysis']['parts'][0]['evidence'])

    def test_box_is_not_invented(self):
        data = observation()
        del data['damageAnalysis']['parts'][0]['box']
        self.assertIsNone(server.build_analysis_response(data, {})['parts'][0]['box'])

    def test_low_quality_has_no_findings_even_if_model_supplies_them(self):
        data = observation()
        data['imageQuality'] = {'usable': False, 'issues': ['Foto desfocada']}
        result = server.build_analysis_response(data, {})
        self.assertEqual(result['analysisMode'], 'insufficient_images')
        self.assertEqual(result['parts'], [])

    def test_no_visible_damage_is_distinct_from_failure(self):
        data = observation()
        data['damageAnalysis']['parts'] = []
        result = server.build_analysis_response(data, {})
        self.assertTrue(result['aiPowered'])
        self.assertEqual(result['analysisMode'], 'visual')
        self.assertEqual(result['parts'], [])

    def test_invalid_images_rejected_and_mime_preserved(self):
        for value in [[], [PNG] * 5, ['junk'], ['!!!!'], [base64.b64encode(b'not an image').decode()]]:
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    server.prepare_images(value)
        self.assertEqual(server.prepare_images([PNG])[0]['inline_data']['mime_type'], 'image/png')

    def test_provider_request_uses_json_and_header_key(self):
        payload = {'candidates': [{'finishReason': 'STOP', 'content': {'parts': [{'text': json.dumps(observation())}]}}]}
        response = io.BytesIO(json.dumps(payload).encode())
        with patch.object(server.urllib.request, 'urlopen', return_value=response) as remote:
            result, error = server.call_gemini_vision([PNG], api_key='test-only-key')
        self.assertIsNone(error)
        self.assertEqual(result, observation())
        request = remote.call_args.args[0]
        self.assertNotIn('test-only-key', request.full_url)
        data = json.loads(request.data)
        self.assertEqual(data['generationConfig']['responseMimeType'], 'application/json')
        self.assertEqual(data['contents'][0]['parts'][1]['inline_data']['mime_type'], 'image/png')

    def test_provider_failure_does_not_expose_body(self):
        error = urllib.error.HTTPError('https://example.invalid', 429, 'quota', {}, io.BytesIO(b'private upstream data'))
        with patch.object(server.urllib.request, 'urlopen', side_effect=error):
            self.assertEqual(server.call_gemini_vision([PNG], api_key='test-only-key'), (None, 'HTTP_429'))

    def test_provider_reason_is_allowlisted_and_explained(self):
        payload = {'error': {'message': 'private content', 'details': [{'reason': 'API_KEY_INVALID'}]}}
        error = urllib.error.HTTPError('https://example.invalid', 400, 'bad request', {}, io.BytesIO(json.dumps(payload).encode()))
        with patch.object(server.urllib.request, 'urlopen', side_effect=error):
            self.assertEqual(server.call_gemini_vision([PNG], api_key='test-only-key'), (None, 'API_KEY_INVALID'))
        self.assertIn('inválida', server.vision_error_message('API_KEY_INVALID'))
        self.assertIn('cota', server.vision_error_message('HTTP_429'))

    def test_connection_failure_has_its_own_code(self):
        with patch.object(server.urllib.request, 'urlopen', side_effect=urllib.error.URLError('private connection details')):
            self.assertEqual(server.call_gemini_vision([PNG], api_key='test-only-key'), (None, 'CONNECTION_ERROR'))


class ApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = server.ThreadedTCPServer(('127.0.0.1', 0), server.AutoBudgetHandler)
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = 'http://127.0.0.1:' + str(cls.httpd.server_address[1])

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()
        cls.httpd.server_close()
        cls.thread.join()

    def post(self, body):
        request = urllib.request.Request(self.url + '/api/analyze', json.dumps(body).encode(), {'Content-Type': 'application/json'})
        try:
            response = urllib.request.urlopen(request)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            return response.status, json.load(response)

    def test_api_does_not_simulate_when_key_missing(self):
        with patch.object(server, 'get_gemini_api_key', return_value=''):
            status, body = self.post({'images': [PNG]})
        self.assertEqual(status, 503)
        self.assertFalse(body['success'])
        self.assertEqual(body['analysisMode'], 'error')
        self.assertNotIn('parts', body)

    def test_invalid_input(self):
        for body in [[], {'images': []}, {'images': ['bad']}, {'images': [PNG], 'vehicle': []}]:
            with self.subTest(body=body):
                # Nonempty invalid vehicle structure is handled as invalid input.
                if body == {'images': [PNG], 'vehicle': []}:
                    body['vehicle'] = ['invalid']
                self.assertEqual(self.post(body)[0], 400)

    def test_malformed_model_response_is_not_success(self):
        with patch.object(server, 'call_gemini_vision', return_value=({'damageAnalysis': {}}, None)):
            self.assertEqual(self.post({'images': [PNG]})[0], 502)

    def test_valid_model_response(self):
        with patch.object(server, 'call_gemini_vision', return_value=(copy.deepcopy(observation()), None)):
            status, result = self.post({'images': [PNG]})
        self.assertEqual(status, 200)
        self.assertTrue(result['aiPowered'])
        self.assertEqual(result['parts'][0]['imageIndex'], 0)


if __name__ == '__main__':
    unittest.main()
