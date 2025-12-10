# simple_test.py
"""
Aplicație simplă pentru test rapid CI/CD
"""


def greet(name):
    """Salută utilizatorul"""
    return f"Hello, {name}!"


def calculate_sum(a, b):
    """Calculează suma"""
    return a + b


def get_server_info():
    """Info despre server"""
    return {
        "server": "localhost",
        "port": 5000,
        "status": "running",
        "version": "1.0.0"
    }


def main():
    print("=" * 50)
    print("  Simple Cloud Application")
    print("=" * 50)

    print(f"\n{greet('Cloud User')}")
    print(f"Sum: 10 + 20 = {calculate_sum(10, 20)}")

    print("\nServer Info:")
    info = get_server_info()
    for key, value in info.items():
        print(f"  {key}: {value}")

    print("\n✅ Application ready for deployment!")
    return True


if __name__ == "__main__":
    success = main()
    if success:
        print("✅ Test: PASSED")
