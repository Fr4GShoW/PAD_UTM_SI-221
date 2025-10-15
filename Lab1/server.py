import socket
import threading
import json
import xml.etree.ElementTree as ET
from lxml import etree
import pickle
from collections import defaultdict
from queue import Queue
import hashlib
from datetime import datetime
import jsonschema
import os
import sys


# =============================================
# Creare automată a fișierelor de schemă
# =============================================
def create_schema_files():
    """Creează fișierele de schemă dacă nu există"""

    # Schema XSD
    xsd_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
    <xs:element name="message">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="id" type="xs:string"/>
                <xs:element name="topic" type="xs:string"/>
                <xs:element name="timestamp" type="xs:string"/>
                <xs:element name="content" type="xs:string"/>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
</xs:schema>'''

    # Schema JSON
    json_schema_content = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "message_id": {"type": "integer"},
            "timestamp": {"type": "string"},
            "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
            "source": {"type": "string"},
            "value": {"type": "number"},
            "status": {"type": "string", "enum": ["active", "inactive", "warning", "error"]},
            "description": {"type": "string"}
        },
        "required": ["message_id", "timestamp", "priority", "source", "status", "description"]
    }

    # Creează fișierele
    files_created = []

    try:
        with open('schema.xsd', 'w', encoding='utf-8') as f:
            f.write(xsd_content)
        files_created.append('schema.xsd')
        print("✅ Fișierul schema.xsd a fost creat automat")
    except Exception as e:
        print(f"❌ Eroare creare schema.xsd: {e}")

    try:
        with open('schema.json', 'w', encoding='utf-8') as f:
            json.dump(json_schema_content, f, indent=2)
        files_created.append('schema.json')
        print("✅ Fișierul schema.json a fost creat automat")
    except Exception as e:
        print(f"❌ Eroare creare schema.json: {e}")

    return files_created


# Verifică și creează fișierele de schemă la pornire
print("🔍 Verific fișierele de schemă...")
schema_files = create_schema_files()


# =============================================
# Agent de Mesaje (Message Broker)
# =============================================
class MessageBroker:
    def __init__(self):
        self.queues = defaultdict(Queue)
        self.subscribers = defaultdict(list)
        self.message_store = []
        self.routing_table = {}
        self._initialize_storage()

    def _initialize_storage(self):
        """Inițializează fișierele de stocare"""
        try:
            # JSON storage
            with open('messages.json', 'w', encoding='utf-8') as f:
                json.dump([], f, indent=2)

            # XML storage
            with open('messages.xml', 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n<messages>\n</messages>')

            print("✅ Fișierele de stocare au fost inițializate")
        except Exception as e:
            print(f"❌ Eroare inițializare stocare: {e}")

    def add_message(self, topic, message):
        """Stochează mesajul și îl pune în coada corespunzătoare"""
        msg_id = hashlib.sha256(pickle.dumps(message)).hexdigest()[:16]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        stored_msg = {
            'id': msg_id,
            'topic': topic,
            'format': message.get('format', 'text'),
            'content': message['content'],
            'timestamp': timestamp
        }

        self.message_store.append(stored_msg)
        self.queues[topic].put(stored_msg)

        # Salvare în format corespunzător
        if message.get('format') == 'json':
            self._save_json_message(stored_msg)
        elif message.get('format') == 'xml':
            self._save_xml_message(stored_msg)
        else:
            self._save_text_message(stored_msg)

        # Trimite mesajul tuturor subscriberilor
        for subscriber in self.subscribers[topic]:
            try:
                subscriber.send_message(stored_msg)
            except:
                self.subscribers[topic].remove(subscriber)

    def _save_json_message(self, message):
        """Salvează mesajul JSON în fișier"""
        try:
            with open('messages.json', 'r+', encoding='utf-8') as f:
                try:
                    messages = json.load(f)
                except json.JSONDecodeError:
                    messages = []

                # Încercăm să parsăm conținutul ca JSON
                try:
                    content_parsed = json.loads(message['content'])
                except:
                    content_parsed = message['content']

                messages.append({
                    'id': message['id'],
                    'topic': message['topic'],
                    'timestamp': message['timestamp'],
                    'content': content_parsed
                })

                f.seek(0)
                json.dump(messages, f, indent=2, ensure_ascii=False)
                f.truncate()
        except Exception as e:
            print(f"Eroare salvare JSON: {e}")

    def _save_xml_message(self, message):
        """Salvează mesajul XML în fișier"""
        try:
            # Verificăm dacă fișierul există și are conținut valid
            if os.path.exists('messages.xml') and os.path.getsize('messages.xml') > 0:
                try:
                    tree = ET.parse('messages.xml')
                    root = tree.getroot()
                except ET.ParseError:
                    # Dacă fișierul este corupt, creăm unul nou
                    root = ET.Element("messages")
                    tree = ET.ElementTree(root)
            else:
                root = ET.Element("messages")
                tree = ET.ElementTree(root)

            # Creăm elementul message conform schemei XSD
            msg_element = ET.Element("message")

            ET.SubElement(msg_element, "id").text = message['id']
            ET.SubElement(msg_element, "topic").text = message['topic']
            ET.SubElement(msg_element, "timestamp").text = message['timestamp']

            content_elem = ET.SubElement(msg_element, "content")
            content_elem.text = message['content']

            root.append(msg_element)

            # Scriem înapoi în fișier
            with open('messages.xml', 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write(ET.tostring(root, encoding='unicode'))

        except Exception as e:
            print(f"Eroare salvare XML: {e}")

    def _save_text_message(self, message):
        """Salvează mesajul text în fișier"""
        try:
            with open('messages.txt', 'a', encoding='utf-8') as f:
                f.write(f"[{message['timestamp']}] {message['topic']}: {message['content']}\n")
        except Exception as e:
            print(f"Eroare salvare text: {e}")

    def add_subscriber(self, topic, subscriber):
        """Înregistrează un subscriber la un topic"""
        self.subscribers[topic].append(subscriber)

    def add_route(self, topic, target):
        """Adaugă o rută pentru un topic"""
        self.routing_table[topic] = target


# =============================================
# Validatori XML și JSON
# =============================================
class XMLValidator:
    def __init__(self, xsd_path):
        self.schema = None
        try:
            with open(xsd_path, 'r') as f:
                schema_root = etree.XML(f.read())
            self.schema = etree.XMLSchema(schema_root)
            print("✅ Schema XSD încărcată cu succes!")
        except Exception as e:
            print(f"❌ Eroare încărcare schema XSD: {e}")

    def validate(self, xml_string):
        if not self.schema:
            print("⚠️  Fără schema XSD, se acceptă orice XML")
            return True

        try:
            root = etree.fromstring(xml_string)
            self.schema.validate(root)
            print("✅ Validare XSD: Mesaj XML valid")
            return True
        except etree.XMLSyntaxError as e:
            print(f"❌ Eroare parsare XML: {e}")
            return False
        except Exception as e:
            print(f"❌ Eroare validare: {e}")
            return False


class JSONValidator:
    def __init__(self, schema_path):
        self.schema = None

        print(f"\n🔍 JSONValidator initialization:")
        print(f"   JSON Schema path: {schema_path}")
        print(f"   File exists: {os.path.exists(schema_path)}")

        if not os.path.exists(schema_path):
            print(f"❌ JSON Schema file not found: {schema_path}")
            return

        try:
            with open(schema_path, 'r') as f:
                self.schema = json.load(f)
            print("✅ JSON Schema loaded successfully!")
        except Exception as e:
            print(f"❌ Error loading JSON schema: {e}")

    def validate(self, json_string):
        if not self.schema:
            print("⚠️  JSON VALIDATION: No JSON schema, accepting any JSON")
            return True

        try:
            data = json.loads(json_string)
            jsonschema.validate(instance=data, schema=self.schema)
            print("✅ JSON validation: Valid JSON message")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            return False
        except jsonschema.ValidationError as e:
            print(f"❌ JSON validation error: {e}")
            return False
        except Exception as e:
            print(f"❌ JSON validation error: {e}")
            return False


# =============================================
# Handler pentru Conexiuni TCP
# =============================================
class ClientHandler(threading.Thread):
    def __init__(self, client_socket, broker, xml_validator, json_validator):
        super().__init__()
        self.socket = client_socket
        self.broker = broker
        self.xml_validator = xml_validator
        self.json_validator = json_validator

    def run(self):
        while True:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break

                message = pickle.loads(data)
                self.process_message(message)
            except (EOFError, ConnectionResetError, socket.error):
                break

    def process_message(self, message):
        msg_type = message.get('type')
        topic = message.get('topic')
        content = message.get('content')
        format_type = message.get('format', 'text')

        print(f"📨 Processing message: type={msg_type}, topic={topic}, format={format_type}")

        if msg_type == 'PUBLISH':
            # Validare în funcție de format
            validation_passed = True
            error_msg = ''

            if format_type == 'xml':
                print("🔍 Validating XML...")
                if not self.xml_validator.validate(content):
                    validation_passed = False
                    error_msg = 'XML invalid according to XSD schema'
            elif format_type == 'json':
                print("🔍 Validating JSON...")
                if not self.json_validator.validate(content):
                    validation_passed = False
                    error_msg = 'JSON invalid according to JSON schema'

            if not validation_passed:
                print(f"❌ Message rejected: {error_msg}")
                self.socket.send(pickle.dumps({
                    'status': 'ERROR',
                    'message': error_msg
                }))
                return

            self.broker.add_message(topic, message)
            self.socket.send(pickle.dumps({'status': 'OK'}))
            print("✅ Message processed and saved successfully")

        elif msg_type == 'SUBSCRIBE':
            self.broker.add_subscriber(topic, self)
            self.socket.send(pickle.dumps({'status': 'SUBSCRIBED'}))

    def send_message(self, message):
        try:
            self.socket.send(pickle.dumps(message))
        except:
            pass


# =============================================
# Server TCP cu Suport pentru UDP Broadcast
# =============================================
class NetworkServer:
    def __init__(self, host='localhost', tcp_port=9999, udp_port=8888):
        print("\n" + "=" * 50)
        print("🚀 Starting server...")
        print("=" * 50)

        self.broker = MessageBroker()
        self.xml_validator = XMLValidator('schema.xsd')
        self.json_validator = JSONValidator('schema.json')
        self.tcp_port = tcp_port
        self.udp_port = udp_port
        self.host = host

    def start_tcp_server(self):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((self.host, self.tcp_port))
            server.listen(5)
            print(f"🚀 TCP Server started on {self.host}:{self.tcp_port}")

            while True:
                try:
                    client_socket, addr = server.accept()
                    print(f"📡 TCP Client connected: {addr}")
                    handler = ClientHandler(client_socket, self.broker, self.xml_validator, self.json_validator)
                    handler.start()
                except Exception as e:
                    print(f"Error accepting TCP client: {e}")
        except Exception as e:
            print(f"❌ Error starting TCP server: {e}")

    def start_udp_broadcast_server(self):
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind(('', self.udp_port))
            print(f"📢 UDP Broadcast Server started on port {self.udp_port}")

            while True:
                try:
                    data, addr = server.recvfrom(4096)
                    message = pickle.loads(data)
                    topic = message.get('topic')
                    content = message.get('content')
                    format_type = message.get('format', 'text')

                    print(f"📨 UDP message received from {addr}: topic={topic}, format={format_type}")

                    # Validare în funcție de format
                    validation_passed = True
                    if format_type == 'xml':
                        if not self.xml_validator.validate(content):
                            validation_passed = False
                            print("❌ Invalid XML message rejected")
                    elif format_type == 'json':
                        if not self.json_validator.validate(content):
                            validation_passed = False
                            print("❌ Invalid JSON message rejected")

                    if validation_passed:
                        self.broker.add_message(topic, message)
                        print("✅ Valid UDP message processed")
                    else:
                        print("❌ UDP message rejected - validation failed")

                except Exception as e:
                    print(f"Error processing UDP: {e}")
        except Exception as e:
            print(f"❌ Error starting UDP server: {e}")

    def start_servers(self):
        tcp_thread = threading.Thread(target=self.start_tcp_server)
        udp_thread = threading.Thread(target=self.start_udp_broadcast_server)

        tcp_thread.daemon = True
        udp_thread.daemon = True

        tcp_thread.start()
        udp_thread.start()

        print("\n" + "=" * 50)
        print("✅ All servers are running and functional!")
        print("📁 Messages are saved in: messages.json, messages.xml, messages.txt")
        print("\n🔍 VALIDATION STATUS:")
        print(f"   XML:  {'✅ Active' if self.xml_validator.schema else '❌ Inactive'}")
        print(f"   JSON: {'✅ Active' if self.json_validator.schema else '❌ Inactive'}")
        print("=" * 50)

        if not self.xml_validator.schema:
            print("\n🚨 WARNING: XSD validation is inactive!")
            print("   Make sure 'schema.xsd' file exists in the same folder as server.py")

        # Menține thread-ul principal activ
        try:
            while True:
                threading.Event().wait(1)
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")


if __name__ == "__main__":
    server = NetworkServer()
    server.start_servers()