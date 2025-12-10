# app_success.py
"""
Aplicație Cloud Demo - Cod Valid
Acest fișier va trece toate testele în pipeline
"""

import json
import time
from datetime import datetime


class CloudApplication:
    """Aplicație cloud de exemplu"""

    def __init__(self, name="CloudApp"):
        self.name = name
        self.version = "1.0.0"
        self.started_at = datetime.now()
        self.users = []
        self.requests_count = 0

    def add_user(self, user_data):
        """Adaugă un utilizator nou"""
        if not isinstance(user_data, dict):
            raise ValueError("User data must be a dictionary")

        if "name" not in user_data or "email" not in user_data:
            raise ValueError("User must have name and email")

        user_data["id"] = len(self.users) + 1
        user_data["created_at"] = datetime.now().isoformat()
        self.users.append(user_data)

        return user_data

    def get_user(self, user_id):
        """Returnează un utilizator după ID"""
        for user in self.users:
            if user.get("id") == user_id:
                return user
        return None

    def get_all_users(self):
        """Returnează toți utilizatorii"""
        return self.users

    def process_request(self, endpoint, data=None):
        """Procesează un request"""
        self.requests_count += 1

        if endpoint == "/health":
            return {
                "status": "healthy",
                "uptime": str(datetime.now() - self.started_at),
                "requests": self.requests_count
            }

        elif endpoint == "/users":
            if data:
                return self.add_user(data)
            return self.get_all_users()

        elif endpoint.startswith("/users/"):
            user_id = int(endpoint.split("/")[-1])
            return self.get_user(user_id)

        else:
            return {"error": "Endpoint not found"}, 404

    def calculate_stats(self):
        """Calculează statistici"""
        return {
            "total_users": len(self.users),
            "total_requests": self.requests_count,
            "app_name": self.name,
            "version": self.version,
            "uptime": str(datetime.now() - self.started_at)
        }

    def export_data(self):
        """Exportă datele în JSON"""
        return json.dumps({
            "users": self.users,
            "stats": self.calculate_stats()
        }, indent=2)


def main():
    """Funcția principală"""
    print("=" * 60)
    print(f"  🚀 Starting Cloud Application")
    print("=" * 60)

    # Inițializare aplicație
    app = CloudApplication("MyCloudApp")

    # Adaugă câțiva utilizatori de test
    print("\n📝 Adding test users...")
    users_to_add = [
        {"name": "Ion Popescu", "email": "ion@example.com"},
        {"name": "Maria Ionescu", "email": "maria@example.com"},
        {"name": "Andrei Georgescu", "email": "andrei@example.com"}
    ]

    for user_data in users_to_add:
        user = app.add_user(user_data)
        print(f"  ✓ Added user: {user['name']} (ID: {user['id']})")

    # Procesează câteva request-uri
    print("\n🔄 Processing requests...")

    health = app.process_request("/health")
    print(f"  ✓ Health check: {health['status']}")

    all_users = app.process_request("/users")
    print(f"  ✓ Retrieved {len(all_users)} users")

    user_1 = app.process_request("/users/1")
    if user_1:
        print(f"  ✓ Retrieved user: {user_1['name']}")

    # Afișează statistici
    print("\n📊 Application Statistics:")
    stats = app.calculate_stats()
    for key, value in stats.items():
        print(f"  • {key}: {value}")

    # Export date
    print("\n💾 Exporting data...")
    exported = app.export_data()
    print("  ✓ Data exported successfully")

    print("\n" + "=" * 60)
    print("  ✅ Application running successfully on localhost:5000")
    print("=" * 60)

    return app


if __name__ == "__main__":
    application = main()
    print("\n✅ Pipeline Test: SUCCESS")
    print("This code will pass all CI/CD tests!")
