# app.py - VERSIUNEA COMPLETĂ
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import json
import time
import random
from datetime import datetime
from queue import Queue
import io

app = Flask(__name__)
app.secret_key = 'cloud-simulator-secret-key-2025'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = {'json', 'txt', 'py', 'yaml', 'yml'}

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# ==================== TOATE CLASELE CLOUD ====================

class CloudDatabase:
    """Serviciu Database cu TOATE operațiile"""

    def __init__(self, name: str, db_type: str = "PostgreSQL"):
        self.name = name
        self.db_type = db_type
        self.data = {}
        self.transactions = []
        self.connected = True
        self.connection_string = f"localhost:5432/{name}"

    def insert(self, table: str, key: str, value: any):
        if table not in self.data:
            self.data[table] = {}
        self.data[table][key] = value
        self.transactions.append({
            "op": "INSERT", "table": table, "key": key,
            "time": datetime.now().strftime("%H:%M:%S")
        })
        return True

    def select(self, table: str, key: str = None):
        if key:
            return self.data.get(table, {}).get(key)
        return self.data.get(table, {})

    def update(self, table: str, key: str, value: any):
        if table in self.data and key in self.data[table]:
            self.data[table][key] = value
            self.transactions.append({
                "op": "UPDATE", "table": table, "key": key,
                "time": datetime.now().strftime("%H:%M:%S")
            })
            return True
        return False

    def delete(self, table: str, key: str):
        if table in self.data and key in self.data[table]:
            del self.data[table][key]
            self.transactions.append({
                "op": "DELETE", "table": table, "key": key,
                "time": datetime.now().strftime("%H:%M:%S")
            })
            return True
        return False

    def migrate_from_json(self, json_file_path: str):
        """Migrare date din JSON"""
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            migrated_records = 0
            for table, records in data.items():
                if isinstance(records, dict):
                    for key, value in records.items():
                        self.insert(table, key, value)
                        migrated_records += 1

            return {"success": True, "records": migrated_records}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def export_to_json(self):
        """Export date către JSON"""
        return json.dumps(self.data, indent=2)

    def get_stats(self):
        return {
            "name": self.name,
            "type": self.db_type,
            "connection": self.connection_string,
            "status": "connected" if self.connected else "disconnected",
            "tables": list(self.data.keys()),
            "total_records": sum(len(t) for t in self.data.values()),
            "total_transactions": len(self.transactions),
            "transactions": self.transactions[-15:]
        }


class CloudCache:
    """Serviciu Cache cu TTL și operații avansate"""

    def __init__(self, name: str):
        self.name = name
        self.cache = {}
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    def set(self, key: str, value: any, ttl: int = 300):
        self.cache[key] = {
            "value": value,
            "expires": time.time() + ttl,
            "ttl": ttl,
            "created": datetime.now().strftime("%H:%M:%S")
        }
        return True

    def get(self, key: str):
        if key in self.cache:
            if time.time() < self.cache[key]["expires"]:
                self.hits += 1
                return self.cache[key]["value"]
            else:
                del self.cache[key]
                self.evictions += 1
        self.misses += 1
        return None

    def delete(self, key: str):
        if key in self.cache:
            del self.cache[key]
            return True
        return False

    def flush_all(self):
        """Șterge TOATE datele din cache"""
        count = len(self.cache)
        self.cache = {}
        return count

    def get_ttl(self, key: str):
        """Returnează timpul rămas până la expirare"""
        if key in self.cache:
            remaining = self.cache[key]["expires"] - time.time()
            return max(0, int(remaining))
        return None

    def get_all_keys(self):
        expired = [k for k, v in self.cache.items() if time.time() >= v["expires"]]
        for k in expired:
            del self.cache[k]
            self.evictions += 1
        return list(self.cache.keys())

    def get_stats(self):
        total = self.hits + self.misses
        return {
            "name": self.name,
            "entries": len(self.cache),
            "keys": self.get_all_keys(),
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "hit_rate": f"{(self.hits / total * 100) if total > 0 else 0:.1f}%",
            "memory_usage": f"{len(json.dumps(self.cache)) / 1024:.2f} KB"
        }


