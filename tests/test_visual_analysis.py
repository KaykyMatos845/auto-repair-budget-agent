import base64
import io
import json
from pathlib import Path
import sys
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import urllib.error
import urllib.request

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import server
import local_vision as vision
import numpy as np
from PIL import Image


def encoded_photo(image):
    stream = io.BytesIO()
    image.save(stream, format='PNG')
    return base64.b64encode(stream.getvalue()).decode()


def observation():
    return {'vehicle': {'brand': '', 'model': '', 'year': '', 'color': ''},
            'imageQuality': {'usable': True, 'issues': []}, 'limitations': [],
            'damageAnalysis': {'summary': 'Sugestão local', 'parts': [
                {'name': 'Lanterna', 'category': 'Detector local', 'evidence': 'Possível dano na região marcada.',
                 'imageIndex': 0, 'box': [10, 20, 30, 40]}]}}


class ContractTests(unittest.TestCase):
    def test_no_synthetic_fallback(self):
        with self.assertRaises(ValueError):
            server.build_analysis_response(None, {})

    def test_findings_require_photo_and_region(self):
        for changes in [{'evidence': ''}, {'imageIndex': 2}, {'imageIndex': True}, {'box': [90, 20, 10, 40]}]:
            with self.subTest(changes=changes):
                data = observation()
                data['damageAnalysis']['parts'][0].update(changes)
                with self.assertRaises(ValueError):
                    server.build_analysis_response(data, {}, 2)

    def test_prices_and_work_are_not_predicted(self):
        data = observation()
        data['damageAnalysis']['parts'][0].update({'newPrice': {'price': 1}, 'ops': {'mec': 99},
                                                  'actionRequired': 'Substituição', 'reviewed': True})
        part = server.build_analysis_response(data, {}, 1)['parts'][0]
        self.assertNotEqual(part['newPrice']['price'], 1)
        self.assertEqual(sum(part['ops'].values()), 0)
        self.assertFalse(part['reviewed'])
        self.assertEqual(part['actionRequired'], 'Avaliação presencial')

    def test_low_quality_never_becomes_findings(self):
        data = observation()
        data['imageQuality'] = {'usable': False, 'issues': ['Desfocada']}
        result = server.build_analysis_response(data, {})
        self.assertEqual(result['analysisMode'], 'insufficient_images')
        self.assertEqual(result['parts'], [])

    def test_no_detection_is_not_no_damage(self):
        data = observation()
        data['damageAnalysis']['parts'] = []
        result = server.build_analysis_response(data, {})
        self.assertEqual(result['parts'], [])
        self.assertTrue(result['requiresReview'])


