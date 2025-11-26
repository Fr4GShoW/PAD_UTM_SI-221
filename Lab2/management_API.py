import json
from http.server import HTTPServer, BaseHTTPRequestHandler


class ManagementAPI(BaseHTTPRequestHandler):
    def __init__(self, proxy_server, *args):
        self.proxy_server = proxy_server
        super().__init__(*args)

    def do_GET(self):
        if self.path == '/stats':
            stats = self.proxy_server.get_statistics()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress default logging
        return