class MessageBroker:
    """Message Broker complet funcțional"""

    def __init__(self, name: str):
        self.name = name
        self.queues = {}
        self.messages_sent = 0
        self.messages_received = 0
        self.dead_letter_queue = Queue()
        self.history = []

    def create_queue(self, queue_name: str):
        if queue_name not in self.queues:
            self.queues[queue_name] = Queue()
            self.history.append({
                "action": "CREATE_QUEUE",
                "queue": queue_name,
                "time": datetime.now().strftime("%H:%M:%S")
            })
            return True
        return False

    def delete_queue(self, queue_name: str):
        if queue_name in self.queues:
            del self.queues[queue_name]
            self.history.append({
                "action": "DELETE_QUEUE",
                "queue": queue_name,
                "time": datetime.now().strftime("%H:%M:%S")
            })
            return True
        return False

    def publish(self, queue_name: str, message: str, priority: int = 0):
        if queue_name not in self.queues:
            self.create_queue(queue_name)

        msg_obj = {
            "content": message,
            "priority": priority,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

        self.queues[queue_name].put(msg_obj)
        self.messages_sent += 1
        self.history.append({
            "action": "PUBLISH",
            "queue": queue_name,
            "message": message,
            "time": datetime.now().strftime("%H:%M:%S")
        })
        return True

    def consume(self, queue_name: str):
        if queue_name in self.queues and not self.queues[queue_name].empty():
            msg = self.queues[queue_name].get()
            self.messages_received += 1
            self.history.append({
                "action": "CONSUME",
                "queue": queue_name,
                "message": str(msg["content"])[:50],
                "time": datetime.now().strftime("%H:%M:%S")
            })
            return msg["content"]
        return None

    def get_queue_size(self, queue_name: str):
        if queue_name in self.queues:
            return self.queues[queue_name].qsize()
        return 0

    def purge_queue(self, queue_name: str):
        """Șterge toate mesajele dintr-un queue"""
        if queue_name in self.queues:
            count = self.queues[queue_name].qsize()
            self.queues[queue_name] = Queue()
            return count
        return 0

    def get_stats(self):
        return {
            "name": self.name,
            "queues": list(self.queues.keys()),
            "queue_count": len(self.queues),
            "queue_sizes": {q: self.get_queue_size(q) for q in self.queues},
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "messages_pending": sum(self.get_queue_size(q) for q in self.queues),
            "history": self.history[-20:]
        }


class InfrastructureAsCode:
    """IaC Manager complet cu validare"""

    def __init__(self):
        self.infrastructure = {
            "compute_instances": [],
            "databases": [],
            "cache_services": [],
            "message_brokers": [],
            "load_balancers": [],
            "storage": []
        }
        self.logs = []
        self.provision_count = 0

    def provision_from_config(self, config: dict):
        self.logs = []
        self.provision_count += 1
        start_time = time.time()

        self.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Începe provizionarea #{self.provision_count}")

        # Reset infrastructure
        self.infrastructure = {
            "compute_instances": [], "databases": [],
            "cache_services": [], "message_brokers": [],
            "load_balancers": [], "storage": []
        }

        # Provizionare Compute Instances
        for instance in config.get("compute_instances", []):
            inst = {
                "id": f"vm-{len(self.infrastructure['compute_instances']) + 1}",
                "name": instance["name"],
                "cpu": instance.get("cpu", 2),
                "ram": instance.get("ram", 4),
                "os": instance.get("os", "Ubuntu 22.04"),
                "status": "running",
                "ip": f"10.0.0.{len(self.infrastructure['compute_instances']) + 10}"
            }
            self.infrastructure["compute_instances"].append(inst)
            self.logs.append(f"✓ VM: {inst['name']} ({inst['cpu']}vCPU, {inst['ram']}GB RAM) - {inst['ip']}")

        # Provizionare Databases
        for db in config.get("databases", []):
            database = {
                "id": f"db-{len(self.infrastructure['databases']) + 1}",
                "name": db["name"],
                "type": db.get("type", "PostgreSQL"),
                "storage": db.get("storage", 10),
                "version": db.get("version", "14.0"),
                "status": "active"
            }
            self.infrastructure["databases"].append(database)
            self.logs.append(
                f"✓ DB: {database['name']} ({database['type']} v{database['version']}, {database['storage']}GB)")

        # Provizionare Cache
        for cache in config.get("cache_services", []):
            c = {
                "id": f"cache-{len(self.infrastructure['cache_services']) + 1}",
                "name": cache["name"],
                "type": cache.get("type", "Redis"),
                "memory": cache.get("memory", 1),
                "version": cache.get("version", "7.0")
            }
            self.infrastructure["cache_services"].append(c)
            self.logs.append(f"✓ Cache: {c['name']} ({c['type']} v{c['version']}, {c['memory']}GB)")

        # Provizionare Message Brokers
        for broker in config.get("message_brokers", []):
            b = {
                "id": f"mq-{len(self.infrastructure['message_brokers']) + 1}",
                "name": broker["name"],
                "type": broker.get("type", "RabbitMQ"),
                "version": broker.get("version", "3.11")
            }
            self.infrastructure["message_brokers"].append(b)
            self.logs.append(f"✓ MQ: {b['name']} ({b['type']} v{b['version']})")

        # Provizionare Load Balancers
        for lb in config.get("load_balancers", []):
            load_balancer = {
                "id": f"lb-{len(self.infrastructure['load_balancers']) + 1}",
                "name": lb["name"],
                "type": lb.get("type", "Application LB"),
                "algorithm": lb.get("algorithm", "Round Robin")
            }
            self.infrastructure["load_balancers"].append(load_balancer)
            self.logs.append(f"✓ LB: {load_balancer['name']} ({load_balancer['algorithm']})")

        # Provizionare Storage
        for storage in config.get("storage", []):
            stor = {
                "id": f"stor-{len(self.infrastructure['storage']) + 1}",
                "name": storage["name"],
                "type": storage.get("type", "Block Storage"),
                "size": storage.get("size", 100)
            }
            self.infrastructure["storage"].append(stor)
            self.logs.append(f"✓ Storage: {stor['name']} ({stor['type']}, {stor['size']}GB)")

        duration = time.time() - start_time
        self.logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] Provizionare completă în {duration:.2f}s")

        return self.infrastructure

    def get_total_resources(self):
        return {
            "compute": len(self.infrastructure["compute_instances"]),
            "databases": len(self.infrastructure["databases"]),
            "caches": len(self.infrastructure["cache_services"]),
            "brokers": len(self.infrastructure["message_brokers"]),
            "load_balancers": len(self.infrastructure["load_balancers"]),
            "storage": len(self.infrastructure["storage"])
        }


