import socket
import threading
import time  # changed from: from datetime import time


class AdvancedLoadBalancer:
    def __init__(self, proxy_instances):
        self.proxy_instances = proxy_instances
        self.health_check_interval = 30
        self.healthy_instances = set()

    def start_health_checks(self):
        """Start periodic health checks"""

        def health_check_worker():
            while True:
                self.perform_health_checks()
                time.sleep(self.health_check_interval)

        health_thread = threading.Thread(target=health_check_worker)
        health_thread.daemon = True
        health_thread.start()

    def perform_health_checks(self):
        """Check health of all proxy instances"""
        for instance in self.proxy_instances:
            try:
                # Simple health check - attempt connection
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((instance['host'], instance['port']))
                sock.close()

                if result == 0:
                    self.healthy_instances.add(instance['id'])
                    print(f"✅ Proxy {instance['id']} is healthy")
                else:
                    self.healthy_instances.discard(instance['id'])
                    print(f"❌ Proxy {instance['id']} is unhealthy")

            except Exception as e:
                self.healthy_instances.discard(instance['id'])
                print(f"❌ Health check failed for {instance['id']}: {e}")

    def get_healthy_proxies(self):
        """Get list of healthy proxy instances"""
        return [inst for inst in self.proxy_instances
                if inst['id'] in self.healthy_instances]