class ImageAndInferenceTests(unittest.TestCase):
    def test_decode_corrupt_payload(self):
        with self.assertRaises(vision.LocalVisionError):
            vision.decode_photo(base64.b64encode(b'\x89PNG\r\n\x1a\nnot-a-real-png').decode())

    def test_dark_and_small_photo_is_not_analyzed(self):
        with patch.object(vision, 'get_session') as model:
            result = vision.analyze_local([encoded_photo(Image.new('RGB', (100, 100), 'black'))])
        model.assert_not_called()
        self.assertFalse(result['imageQuality']['usable'])
        self.assertTrue(any('escura' in issue for issue in result['imageQuality']['issues']))
        self.assertEqual(result['damageAnalysis']['parts'], [])

    def test_blur_rejected(self):
        _, issues, _ = vision.decode_photo(encoded_photo(Image.new('RGB', (640, 480), (100, 100, 100))))
        self.assertTrue(any('desfoque' in issue for issue in issues))

    def test_real_sample_quality_is_usable(self):
        photo = vision.ROOT / 'public/samples/corolla_side.jpg'
        _, issues, metrics = vision.decode_photo(base64.b64encode(photo.read_bytes()).decode())
        self.assertEqual(issues, [])
        self.assertGreater(metrics['focusVariance'], 20)

    def test_letterbox_preserves_aspect_ratio_and_normalizes(self):
        tensor, geometry = vision.letterbox(Image.new('RGB', (1280, 640), 'white'))
        self.assertEqual(tensor.shape, (1, 3, 640, 640))
        self.assertEqual(geometry, (0.5, 0, 160, 1280, 640))
        self.assertEqual(tensor.dtype, np.float32)
        self.assertAlmostEqual(float(tensor[0, 0, 0, 0]), 114/255, places=5)

    def test_nms_drops_overlapping_same_class_but_not_other_class(self):
        output = np.zeros((1, 18, 3), dtype=np.float32)
        output[0, :4, :] = np.array([[320, 320, 320], [320, 320, 320], [320, 320, 320], [160, 160, 160]])
        output[0, 4, :2] = [0.9, 0.8]
        output[0, 5, 2] = 0.85
        result = vision.parse_detections(output, (0.5, 0, 160, 1280, 640), 0.6)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['box'], [25, 25, 75, 75])
        self.assertEqual({r['classId'] for r in result}, {0, 1})

    def test_threshold_and_malformed_output(self):
        self.assertEqual(vision.parse_detections(np.zeros((1, 18, 5)), (1, 0, 0, 640, 640), 0.6), [])
        with self.assertRaises(vision.LocalVisionError):
            vision.parse_detections(np.zeros((1, 10, 5)), (1, 0, 0, 640, 640), 0.6)

    def test_detail_crop_coordinates_map_to_original_photo(self):
        model = Mock()
        model.get_inputs.return_value = [SimpleNamespace(name='images')]
        model.run.return_value = [None]
        crop_detection = {'classId': 5, 'score': .8, 'xyxy': [100, 100, 200, 200]}
        with patch.object(vision, 'parse_detections', side_effect=[[], [], [], [], [crop_detection]]):
            detections, passes = vision.detect_photo(model, Image.new('RGB', (1000, 1000)), .6, True)
        self.assertEqual(passes, 5)
        self.assertEqual(model.run.call_count, 5)
        self.assertEqual(detections[0]['box'], [40, 40, 50, 50])

    def test_crop_duplicates_and_internal_edge_fragments_are_removed(self):
        model = Mock()
        model.get_inputs.return_value = [SimpleNamespace(name='images')]
        model.run.return_value = [None]
        full = {'classId': 5, 'score': .7, 'xyxy': [400, 400, 500, 500]}
        duplicate = {'classId': 5, 'score': .8, 'xyxy': [100, 100, 200, 200]}
        fragment = {'classId': 8, 'score': .9, 'xyxy': [0, 100, 200, 200]}
        with patch.object(vision, 'parse_detections', side_effect=[[full], [], [], [], [duplicate, fragment]]):
            detections, _ = vision.detect_photo(model, Image.new('RGB', (1000, 1000)), .6, True)
        self.assertEqual(len(detections), 1)
        self.assertEqual(detections[0]['score'], .8)

    def test_small_photos_and_quick_mode_use_only_one_pass(self):
        for size, detailed in [((640, 480), True), ((1600, 1200), False)]:
            model = Mock()
            model.get_inputs.return_value = [SimpleNamespace(name='images')]
            model.run.return_value = [np.zeros((1, 18, 1))]
            self.assertEqual(vision.detect_photo(model, Image.new('RGB', size), .6, detailed), ([], 1))
            self.assertEqual(model.run.call_count, 1)

    def test_missing_or_corrupt_weights_are_errors(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(vision, '_session', None):
            path = Path(temp)/'model.onnx'
            with patch.object(vision, 'model_path', return_value=path):
                with self.assertRaises(vision.LocalVisionError) as error:
                    vision.get_session()
                self.assertEqual(error.exception.code, 'LOCAL_MODEL_MISSING')
                path.write_bytes(b'wrong weights')
                with self.assertRaises(vision.LocalVisionError) as error:
                    vision.get_session()
                self.assertEqual(error.exception.code, 'LOCAL_MODEL_INTEGRITY')

    def test_invalid_configuration(self):
        with patch.dict(vision.os.environ, {'LOCAL_CONFIDENCE': 'bad'}):
            with self.assertRaises(vision.LocalVisionError) as error:
                vision.analyze_local([])
        self.assertEqual(error.exception.code, 'LOCAL_CONFIG')

    @unittest.skipUnless(vision.model_path().exists(), 'Instale os pesos com scripts/download_model.py')
    def test_real_model_runs_with_network_blocked(self):
        photo = vision.ROOT / 'public/samples/corolla_side.jpg'
        encoded = base64.b64encode(photo.read_bytes()).decode()
        with patch('urllib.request.urlopen', side_effect=AssertionError('Network must not be used')), \
             patch('socket.create_connection', side_effect=AssertionError('Network must not be used')):
            result = vision.analyze_local([encoded])
        self.assertGreater(len(result['damageAnalysis']['parts']), 0)
        for part in result['damageAnalysis']['parts']:
            self.assertIn(part['name'], {item[0] for item in vision.LABELS})
            self.assertTrue(all(0 <= x <= 100 for x in part['box']))
        self.assertEqual(result['vehicle']['model'], '')

    @unittest.skipUnless(vision.model_path().exists(), 'Instale os pesos com scripts/download_model.py')
    def test_detail_mode_recovers_sample_lantern_without_network(self):
        photo = vision.ROOT / 'public/samples/onix_rear.jpg'
        encoded = base64.b64encode(photo.read_bytes()).decode()
        with patch.dict(vision.os.environ, {'LOCAL_CONFIDENCE': '.60'}), \
             patch('socket.create_connection', side_effect=AssertionError('Network must not be used')):
            quick = vision.analyze_local([encoded], detailed=False)
            detailed = vision.analyze_local([encoded, encoded], detailed=True)
        self.assertFalse(quick['damageAnalysis']['parts'])
        lanterns = [part for part in detailed['damageAnalysis']['parts'] if part['name'] == 'Lanterna']
        self.assertEqual(len(lanterns), 2)
        self.assertEqual({part['imageIndex'] for part in lanterns}, {0, 1})
        self.assertEqual(detailed['analysisSettings']['inferencePasses'], 10)


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

    def post(self, body, route='/api/analyze'):
        req = urllib.request.Request(self.url + route, json.dumps(body).encode(), {'Content-Type': 'application/json'})
        try:
            response = urllib.request.urlopen(req)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            return response.status, json.load(response)

    def test_image_validation(self):
        for body in [[], {'images': []}, {'images': ['not-base64']}]:
            self.assertEqual(self.post(body)[0], 400)

    def test_local_missing_model_error_is_not_fake_success(self):
        photo = vision.ROOT / 'public/samples/civic_front.jpg'
        with patch.object(server, 'analyze_local', side_effect=vision.LocalVisionError('LOCAL_MODEL_MISSING', 'Instale os pesos.')):
            status, data = self.post({'images': [base64.b64encode(photo.read_bytes()).decode()]})
        self.assertEqual(status, 503)
        self.assertFalse(data['success'])
        self.assertNotIn('parts', data)

    def test_valid_local_output(self):
        photo = vision.ROOT / 'public/samples/civic_front.jpg'
        with patch.object(server, 'analyze_local', return_value=observation()):
            status, data = self.post({'images': [base64.b64encode(photo.read_bytes()).decode()]})
        self.assertEqual(status, 200)
        self.assertEqual(data['provider'], 'local')
        self.assertEqual(data['parts'][0]['actionRequired'], 'Avaliação presencial')

    def test_analysis_mode_is_validated_and_forwarded(self):
        photo = vision.ROOT / 'public/samples/civic_front.jpg'
        encoded = base64.b64encode(photo.read_bytes()).decode()
        with patch.object(server, 'analyze_local', return_value=observation()) as analyze:
            self.assertEqual(self.post({'images': [encoded], 'detailed': 'false'})[0], 400)
            analyze.assert_not_called()
            self.assertEqual(self.post({'images': [encoded], 'detailed': False})[0], 200)
            self.assertIs(analyze.call_args.kwargs['detailed'], False)

    def test_cloud_credentials_endpoint_removed(self):
        self.assertEqual(self.post({}, '/api/set-key')[0], 404)

    def test_health_has_no_cloud_keys(self):
        with urllib.request.urlopen(self.url + '/api/health') as response:
            data = json.load(response)
        self.assertEqual(data['provider'], 'local')
        self.assertFalse(data['networkRequiredForAnalysis'])
        self.assertNotIn('providers', data)


if __name__ == '__main__':
    unittest.main()