class CICDPipeline:
    """Pipeline CI/CD complet"""

    def __init__(self):
        self.builds = []
        self.status = "idle"
        self.failed_builds = 0
        self.successful_builds = 0

    def run_pipeline(self, code_content: str, branch: str = "main"):
        build_number = len(self.builds) + 1
        build = {
            "id": f"build-{build_number}",
            "number": build_number,
            "branch": branch,
            "time": datetime.now().strftime("%H:%M:%S"),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "stages": [],
            "duration": 0
        }

        start_time = time.time()

        # Stage 1: Build
        build["stages"].append({
            "name": "Build",
            "status": "success",
            "duration": "1.2s",
            "logs": [
                "✓ Cloning repository...",
                "✓ Installing dependencies...",
                "✓ Compiling code...",
                f"✓ Artifact created: app-{build_number}.tar.gz"
            ]
        })

        # Stage 2: Test - VERIFICARE MAI INTELIGENTĂ
        # Verifică doar pentru erori de sintaxă evidente
        test_success = True

        # Verifică erori de sintaxă Python
        try:
            compile(code_content, '<string>', 'exec')
            syntax_ok = True
        except SyntaxError:
            syntax_ok = False
            test_success = False

        # Verifică doar dacă este prea scurt (probabil gol)
        if len(code_content) < 10:
            test_success = False

        # Verifică dacă există funcția main sau clase definite
        has_main = "def main" in code_content or "class " in code_content
        if not has_main:
            test_success = False

        build["stages"].append({
            "name": "Test",
            "status": "success" if test_success else "failed",
            "duration": "2.5s",
            "logs": [
                "✓ test_unit_database - PASSED",
                "✓ test_unit_cache - PASSED",
                "✓ test_integration - PASSED",
                f"✓ Code coverage: {random.randint(75, 95)}%",
                "✓ All tests passed successfully!"
            ] if test_success else [
                "✗ test_unit_database - FAILED",
                "✗ Syntax error detected" if not syntax_ok else "✗ Code validation failed",
                "✗ Build aborted"
            ]
        })

        # Stage 3: Security Scan
        if test_success:
            build["stages"].append({
                "name": "Security",
                "status": "success",
                "duration": "1.5s",
                "logs": [
                    "✓ Vulnerability scan completed",
                    "✓ No critical issues found",
                    "✓ Dependencies up to date"
                ]
            })

        # Stage 4: Deploy
        # Stage 4: Deploy
        if test_success:
            deploy_url = f"http://localhost:5000/app-{build_number}"

            build["stages"].append({
                "name": "Deploy",
                "status": "success",
                "duration": "1.8s",
                "logs": [
                    "✓ Deploying to localhost:5000",
                    "✓ Health check passed",
                    f"✓ Application deployed at {deploy_url}",
                    "✓ Application is live!"
                ]
            })
            build["overall_status"] = "success"
            build["deploy_url"] = deploy_url
            build["deployed_at"] = datetime.now().isoformat()
            self.successful_builds += 1
        else:
            build["overall_status"] = "failed"
            self.failed_builds += 1

        build["duration"] = f"{time.time() - start_time:.2f}s"

        self.builds.append(build)
        self.status = build["overall_status"]

        return build

    def get_stats(self):
        return {
            "total_builds": len(self.builds),
            "successful": self.successful_builds,
            "failed": self.failed_builds,
            "success_rate": f"{(self.successful_builds / len(self.builds) * 100) if self.builds else 0:.1f}%",
            "last_status": self.status
        }


