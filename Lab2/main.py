import threading
import time
from http.server import HTTPServer

from backend_simulator import BackendServer
from http_proxy import DistributedProxyServer
from health_check import AdvancedLoadBalancer
from management_API import ManagementAPI


def main():
    # Start backend servers for testing
    backend_ports = [8000, 8001, 8002]
    for i, port in enumerate(backend_ports):
        backend = BackendServer(port, f"backend-{i}")
        threading.Thread(target=backend.start, daemon=True).start()

    time.sleep(0.5)  # let backends start

    # Start distributed proxy
    proxy = DistributedProxyServer(host='localhost', port=8080)
    threading.Thread(target=proxy.start, daemon=True).start()

    # Start health checks for the proxy instance(s)
    proxy_instances = [{'id': 'proxy-1', 'host': 'localhost', 'port': 8080}]
    health = AdvancedLoadBalancer(proxy_instances)
    health.health_check_interval = 10  # faster checks for testing
    health.start_health_checks()

    # Start management API and attach proxy to server instance
    management_address = ('localhost', 8081)
    httpd = HTTPServer(management_address, ManagementAPI)
    httpd.proxy_server = proxy
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    print("📊 Management API running on http://localhost:8081/stats")

    print("=" * 50)
    print("🚀 Distributed Proxy System Started!")
    print("Proxy: http://localhost:8080")
    print("Management: http://localhost:8081/stats")
    print("Backends: ports 8000, 8001, 8002")
    print("=" * 50)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")


if __name__ == "__main__":
    main()