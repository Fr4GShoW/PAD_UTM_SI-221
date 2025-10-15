import tkinter as tk
from tkinter import ttk, messagebox
import socket
import pickle
import json
import xml.etree.ElementTree as ET
from datetime import datetime
import random
import threading


class MessageSenderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Message Sender - TCP & UDP Broadcast")
        self.root.geometry("600x500")

        self.server_host = 'localhost'
        self.tcp_port = 9999
        self.udp_port = 8888

        self.setup_gui()

    def setup_gui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configurare grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Selector format
        ttk.Label(main_frame, text="Format mesaj:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.format_var = tk.StringVar(value="json")
        format_combo = ttk.Combobox(main_frame, textvariable=self.format_var,
                                    values=["json", "xml"], state="readonly")
        format_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5)
        format_combo.bind('<<ComboboxSelected>>', self.on_format_change)

        # Topic
        ttk.Label(main_frame, text="Topic:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.topic_var = tk.StringVar(value="general")
        topic_combo = ttk.Combobox(main_frame, textvariable=self.topic_var,
                                   values=["general", "alerts", "notifications", "updates", "errors"])
        topic_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        # Buton mesaj random
        ttk.Button(main_frame, text="🎲 Mesaj Random",
                   command=self.generate_random_message).grid(row=2, column=0, columnspan=2, pady=10)

        # Text area pentru mesaj
        ttk.Label(main_frame, text="Conținut mesaj:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.message_text = tk.Text(main_frame, height=15, width=60)
        self.message_text.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        # Scrollbar pentru text area
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.message_text.yview)
        scrollbar.grid(row=4, column=2, sticky=(tk.N, tk.S))
        self.message_text.configure(yscrollcommand=scrollbar.set)

        # Butoane trimitere
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="📨 Trimite pe TCP",
                   command=self.send_tcp_message).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="📢 Trimite pe UDP Broadcast",
                   command=self.send_udp_message).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="🚀 Trimite pe AMBELE",
                   command=self.send_both).pack(side=tk.LEFT, padx=5)

        # Status
        self.status_var = tk.StringVar(value="✅ Gata pentru trimitere")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=6, column=0, columnspan=2, pady=5)

        # Configurare weights pentru resize
        main_frame.rowconfigure(4, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Generează primul mesaj random
        self.generate_random_message()

    def on_format_change(self, event=None):
        """La schimbarea formatului, generează un mesaj random nou"""
        self.generate_random_message()

    def generate_random_message(self):
        """Generează un mesaj random în formatul selectat"""
        format_type = self.format_var.get()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if format_type == "json":
            random_data = {
                "message_id": random.randint(1000, 9999),
                "timestamp": timestamp,
                "priority": random.choice(["low", "medium", "high", "critical"]),
                "source": random.choice(["sensor_1", "sensor_2", "server", "client"]),
                "value": round(random.uniform(0, 100), 2),
                "status": random.choice(["active", "inactive", "warning", "error"]),
                "description": f"Mesaj de test generat automat la {timestamp}"
            }
            content = json.dumps(random_data, indent=2, ensure_ascii=False)

        else:  # XML - structură conformă cu schema XSD
            # Creăm un ID pentru mesaj
            message_id = str(random.randint(1000, 9999))

            # Creăm conținutul ca JSON string care va fi pus în elementul <content>
            content_data = {
                "priority": random.choice(["low", "medium", "high"]),
                "source": random.choice(["sensor_A", "sensor_B", "main_server"]),
                "value": round(random.uniform(0, 100), 2),
                "status": random.choice(["ok", "warning", "error"]),
                "description": f"Mesaj XML generat la {timestamp}"
            }

            # Creăm structura XML conform schemei XSD
            root = ET.Element("message")
            ET.SubElement(root, "id").text = message_id
            ET.SubElement(root, "topic").text = self.topic_var.get()
            ET.SubElement(root, "timestamp").text = timestamp
            ET.SubElement(root, "content").text = json.dumps(content_data)

            content = ET.tostring(root, encoding='unicode')

        # Curăță și inserează noul conținut
        self.message_text.delete(1.0, tk.END)
        self.message_text.insert(1.0, content)

    def get_message_data(self):
        """Returnează datele mesajului pentru trimitere"""
        return {
            'type': 'PUBLISH',
            'topic': self.topic_var.get(),
            'format': self.format_var.get(),
            'content': self.message_text.get(1.0, tk.END).strip(),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def send_tcp_message(self):
        """Trimite mesajul pe TCP"""
        threading.Thread(target=self._send_tcp_thread, daemon=True).start()

    def _send_tcp_thread(self):
        try:
            message_data = self.get_message_data()

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect((self.server_host, self.tcp_port))
                sock.send(pickle.dumps(message_data))
                response = sock.recv(1024)
                response_data = pickle.loads(response)

                self.status_var.set(f"✅ TCP: {response_data.get('status', 'OK')}")

        except Exception as e:
            self.status_var.set(f"❌ Eroare TCP: {str(e)}")

    def send_udp_message(self):
        """Trimite mesajul pe UDP Broadcast"""
        threading.Thread(target=self._send_udp_thread, daemon=True).start()

    def _send_udp_thread(self):
        try:
            message_data = self.get_message_data()

            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.sendto(pickle.dumps(message_data), ('<broadcast>', self.udp_port))

            self.status_var.set("✅ Mesaj UDP Broadcast trimis!")

        except Exception as e:
            self.status_var.set(f"❌ Eroare UDP: {str(e)}")

    def send_both(self):
        """Trimite mesajul pe ambele protocoale simultan"""
        self.status_var.set("🔄 Trimitere simultană...")
        threading.Thread(target=self._send_both_thread, daemon=True).start()

    def _send_both_thread(self):
        try:
            message_data = self.get_message_data()

            # TCP
            tcp_success = False
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(5)
                    sock.connect((self.server_host, self.tcp_port))
                    sock.send(pickle.dumps(message_data))
                    response = sock.recv(1024)
                    tcp_success = True
            except:
                tcp_success = False

            # UDP
            udp_success = False
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                    sock.settimeout(5)
                    sock.sendto(pickle.dumps(message_data), ('<broadcast>', self.udp_port))
                    udp_success = True
            except:
                udp_success = False

            if tcp_success and udp_success:
                self.status_var.set("✅ Trimis pe ambele protocoale!")
            elif tcp_success:
                self.status_var.set("✅ Trimis pe TCP, ❌ UDP eșuat")
            elif udp_success:
                self.status_var.set("❌ TCP eșuat, ✅ Trimis pe UDP")
            else:
                self.status_var.set("❌ Ambele trimiteri au eșuat")

        except Exception as e:
            self.status_var.set(f"❌ Eroare trimitere: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MessageSenderGUI(root)
    root.mainloop()
