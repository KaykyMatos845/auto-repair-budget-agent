import http.client
from pathlib import Path
import sys
import threading
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import monitor_proxy as proxy


class MonitorTests(unittest.TestCase):
    def test_only_explicit_read_routes_are_allowed(self):
        self.assertEqual(proxy.allowed_path('/v1.24/nodes?filters={}'), '/nodes?filters={}')
        for target in ['/containers/id/archive', '/containers/id/logs', '/events', '/exec/id/json',
                       '//example.com/nodes', 'http://example.com/nodes', '/nodes/../secrets']:
            self.assertIsNone(proxy.allowed_path(target), target)

    def test_write_methods_and_secret_routes_never_reach_docker(self):
        server = proxy.http.server.ThreadingHTTPServer(('127.0.0.1', 0), proxy.Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with patch.object(proxy, 'DockerConnection') as docker:
                for method, path in [('POST', '/services/create'), ('DELETE', '/containers/id'),
                                     ('PUT', '/nodes/id/update'), ('GET', '/secrets')]:
                    client = http.client.HTTPConnection('127.0.0.1', server.server_port)
                    client.request(method, path)
                    response = client.getresponse()
                    self.assertEqual(response.status, 403)
                    response.read()
                    client.close()
                docker.assert_not_called()
                upstream = docker.return_value
                upstream.getresponse.return_value = Mock(status=200, read=Mock(return_value=b'[]'),
                                                        getheader=Mock(return_value='application/json'))
                client = http.client.HTTPConnection('127.0.0.1', server.server_port)
                client.request('GET', '/v1.24/nodes')
                response = client.getresponse()
                self.assertEqual(response.status, 200)
                self.assertEqual(response.read(), b'[]')
                upstream.request.assert_called_once_with('GET', '/nodes', headers={'Host': 'docker'})
                client.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join()
