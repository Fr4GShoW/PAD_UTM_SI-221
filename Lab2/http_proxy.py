import socket
import threading
import hashlib
import time
import pickle
from urllib.parse import urlparse
from collections import defaultdict
import http.client
import json


class DistributedProxyServer:
    def __init__(self, host='localhost', port=8080, cache_ttl=300):
        self.host = host
        self.port = port
        self.cache_ttl = cache_ttl
        self.cache = {}
        self.cache_timestamps = {}
        self.backend_servers = [
            {'host': 'localhost', 'port': 8000, 'weight': 1},
            {'host': 'localhost', 'port': 8001, 'weight': 1},
            {'host': 'localhost', 'port': 8002, 'weight': 2}
        ]
        self.server_stats = defaultdict(lambda: {'requests': 0, 'errors': 0})
        self.current_server = 0
        self.lock = threading.Lock()

    def start(self):
        """Start the proxy server with concurrent request processing"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(100)  # Handle up to 100 concurrent connections
        print(f"🚀 Distributed Proxy Server running on {self.host}:{self.port}")

        while True:
            client_socket, client_address = server_socket.accept()
            print(f"📥 Connection from {client_address}")

            # Handle each client in a separate thread
            client_thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket, client_address)
            )
            client_thread.daemon = True
            client_thread.start()

    def handle_client(self, client_socket, client_address):
        """Handle HTTP requests from clients"""
        try:
            request_data = client_socket.recv(4096).decode('utf-8')

            if not request_data:
                return

            # Parse HTTP request
            request_lines = request_data.split('\r\n')
            request_line = request_lines[0]
            method, url, version = request_line.split()

            print(f"📨 {method} {url} from {client_address}")

            # Process the request
            response = self.process_request(method, url, request_data, client_address)

            # Send response back to client
            client_socket.sendall(response)

        except Exception as e:
            print(f"❌ Error handling client {client_address}: {e}")
            error_response = self.create_error_response(500, "Internal Server Error")
            client_socket.sendall(error_response)
        finally:
            client_socket.close()

    def process_request(self, method, url, request_data, client_address):
        """Process HTTP request with caching and load balancing"""
        # Generate cache key
        cache_key = self.generate_cache_key(method, url, request_data)

        # Check cache for GET requests
        if method.upper() == 'GET':
            cached_response = self.get_cached_response(cache_key)
            if cached_response:
                print(f"💾 Serving from cache: {url}")
                return cached_response

        # Select backend server using weighted round-robin
        backend_server = self.select_backend_server()
        print(f"🔀 Routing to backend: {backend_server['host']}:{backend_server['port']}")

        try:
            # Forward request to backend server
            response = self.forward_to_backend(backend_server, request_data, url)

            # Cache successful GET responses
            if method.upper() == 'GET' and response.startswith(b'HTTP/1.1 200'):
                self.cache_response(cache_key, response)

            # Update server statistics
            self.update_server_stats(backend_server, success=True)

            return response

        except Exception as e:
            print(f"❌ Backend error: {e}")
            self.update_server_stats(backend_server, success=False)
            return self.create_error_response(502, "Bad Gateway")

    def select_backend_server(self):
        """Weighted round-robin load balancing"""
        with self.lock:
            total_weight = sum(server['weight'] for server in self.backend_servers)
            self.current_server = (self.current_server + 1) % total_weight

            current_weight = 0
            for server in self.backend_servers:
                current_weight += server['weight']
                if self.current_server < current_weight:
                    return server

    def forward_to_backend(self, backend_server, request_data, original_url):
        """Forward HTTP request to backend server"""
        # Parse the original URL to extract path
        parsed_url = urlparse(original_url)
        path = parsed_url.path or '/'

        # Create connection to backend
        conn = http.client.HTTPConnection(
            backend_server['host'],
            backend_server['port']
        )

        # Parse and reconstruct the request for backend
        lines = request_data.split('\r\n')
        request_line = lines[0]

        # Modify request line to use correct path
        method, _, version = request_line.split()
        modified_request_line = f"{method} {path} {version}"
        lines[0] = modified_request_line

        # Rebuild request
        modified_request = '\r\n'.join(lines)

        # Send request to backend
        conn.request("GET", path, body=modified_request.encode('utf-8'))
        response = conn.getresponse()

        # Read response data
        response_data = response.read()

        # Build HTTP response
        status_line = f"HTTP/1.1 {response.status} {response.reason}\r\n"
        headers = ""
        for header, value in response.getheaders():
            headers += f"{header}: {value}\r\n"

        full_response = (status_line + headers + "\r\n").encode('utf-8') + response_data
        conn.close()

        return full_response

    def generate_cache_key(self, method, url, request_data):
        """Generate unique cache key for request"""
        key_data = f"{method}:{url}:{request_data}"
        return hashlib.md5(key_data.encode()).hexdigest()

    def get_cached_response(self, cache_key):
        """Retrieve response from cache if valid"""
        if cache_key in self.cache:
            if time.time() - self.cache_timestamps[cache_key] < self.cache_ttl:
                return self.cache[cache_key]
            else:
                # Cache expired
                del self.cache[cache_key]
                del self.cache_timestamps[cache_key]
        return None

    def cache_response(self, cache_key, response):
        """Store response in cache"""
        with self.lock:
            self.cache[cache_key] = response
            self.cache_timestamps[cache_key] = time.time()

    def update_server_stats(self, server, success=True):
        """Update backend server statistics"""
        server_key = f"{server['host']}:{server['port']}"
        with self.lock:
            self.server_stats[server_key]['requests'] += 1
            if not success:
                self.server_stats[server_key]['errors'] += 1

    def create_error_response(self, status_code, message):
        """Create HTTP error response"""
        response_body = f"""
        <html>
            <head><title>{status_code} {message}</title></head>
            <body>
                <h1>{status_code} {message}</h1>
                <p>Distributed Proxy Server</p>
            </body>
        </html>
        """

        response = f"HTTP/1.1 {status_code} {message}\r\n"
        response += "Content-Type: text/html\r\n"
        response += f"Content-Length: {len(response_body)}\r\n"
        response += "Connection: close\r\n"
        response += "\r\n"
        response += response_body

        return response.encode('utf-8')

    def get_statistics(self):
        """Get proxy server statistics"""
        with self.lock:
            return {
                'cache_size': len(self.cache),
                'cache_hits': sum(1 for ts in self.cache_timestamps.values()
                                  if time.time() - ts < self.cache_ttl),
                'server_stats': dict(self.server_stats),
                'backend_servers': self.backend_servers
            }