class MonitoringService:
    """Serviciu de monitoring și logs"""

    def __init__(self):
        self.logs = []
        self.metrics = {
            "cpu_usage": [],
            "memory_usage": [],
            "requests": 0,
            "errors": 0
        }

    def log(self, level: str, message: str):
        entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "level": level,
            "message": message
        }
        self.logs.append(entry)
        if len(self.logs) > 100:
            self.logs.pop(0)

    def record_metric(self, metric_type: str, value: float):
        if metric_type in self.metrics:
            if isinstance(self.metrics[metric_type], list):
                self.metrics[metric_type].append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "value": value
                })
                if len(self.metrics[metric_type]) > 50:
                    self.metrics[metric_type].pop(0)

    def get_logs(self, limit: int = 50):
        return self.logs[-limit:]

    def get_metrics(self):
        # Simulează metrici în timp real
        self.record_metric("cpu_usage", random.uniform(20, 80))
        self.record_metric("memory_usage", random.uniform(30, 70))

        return {
            "cpu": self.metrics["cpu_usage"][-10:] if self.metrics["cpu_usage"] else [],
            "memory": self.metrics["memory_usage"][-10:] if self.metrics["memory_usage"] else [],
            "requests": self.metrics["requests"],
            "errors": self.metrics["errors"],
            "uptime": "99.9%"
        }


# ==================== INSTANȚE GLOBALE ====================
iac = InfrastructureAsCode()
database = CloudDatabase("primary-db", "PostgreSQL")
cache = CloudCache("redis-cache")
broker = MessageBroker("rabbitmq")
pipeline = CICDPipeline()
monitoring = MonitoringService()

# Init demo data
broker.create_queue("orders")
broker.create_queue("notifications")
broker.create_queue("analytics")

monitoring.log("INFO", "Cloud Provider Simulator started")
monitoring.log("SUCCESS", "All services initialized")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


# ==================== ROUTES ====================

@app.route('/')
def index():
    monitoring.metrics["requests"] += 1
    stats = {
        "infrastructure": iac.infrastructure,
        "resources": iac.get_total_resources(),
        "database": database.get_stats(),
        "cache": cache.get_stats(),
        "broker": broker.get_stats(),
        "pipeline": pipeline.get_stats(),
        "monitoring": monitoring.get_metrics()
    }
    return render_template('index.html', stats=stats)


@app.route('/infrastructure', methods=['GET', 'POST'])
def infrastructure():
    if request.method == 'POST':
        if 'config_file' not in request.files:
            flash('Selectează un fișier de configurație!', 'danger')
            return redirect(request.url)

        file = request.files['config_file']
        if file.filename == '':
            flash('Niciun fișier selectat!', 'danger')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                iac.provision_from_config(config)
                monitoring.log("SUCCESS", f"Infrastructure provisioned from {filename}")
                flash(f'✓ Infrastructură provizionată cu succes din {filename}!', 'success')
            except json.JSONDecodeError:
                monitoring.log("ERROR", "Invalid JSON configuration file")
                flash('Eroare: Fișierul JSON este invalid!', 'danger')
            except Exception as e:
                monitoring.log("ERROR", f"Provisioning failed: {str(e)}")
                flash(f'Eroare: {str(e)}', 'danger')

            return redirect(url_for('infrastructure'))

    return render_template('infrastructure.html',
                           infra=iac.infrastructure,
                           resources=iac.get_total_resources(),
                           logs=iac.logs)


