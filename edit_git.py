import json
from datetime import datetime
import os
import sys
import textwrap


class READMEGenerator:
    def __init__(self):
        self.sections = {}

    def set_basic_info(self, title, description, repo_url, live_url=""):
        """Set basic project information"""
        self.sections['basic'] = {
            'title': title,
            'description': description,
            'repo_url': repo_url,
            'live_url': live_url
        }

    def set_badges(self, badges):
        """Set project badges"""
        self.sections['badges'] = badges

    def set_features(self, features):
        """Set project features"""
        self.sections['features'] = features

    def set_technologies(self, technologies):
        """Set technologies used"""
        self.sections['technologies'] = technologies

    def set_installation(self, steps):
        """Set installation steps"""
        self.sections['installation'] = steps

    def set_usage(self, usage_instructions):
        """Set usage instructions"""
        self.sections['usage'] = usage_instructions

    def set_api(self, api_endpoints):
        """Set API documentation"""
        self.sections['api'] = api_endpoints

    def set_project_structure(self, structure):
        """Set project structure"""
        self.sections['structure'] = structure

    def set_labs(self, labs):
        """Set laboratory works with descriptions"""
        self.sections['labs'] = labs

    def set_contributing(self, guidelines):
        """Set contributing guidelines"""
        self.sections['contributing'] = guidelines

    def set_license(self, license_type):
        """Set license information"""
        self.sections['license'] = license_type

    def generate_badges(self):
        """Generate badges section"""
        if 'badges' not in self.sections:
            return ""

        badges_md = ""
        for badge in self.sections['badges']:
            badges_md += f"![{badge['alt']}]({badge['url']}) "

        return badges_md + "\n\n"

    def generate_labs_section(self):
        """Generate labs section with buttons and descriptions"""
        if 'labs' not in self.sections:
            return ""

        labs_md = "## 🗂️ Laboratory Works\n\n"

        for lab in self.sections['labs']:
            # Create badge-style button for each lab
            lab_name = lab.get('name', 'Unnamed Lab')
            lab_path = lab.get('path', '#')
            lab_badge = f"[![{lab_name}](https://img.shields.io/badge/{lab_name.replace(' ', '%20')}-8A2BE2?style=for-the-badge&logo=github&logoColor=white)]({lab_path})"

            labs_md += f"### {lab_badge}\n\n"

            # Handle optional fields with defaults
            title = lab.get('title', f'{lab_name} - Distributed Systems Laboratory')
            description = lab.get('description', 'Laboratory work for Distributed Systems Programming course.')

            labs_md += f"**{title}**\n\n"
            labs_md += f"{description}\n\n"

            # Add technologies if specified
            if 'technologies' in lab:
                labs_md += "**Technologies:** " + ", ".join(f"`{tech}`" for tech in lab['technologies']) + "\n\n"

            # Add features if specified
            if 'features' in lab:
                labs_md += "**Key Features:**\n"
                for feature in lab['features']:
                    labs_md += f"- {feature}\n"
                labs_md += "\n"

            labs_md += "---\n\n"

        return labs_md

    def generate_features(self):
        """Generate features section"""
        if 'features' not in self.sections:
            return ""

        features_md = "## ✨ Features\n\n"
        for feature in self.sections['features']:
            features_md += f"- {feature}\n"

        return features_md + "\n"

    def generate_technologies(self):
        """Generate technologies section"""
        if 'technologies' not in self.sections:
            return ""

        tech_md = "## 🛠️ Technologies\n\n"
        for tech in self.sections['technologies']:
            tech_md += f"- **{tech}**\n"

        return tech_md + "\n"

    def generate_installation(self):
        """Generate installation section"""
        if 'installation' not in self.sections:
            return ""

        install_md = "## 🚀 Installation\n\n"
        for i, step in enumerate(self.sections['installation'], 1):
            install_md += f"{i}. {step}\n"

        return install_md + "\n"

    def generate_usage(self):
        """Generate usage section"""
        if 'usage' not in self.sections:
            return ""

        usage_md = "## 📖 Usage\n\n"
        if isinstance(self.sections['usage'], list):
            for instruction in self.sections['usage']:
                usage_md += f"{instruction}\n\n"
        else:
            usage_md += self.sections['usage'] + "\n\n"

        return usage_md

    def generate_api(self):
        """Generate API documentation"""
        if 'api' not in self.sections:
            return ""

        api_md = "## 🔧 API Reference\n\n"
        for endpoint in self.sections['api']:
            api_md += f"### `{endpoint['method']} {endpoint['path']}`\n\n"
            api_md += f"**Description:** {endpoint['description']}\n\n"
            if 'parameters' in endpoint:
                api_md += "**Parameters:**\n\n"
                for param in endpoint['parameters']:
                    api_md += f"- `{param['name']}` ({param['type']}): {param['description']}\n"
            api_md += "\n"

        return api_md

    def generate_structure(self):
        """Generate project structure"""
        if 'structure' not in self.sections:
            return ""

        structure_md = "## 📁 Project Structure\n\n```\n"
        structure_md += self.sections['structure']
        structure_md += "\n```\n\n"

        return structure_md

    def generate_contributing(self):
        """Generate contributing guidelines"""
        if 'contributing' not in self.sections:
            return "## 🤝 Contributing\n\nContributions are welcome! Please feel free to submit a Pull Request.\n\n"

        return f"## 🤝 Contributing\n\n{self.sections['contributing']}\n\n"

    def generate_license(self):
        """Generate license section"""
        basic = self.sections.get('basic', {})
        license_type = self.sections.get('license', 'MIT')

        return f"## 📄 License\n\nThis project is licensed under the {license_type} License - see the [LICENSE](LICENSE) file for details.\n\n"

    def generate_readme(self):
        """Generate complete README"""
        basic = self.sections['basic']

        readme = f"""# {basic['title']}

{self.generate_badges()}
## 📋 Description

{basic['description']}

"""

        # Add live demo link if available
        if basic.get('live_url'):
            readme += f"**Live Demo:** [{basic['live_url']}]({basic['live_url']})\n\n"

        # Generate all sections - Labs section comes early for visibility
        sections = [
            self.generate_labs_section(),  # Added labs section
            self.generate_features(),
            self.generate_technologies(),
            self.generate_installation(),
            self.generate_usage(),
            self.generate_api(),
            self.generate_structure(),
            self.generate_contributing(),
            self.generate_license()
        ]

        readme += "".join(sections)

        # Add footer
        readme += f"---\n\n*Generated with ❤️ using Python README Generator*"

        return readme


