import socket
import threading
import pickle
import json
import xml.etree.ElementTree as ET
from datetime import datetime


class MessageListener:
    def __init__(self, host='localhost', tcp_port=9999, udp_port=8888):
        self.host = host
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.running = True

    def start_tcp_listener(self):
        """Ascultă mesaje TCP de la server"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.host, self.tcp_port))

            # Subscribe to all topics
            sock.send(pickle.dumps({
                'type': 'SUBSCRIBE',
                'topic': 'all'
            }))

            print(f"👂 Listener TCP pornit pe {self.host}:{self.tcp_port}")

            while self.running:
                try:
                    data = sock.recv(4096)
                    if data:
                        message = pickle.loads(data)
                        self.display_message(message, "TCP")
                except (EOFError, ConnectionResetError):
                    break

        except Exception as e:
            print(f"❌ Eroare listener TCP: {e}")

    def start_udp_broadcast_listener(self):
        """Ascultă mesaje UDP broadcast"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.bind(('', self.udp_port))

            print(f"📡 Listener UDP Broadcast pornit pe portul {self.udp_port}")

            while self.running:
                try:
                    data, addr = sock.recvfrom(4096)
                    if data:
                        message = pickle.loads(data)
                        self.display_message(message, "UDP Broadcast")
                except Exception as e:
                    print(f"Eroare recepție UDP: {e}")

        except Exception as e:
            print(f"❌ Eroare listener UDP: {e}")

    def display_message(self, message, protocol):
        """Afișează mesajul primit"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n{'=' * 50}")
        print(f"📨 [{timestamp}] Mesaj primit via {protocol}")
        print(f"📝 Topic: {message.get('topic', 'N/A')}")
        print(f"📋 Format: {message.get('format', 'text')}")
        print(f"⏰ Timestamp: {message.get('timestamp', 'N/A')}")
        print(f"📄 Content:")

        if message.get('format') == 'json':
            try:
                content = json.loads(message['content'])
                print(json.dumps(content, indent=2, ensure_ascii=False))
            except:
                print(message['content'])
        elif message.get('format') == 'xml':
            try:
                root = ET.fromstring(message['content'])
                print(ET.tostring(root, encoding='unicode'))
            except:
                print(message['content'])
        else:
            print(message.get('content', 'N/A'))

        print(f"{'=' * 50}")

    def start_listening(self):
        """Pornește ambele listener-e"""
        tcp_thread = threading.Thread(target=self.start_tcp_listener)
        udp_thread = threading.Thread(target=self.start_udp_broadcast_listener)

        tcp_thread.daemon = True
        udp_thread.daemon = True

        tcp_thread.start()
        udp_thread.start()

        print("✅ Listener-e pornite! Aștept mesaje...")
        print("👉 Apasă Ctrl+C pentru a opri")

        try:
            while True:
                threading.Event().wait(1)
        except KeyboardInterrupt:
            self.running = False
            print("\n🛑 Listener-e oprite")


if __name__ == "__main__":
    listener = MessageListener()
    listener.start_listening()