@app.route('/database', methods=['GET', 'POST'])
def database_page():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'insert':
            table = request.form.get('table')
            key = request.form.get('key')
            value = request.form.get('value')
            database.insert(table, key, value)
            monitoring.log("INFO", f"INSERT into {table}: {key}")
            flash(f'✓ Record inserat în {table}', 'success')

        elif action == 'update':
            table = request.form.get('table')
            key = request.form.get('key')
            value = request.form.get('value')
            if database.update(table, key, value):
                monitoring.log("INFO", f"UPDATE in {table}: {key}")
                flash(f'✓ Record actualizat în {table}', 'success')
            else:
                flash('Record inexistent!', 'warning')

        elif action == 'delete':
            table = request.form.get('table')
            key = request.form.get('key')
            if database.delete(table, key):
                monitoring.log("INFO", f"DELETE from {table}: {key}")
                flash(f'✓ Record șters din {table}', 'success')
            else:
                flash('Record inexistent!', 'warning')

        elif action == 'migrate':
            if 'data_file' in request.files:
                file = request.files['data_file']
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)

                    result = database.migrate_from_json(filepath)
                    if result["success"]:
                        monitoring.log("SUCCESS", f"Migrated {result['records']} records")
                        flash(f'✓ Migrare completă: {result["records"]} records', 'success')
                    else:
                        flash(f'Eroare migrare: {result["error"]}', 'danger')

        return redirect(url_for('database_page'))

    return render_template('database.html',
                           stats=database.get_stats(),
                           data=database.data)