def create_pad_project_example():
    """Create example for PAD_UTM_SI-221 project with 3 Python-focused labs"""
    generator = READMEGenerator()

    # Basic info
    generator.set_basic_info(
        title="PAD_UTM_SI-221",
        description="Proiect pentru disciplina Programarea Aplicațiilor Distribuite (PAD) - UTM, grupa SI-221. Acest proiect se concentrează pe scriptare Python pentru sisteme distribuite, cu aplicații practice în mesagerie, proxy web și cloud.",
        repo_url="https://github.com/Fr4GShoW/PAD_UTM_SI-221",
        live_url=""
    )

    # Badges - Python focused
    badges = [
        {"alt": "Python",
         "url": "https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"},
        {"alt": "Version", "url": "https://img.shields.io/badge/version-1.0.0-blue?style=for-the-badge"},
        {"alt": "License", "url": "https://img.shields.io/badge/license-MIT-green?style=for-the-badge"}
    ]
    generator.set_badges(badges)

    # Labs section with direct buttons - ONLY 3 LABS, PYTHON FOCUSED
    labs = [
        {
            "name": "Lab 1",
            "path": "https://github.com/Fr4GShoW/PAD_UTM_SI-221/tree/main/Lab1",
            "title": "Agent de Mesagerie",
            "description": "Implementarea unui sistem de mesagerie distribuit folosind Python. Acest laborator demonstrează comunicarea asincronă între procesoare folosind cozi de mesaje și socket-uri.",
            "technologies": ["Python 3", "Socket Programming", "Threading", "Message Queues"],
            "features": [
                "Server de mesagerie cu suport pentru multiple clienți",
                "Comunicare asincronă folosind fire de execuție",
                "Protocol de mesaje personalizat",
                "Gestionarea conexiunilor persistente",
                "Sistem de autentificare simplu"
            ]
        },
        {
            "name": "Lab 2",
            "path": "https://github.com/Fr4GShoW/PAD_UTM_SI-221/tree/main/Lab2",
            "title": "Web Proxy: Realizarea Transparenței în Distribuire",
            "description": "Dezvoltarea unui server proxy web care asigură transparența în distribuirea resurselor. Proxy-ul cachează cererile și optimizează comunicarea între clienți și servere.",
            "technologies": ["Python 3", "HTTP Protocol", "Caching", "URL Filtering"],
            "features": [
                "Interceptare și procesare cereri HTTP",
                "Sistem de caching pentru resurse statice",
                "Filtrare URL-uri bazată pe reguli",
                "Logging extensiv al traficului",
                "Suport pentru conexiuni securizate"
            ]
        },
        {
            "name": "Lab 3",
            "path": "https://github.com/Fr4GShoW/PAD_UTM_SI-221/tree/main/Lab3",
            "title": "Aplicație în Nori (Cloud Application)",
            "description": "Crearea unei aplicații distribuite în cloud folosind servicii Python. Integrare cu API-uri cloud și gestionarea resurselor distribuite.",
            "technologies": ["Python 3", "Flask/FastAPI", "REST APIs", "Cloud Storage", "Microservices"],
            "features": [
                "Arhitectură microservicii",
                "API RESTful pentru comunicare",
                "Integrare cu servicii cloud",
                "Managementul stării distribuite",
                "Scalare orizontală a serviciilor"
            ]
        }
    ]
    generator.set_labs(labs)

    # Features - Python focused
    features = [
        "Scriptare intensivă în Python pentru sisteme distribuite",
        "Comunicare prin socket-uri TCP/UDP",
        "Procesare paralelă folosind threading și multiprocessing",
        "Arhitecturi scalabile și resiliente",
        "Integrare cu protocoale web (HTTP/HTTPS)",
        "Gestionarea resurselor în medii distribuite"
    ]
    generator.set_features(features)

    # Technologies - Python focused, minimal XML/JSON
    technologies = [
        "Python 3.8+",
        "Socket Programming",
        "Threading & Multiprocessing",
        "Flask/FastAPI pentru servicii web",
        "Requests pentru HTTP clients",
        "SQLite/PostgreSQL pentru stocare",
        "Unittest pentru teste"
    ]
    generator.set_technologies(technologies)

    # Installation - Python focused
    installation_steps = [
        "Clonează repository-ul: `git clone https://github.com/Fr4GShoW/PAD_UTM_SI-221.git`",
        "Intră în directorul proiectului: `cd PAD_UTM_SI-221`",
        "Creează un mediu virtual: `python -m venv venv`",
        "Activează mediul virtual:",
        "  - Windows: `venv\\Scripts\\activate`",
        "  - Linux/Mac: `source venv/bin/activate`",
        "Instalează dependințele: `pip install -r requirements.txt`",
        "Rulează aplicațiile individuale din fiecare folder Lab"
    ]
    generator.set_installation(installation_steps)

    # Usage instructions for each lab
    usage_instructions = [
        "## 🚀 Cum să rulezi proiectele",
        "",
        "### Lab 1 - Agent de Mesagerie",
        "```bash",
        "cd Lab1",
        "python message_server.py",
        "# În alt terminal:",
        "python message_client.py",
        "```",
        "",
        "### Lab 2 - Web Proxy",
        "```bash",
        "cd Lab2",
        "python proxy_server.py",
        "# Configurează browser-ul să folosească proxy pe localhost:8080",
        "```",
        "",
        "### Lab 3 - Aplicație Cloud",
        "```bash",
        "cd Lab3",
        "python cloud_app.py",
        "# Accesează http://localhost:5000 în browser",
        "```"
    ]
    generator.set_usage(usage_instructions)

    # Project Structure - Simplified for 3 labs
    structure = """PAD_UTM_SI-221/
├── Lab1/                  # Agent de Mesagerie
│   ├── src/
│   │   ├── message_server.py
│   │   ├── message_client.py
│   │   └── message_protocol.py
│   ├── tests/
│   └── requirements.txt
├── Lab2/                  # Web Proxy
│   ├── src/
│   │   ├── proxy_server.py
│   │   ├── cache_manager.py
│   │   └── url_filter.py
│   ├── tests/
│   └── requirements.txt
├── Lab3/                  # Aplicație Cloud
│   ├── src/
│   │   ├── cloud_app.py
│   │   ├── api/
│   │   ├── services/
│   │   └── models/
│   ├── tests/
│   └── requirements.txt
├── docs/                  # Documentație
├── requirements.txt       # Dependințe generale
└── README.md"""
    generator.set_project_structure(structure)

    # Contributing
    generator.set_contributing("""
1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'") 
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
    """)

    # License
    generator.set_license("MIT")

    return generator.generate_readme()


