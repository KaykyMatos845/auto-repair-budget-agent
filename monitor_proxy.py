"""Read-only Docker API subset for the academic Docker Visualizer dashboard."""
import http.client
import http.server
import json
import re
import socket
from urllib.parse import urlsplit

ALLOWED = {'/_ping', '/version', '/info', '/nodes', '/services', '/tasks', '/networks', '/containers/json'}


def allowed_path(target):
    parsed = urlsplit(target)
    path = re.sub(r'^/v\d+\.\d+(?=/)', '', parsed.path)
    if parsed.scheme or parsed.netloc or path not in ALLOWED:
        return None
    return path + ('?' + parsed.query if parsed.query else '')


class DockerConnection(http.client.HTTPConnection):
    def connect(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.settimeout(5)
        self.sock.connect('/host/docker.sock')


class Handler(http.server.BaseHTTPRequestHandler):
    def reply(self, status, body, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def deny(self):
        self.reply(403, b'{"error":"Read-only monitoring endpoint"}')

    do_POST = do_PUT = do_PATCH = do_DELETE = do_CONNECT = deny

    def do_GET(self):
        if self.path == '/healthz':
            self.reply(200, b'{"status":"ok"}')
            return
        path = allowed_path(self.path)
        if path is None or len(self.path) > 8192:
            self.deny()
            return
        connection = DockerConnection('docker', timeout=5)
        try:
            # Do not forward arbitrary headers, credentials, methods or URLs.
            connection.request('GET', path, headers={'Host': 'docker'})
            response = connection.getresponse()
            body = response.read(8 * 1024 * 1024 + 1)
            if len(body) > 8 * 1024 * 1024:
                raise ValueError('Monitoring response too large')
            self.reply(response.status, body, response.getheader('Content-Type', 'application/json'))
        except (OSError, ValueError, http.client.HTTPException):
            self.reply(503, b'{"error":"Docker monitoring unavailable"}')
        finally:
            connection.close()

    def log_message(self, *args):
        pass


if __name__ == '__main__':
    http.server.ThreadingHTTPServer(('0.0.0.0', 2375), Handler).serve_forever()
