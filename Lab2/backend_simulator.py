import socket
import time


class BackendServer:
    """Simple backend server for testing"""

    def __init__(self, port, server_id):
        self.port = port
        self.server_id = server_id

    def start(self):
        def handler(client_socket):
            request = client_socket.recv(1024).decode()

            response = f"""HTTP/1.1 200 OK
Content-Type: text/html
Connection: close

<html>
<body>
    <h1>Backend Server {self.server_id}</h1>
    <p>Port: {self.port}</p>
    <p>Time: {time.time()}</p>
</body>
</html>"""

            client_socket.sendall(response.encode())
            client_socket.close()

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('localhost', self.port))
        server_socket.listen(10)

        print(f"🔧 Backend Server {self.server_id} running on port {self.port}")

        while True:
            client_socket, addr = server_socket.accept()
            handler(client_socket)