def generate_repo_template(generator):
    """Return a dict mapping relative file paths -> file contents for a recommended repo layout.
    Mostly Python files, minimal XML and JSON samples."""
    readme = generator.generate_readme()

    files = {
        "README.md": readme,
        ".gitignore": generate_gitignore(),
        "requirements.txt": generate_requirements(),
        "LICENSE": generate_mit_license(),
        "Lab1/src/message_server.py": LAB1_MESSAGE_SERVER,
        "Lab1/src/message_client.py": LAB1_MESSAGE_CLIENT,
        "Lab1/README.md": "# Lab 1 — Agent de Mesagerie\n\nSee src/ for implementation.",
        "Lab2/src/proxy_server.py": LAB2_PROXY_SERVER,
        "Lab2/src/cache_manager.py": LAB2_CACHE_MANAGER,
        "Lab2/config/config.json": generate_minimal_json(),
        "Lab2/config/rules.xml": generate_minimal_xml(),
        "Lab2/README.md": "# Lab 2 — Web Proxy\n\nProxy, caching, URL filtering examples.",
        "Lab3/src/cloud_app.py": LAB3_CLOUD_APP,
        "Lab3/README.md": "# Lab 3 — Cloud Application\n\nMinimal Flask example.",
        "tests/test_lab1.py": TEST_PLACEHOLDER,
        "tests/test_lab2.py": TEST_PLACEHOLDER,
        "docs/architecture.md": "# Architecture\n\nHigh-level architecture notes.",
        "tools/backend_simulator.py": BACKEND_SIMULATOR_STUB,
        "tools/http_proxy.py": HTTP_PROXY_STUB,
        "tools/health_check.py": HEALTH_CHECK_STUB,
        "tools/management_API.py": MANAGEMENT_API_STUB,
    }

    return files