@app.route('/database/export')
def database_export():
    """Export database to JSON"""
    json_data = database.export_to_json()
    monitoring.log("INFO", "Database exported to JSON")

    return send_file(
        io.BytesIO(json_data.encode()),
        mimetype='application/json',
        as_attachment=True,
        download_name=f'database_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    )


@app.route('/cache', methods=['GET', 'POST'])
def cache_page():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'set':
            key = request.form.get('key')
            value = request.form.get('value')
            ttl = int(request.form.get('ttl', 300))
            cache.set(key, value, ttl)
            monitoring.log("INFO", f"Cache SET: {key} (TTL: {ttl}s)")
            flash(f'✓ Cache SET: {key} (TTL: {ttl}s)', 'success')

        elif action == 'get':
            key = request.form.get('key')
            value = cache.get(key)
            if value:
                monitoring.log("INFO", f"Cache HIT: {key}")
                flash(f'✓ HIT: {key} = {value}', 'success')
            else:
                monitoring.log("WARNING", f"Cache MISS: {key}")
                flash(f'✗ MISS: {key}', 'warning')

        elif action == 'delete':
            key = request.form.get('key')
            if cache.delete(key):
                monitoring.log("INFO", f"Cache DELETE: {key}")
                flash(f'✓ Cheie ștearsă: {key}', 'success')

        elif action == 'flush':
            count = cache.flush_all()
            monitoring.log("WARNING", f"Cache FLUSH ALL: {count} keys")
            flash(f'✓ Cache golit: {count} chei șterse', 'success')

        return redirect(url_for('cache_page'))

    return render_template('cache.html',
                           stats=cache.get_stats(),
                           data=cache.cache)


@app.route('/message_broker', methods=['GET', 'POST'])
def message_broker_page():
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'create':
            queue = request.form.get('queue_name')
            if broker.create_queue(queue):
                monitoring.log("INFO", f"Queue created: {queue}")
                flash(f'✓ Queue creat: {queue}', 'success')
            else:
                flash('Queue există deja!', 'warning')

        elif action == 'delete_queue':
            queue = request.form.get('queue_name')
            if broker.delete_queue(queue):
                monitoring.log("WARNING", f"Queue deleted: {queue}")
                flash(f'✓ Queue șters: {queue}', 'success')

        elif action == 'publish':
            queue = request.form.get('queue_name')
            message = request.form.get('message')
            broker.publish(queue, message)
            monitoring.log("INFO", f"Message published to {queue}")
            flash(f'✓ Mesaj publicat în {queue}', 'success')

        elif action == 'consume':
            queue = request.form.get('queue_name')
            msg = broker.consume(queue)
            if msg:
                monitoring.log("INFO", f"Message consumed from {queue}")
                flash(f'✓ Mesaj: {msg}', 'success')
            else:
                flash('Queue gol!', 'warning')

        elif action == 'purge':
            queue = request.form.get('queue_name')
            count = broker.purge_queue(queue)
            monitoring.log("WARNING", f"Queue purged: {queue} ({count} messages)")
            flash(f'✓ Queue golit: {count} mesaje șterse', 'success')

        return redirect(url_for('message_broker_page'))

    return render_template('message_broker.html', stats=broker.get_stats())


@app.route('/cicd', methods=['GET', 'POST'])
def cicd_page():
    if request.method == 'POST':
        branch = request.form.get('branch', 'main')

        if 'code_file' in request.files:
            file = request.files['code_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                with open(filepath, 'r', encoding='utf-8') as f:
                    code = f.read()

                result = pipeline.run_pipeline(code, branch)
                monitoring.log("INFO", f"CI/CD Pipeline #{result['number']} - {result['overall_status']}")

                if result['overall_status'] == 'success':
                    flash(f'✓ Pipeline #{result["number"]} completat cu succes!', 'success')
                else:
                    flash(f'✗ Pipeline #{result["number"]} eșuat!', 'danger')

        return redirect(url_for('cicd_page'))

    return render_template('cicd.html',
                           pipeline=pipeline,
                           builds=pipeline.builds[-10:],
                           stats=pipeline.get_stats())


@app.route('/monitoring')
def monitoring_page():
    """Pagină de monitoring și logs"""
    metrics = monitoring.get_metrics()
    logs = monitoring.get_logs(50)

    return render_template('monitoring.html',
                           metrics=metrics,
                           logs=logs)
@app.route('/app-<int:build_id>')
def deployed_app(build_id):
    """Pagină pentru aplicația deployed"""
    # Găsește build-ul corespunzător
    build_info = None
    for build in pipeline.builds:
        if build["number"] == build_id:
            build_info = build
            break

    if not build_info:
        return render_template('404.html', message=f"Build #{build_id} not found"), 404

    # Generează statistici pentru aplicația deployed
    app_stats = {
        "build_id": build_id,
        "build_info": build_info,
        "deploy_time": build_info.get("time", "N/A"),
        "branch": build_info.get("branch", "main"),
        "status": build_info.get("overall_status", "unknown"),
        "uptime": "Running",
        "requests": random.randint(100, 1000),
        "active_users": random.randint(10, 50),
        "response_time": f"{random.uniform(50, 200):.2f}ms"
    }

    return render_template('deployed_app.html', stats=app_stats)


@app.route('/api/stats')
def api_stats():
    """API pentru statistici"""
    return jsonify({
        "infrastructure": iac.get_total_resources(),
        "database": database.get_stats(),
        "cache": cache.get_stats(),
        "broker": broker.get_stats(),
        "pipeline": pipeline.get_stats(),
        "monitoring": monitoring.get_metrics()
    })


@app.route('/api/health')
def api_health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": database.connected,
            "cache": True,
            "broker": True,
            "pipeline": pipeline.status
        }
    })


if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("  🌩️  CLOUD PROVIDER WEB APPLICATION - VERSIUNE COMPLETĂ")
    print("=" * 70)
    print("\n  🌐 Aplicația rulează pe: http://localhost:5000")
    print("\n  📋 Funcționalități disponibile:")
    print("     ✓ Infrastructure as Code (IaC) - Upload JSON config")
    print("     ✓ Cloud Database - CRUD + Migrare + Export")
    print("     ✓ Cloud Cache - Redis-like cu TTL")
    print("     ✓ Message Broker - RabbitMQ-like")
    print("     ✓ CI/CD Pipeline - Build, Test, Deploy")
    print("     ✓ Monitoring - Logs și metrici în timp real")
    print("     ✓ API REST - /api/stats, /api/health")
    print("\n" + "=" * 70 + "\n")

    monitoring.log("SUCCESS", "Application started on localhost:5000")
    app.run(debug=True, host='127.0.0.1', port=5000)
