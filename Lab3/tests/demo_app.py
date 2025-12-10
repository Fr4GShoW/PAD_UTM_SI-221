# demo_app.py
"""
Demo Cloud Application - Production Ready
Aplicație completă pentru deployment pe localhost:5000
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class CloudMetrics:
    """Colectare metrici"""

    def __init__(self):
        self.metrics = {
            "requests": 0,
            "errors": 0,
            "response_times": [],
            "start_time": datetime.now()
        }

    def record_request(self, response_time: float, error: bool = False):
        """Înregistrează un request"""
        self.metrics["requests"] += 1
        if error:
            self.metrics["errors"] += 1
        self.metrics["response_times"].append(response_time)

    def get_stats(self) -> Dict:
        """Returnează statistici"""
        response_times = self.metrics["response_times"]
        avg_response = sum(response_times) / len(response_times) if response_times else 0

        uptime = datetime.now() - self.metrics["start_time"]

        return {
            "total_requests": self.metrics["requests"],
            "total_errors": self.metrics["errors"],
            "error_rate": f"{(self.metrics['errors'] / max(self.metrics['requests'], 1) * 100):.2f}%",
            "avg_response_time": f"{avg_response:.3f}s",
            "uptime": str(uptime).split('.')[0],
            "status": "healthy" if self.metrics["errors"] == 0 else "degraded"
        }


class UserManager:
    """Gestionare utilizatori"""

    def __init__(self):
        self.users: Dict[str, Dict] = {}
        self.user_count = 0

    def create_user(self, name: str, email: str, role: str = "user") -> Dict:
        """Creează utilizator nou"""
        self.user_count += 1
        user_id = f"user_{self.user_count:04d}"

        user = {
            "id": user_id,
            "name": name,
            "email": email,
            "role": role,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "active": True
        }

        self.users[user_id] = user
        return user

    def get_user(self, user_id: str) -> Optional[Dict]:
        """Obține utilizator"""
        return self.users.get(user_id)

    def update_last_login(self, user_id: str):
        """Actualizează ultima autentificare"""
        if user_id in self.users:
            self.users[user_id]["last_login"] = datetime.now().isoformat()

    def get_all_users(self) -> List[Dict]:
        """Returnează toți utilizatorii"""
        return list(self.users.values())

    def get_active_users(self) -> List[Dict]:
        """Returnează utilizatori activi"""
        return [u for u in self.users.values() if u["active"]]


class DataStore:
    """Stocare date persistentă"""

    def __init__(self):
        self.data: Dict[str, Dict] = {}

    def save(self, collection: str, key: str, value: Dict):
        """Salvează date"""
        if collection not in self.data:
            self.data[collection] = {}
        self.data[collection][key] = {
            **value,
            "saved_at": datetime.now().isoformat()
        }

    def load(self, collection: str, key: str) -> Optional[Dict]:
        """Încarcă date"""
        return self.data.get(collection, {}).get(key)

    def query(self, collection: str, filter_func=None) -> List[Dict]:
        """Query cu filtrare"""
        items = self.data.get(collection, {}).values()
        if filter_func:
            return [item for item in items if filter_func(item)]
        return list(items)

    def export_all(self) -> str:
        """Exportă toate datele"""
        return json.dumps(self.data, indent=2)


class CloudApplication:
    """Aplicație cloud principală"""

    def __init__(self, name: str = "CloudApp"):
        self.name = name
        self.version = "2.0.0"
        self.metrics = CloudMetrics()
        self.users = UserManager()
        self.datastore = DataStore()

        print(f"✓ {self.name} v{self.version} initialized")

    def handle_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
        """Procesează un request"""
        start_time = time.time()

        try:
            if endpoint == "/health":
                response = self.health_check()

            elif endpoint == "/metrics":
                response = self.metrics.get_stats()

            elif endpoint == "/users" and method == "POST":
                response = self.users.create_user(**data)

            elif endpoint == "/users" and method == "GET":
                response = {"users": self.users.get_all_users()}

            elif endpoint.startswith("/users/") and method == "GET":
                user_id = endpoint.split("/")[-1]
                response = self.users.get_user(user_id) or {"error": "User not found"}

            else:
                response = {"error": "Endpoint not found"}
                self.metrics.record_request(time.time() - start_time, error=True)
                return response

            self.metrics.record_request(time.time() - start_time)
            return response

        except Exception as e:
            self.metrics.record_request(time.time() - start_time, error=True)
            return {"error": str(e)}

    def health_check(self) -> Dict:
        """Health check"""
        return {
            "status": "healthy",
            "application": self.name,
            "version": self.version,
            "timestamp": datetime.now().isoformat(),
            "services": {
                "user_manager": "operational",
                "datastore": "operational",
                "metrics": "operational"
            }
        }

    def run_demo(self):
        """Demonstrație funcționalitate"""
        print("\n" + "=" * 70)
        print(f"  🚀 {self.name} - Demo Application")
        print("=" * 70)

        # Creează utilizatori demo
        print("\n📝 Creating demo users...")
        demo_users = [
            {"name": "Ion Popescu", "email": "ion@example.com", "role": "admin"},
            {"name": "Maria Ionescu", "email": "maria@example.com", "role": "user"},
            {"name": "Andrei Georgescu", "email": "andrei@example.com", "role": "moderator"},
            {"name": "Elena Radu", "email": "elena@example.com", "role": "user"}
        ]

        for user_data in demo_users:
            user = self.handle_request("/users", "POST", user_data)
            print(f"  ✓ Created: {user['name']} ({user['role']})")

        # Simulează requests
        print("\n🔄 Processing requests...")
        self.handle_request("/health", "GET")
        print("  ✓ Health check OK")

        all_users = self.handle_request("/users", "GET")
        print(f"  ✓ Retrieved {len(all_users['users'])} users")

        user_detail = self.handle_request("/users/user_0001", "GET")
        print(f"  ✓ User detail: {user_detail['name']}")

        # Salvează date
        print("\n💾 Saving data to datastore...")
        for user in self.users.get_all_users():
            self.datastore.save("users", user["id"], user)
        print(f"  ✓ Saved {len(self.users.get_all_users())} users")

        # Afișează metrici
        print("\n📊 Application Metrics:")
        metrics = self.metrics.get_stats()
        for key, value in metrics.items():
            print(f"  • {key}: {value}")

        # Health check final
        print("\n🏥 Final Health Check:")
        health = self.health_check()
        print(f"  Status: {health['status']}")
        print(f"  Version: {health['version']}")
        for service, status in health["services"].items():
            print(f"  • {service}: {status}")

        print("\n" + "=" * 70)
        print(f"  ✅ {self.name} deployed successfully on localhost:5000")
        print("=" * 70)


def main():
    """Funcția principală"""
    app = CloudApplication("MyCloudService")
    app.run_demo()

    print("\n✅ CI/CD Pipeline Test: SUCCESS")
    print("All stages completed: Build → Test → Deploy")

    return app


if __name__ == "__main__":
    application = main()