def scaffold_repo(target_dir, files_map):
    """Write the files_map into target_dir, creating directories as needed."""
    for rel_path, content in files_map.items():
        full_path = os.path.join(target_dir, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
    print(f"✅ Scaffold written to: {os.path.abspath(target_dir)}")


def generate_gitignore():
    return textwrap.dedent("""\
        __pycache__/
        *.pyc
        .env
        venv/
        .venv/
        .DS_Store
        .pytest_cache/
    """)


def generate_requirements():
    return textwrap.dedent("""\
        flask
        requests
    """)


def generate_mit_license():
    year = datetime.now().year
    return textwrap.dedent(f"""\
        MIT License

        Copyright (c) {year} Fr4GShoW

        Permission is hereby granted, free of charge, to any person obtaining a copy
        of this software and associated documentation files (the "Software"), to deal
        in the Software without restriction...
    """)


def generate_minimal_json():
    return textwrap.dedent("""\
        {
            "proxy": {
                "host": "localhost",
                "port": 8080,
                "cache_enabled": true
            }
        }
    """)


def generate_minimal_xml():
    return textwrap.dedent("""\
        <?xml version="1.0" encoding="UTF-8"?>
        <rules>
            <rule id="1" action="allow" pattern=".*" />
        </rules>
    """)


# Small placeholders/stubs (kept intentionally minimal and Pythonic)
LAB1_MESSAGE_SERVER = textwrap.dedent("""\
    # simple message server example
    import socket
    import threading

    def handle_client(conn, addr):
        with conn:
            print("Connected", addr)
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)

    def main():
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.bind(('localhost', 9000))
        srv.listen(5)
        print("Message server listening on 9000")
        while True:
            conn, addr = srv.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

    if __name__ == '__main__':
        main()
""")

LAB1_MESSAGE_CLIENT = textwrap.dedent("""\
    # simple message client example
    import socket
    def main():
        with socket.create_connection(('localhost', 9000)) as s:
            s.sendall(b'Hello')
            print(s.recv(1024))
    if __name__ == '__main__':
        main()
""")

LAB2_PROXY_SERVER = textwrap.dedent("""\
    # minimal transparent proxy skeleton
    import socket
    def start_proxy(host='localhost', port=8080):
        print(f"Proxy would listen on {host}:{port} (stub)")
    if __name__ == '__main__':
        start_proxy()
""")

LAB2_CACHE_MANAGER = textwrap.dedent("""\
    # simple in-memory cache example
    _CACHE = {}
    def get(key):
        return _CACHE.get(key)
    def set(key, value):
        _CACHE[key] = value
""")

LAB3_CLOUD_APP = textwrap.dedent("""\
    # minimal Flask app for lab3
    from flask import Flask, jsonify
    app = Flask(__name__)
    @app.route('/')
    def index():
        return jsonify({ 'message': 'Hello from Lab3 cloud app' })
    if __name__ == '__main__':
        app.run(port=5000)
""")

TEST_PLACEHOLDER = textwrap.dedent("""\
    def test_placeholder():
        assert True
""")

# Tool stubs that match names referenced elsewhere (kept minimal)
BACKEND_SIMULATOR_STUB = textwrap.dedent("""\
    # backend_simulator stub
    import time
    def start(port, name):
        print(f"Starting backend {name} on {port} (stub)")
""")

HTTP_PROXY_STUB = textwrap.dedent("""\
    # http_proxy stub
    def start(host='localhost', port=8080):
        print(f"http proxy stub listening on {host}:{port}")
    def get_statistics():
        return {'connections': 0}
""")

HEALTH_CHECK_STUB = textwrap.dedent("""\
    # health_check stub
    def perform_basic_check(host, port):
        return True
""")

MANAGEMENT_API_STUB = textwrap.dedent("""\
    # management_API stub
    def serve(host='localhost', port=8081):
        print(f"management API stub on {host}:{port}")
""")

# Update save_readme to optionally scaffold repository when requested via CLI
def save_readme(content, filename="README.md"):
    """Save README content to file"""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✅ README generated successfully: {filename}")


# Replace example usage with optional scaffolding via CLI
if __name__ == "__main__":
    generator = READMEGenerator()
    # ...existing example population code...
    # Instead of duplicating the whole example setup, reuse the function if present
    try:
        readme_content = create_pad_project_example()
    except Exception:
        # fallback: generate a minimal README if example function changed
        generator.set_basic_info("PAD_UTM_SI-221", "PAD project", "https://github.com/Fr4GShoW/PAD_UTM_SI-221")
        readme_content = generator.generate_readme()

    save_readme(readme_content)

    # CLI: optionally scaffold entire repository layout
    if "--scaffold" in sys.argv:
        idx = sys.argv.index("--scaffold")
        target = "PAD_UTM_SI-221_scaffold"
        if idx + 1 < len(sys.argv) and not sys.argv[idx + 1].startswith("--"):
            target = sys.argv[idx + 1]
        files_map = generate_repo_template(generator)
        scaffold_repo(target, files_map)
    else:
        print("\nRun this script with '--scaffold [target_dir]' to write a recommended repository layout (mostly Python).")

