# PAD_UTM_SI-221

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Version](https://img.shields.io/badge/version-1.0.0-blue?style=for-the-badge) ![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge) 


## 📋 Description

Proiect pentru disciplina Programarea Aplicațiilor Distribuite (PAD) - UTM, grupa SI-221. Acest proiect se concentrează pe scriptare Python pentru sisteme distribuite, cu aplicații practice în mesagerie, proxy web și cloud.

## 🗂️ Laboratory Works

### [![Lab 1](https://img.shields.io/badge/Lab%201-8A2BE2?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Fr4GShoW/PAD_UTM_SI-221/tree/main/Lab1)

**Agent de Mesagerie**

Implementarea unui sistem de mesagerie distribuit folosind Python. Acest laborator demonstrează comunicarea asincronă între procesoare folosind cozi de mesaje și socket-uri.

**Technologies:** `Python 3`, `Socket Programming`, `Threading`, `Message Queues`

**Key Features:**
- Server de mesagerie cu suport pentru multiple clienți
- Comunicare asincronă folosind fire de execuție
- Protocol de mesaje personalizat
- Gestionarea conexiunilor persistente
- Sistem de autentificare simplu

---

### [![Lab 2](https://img.shields.io/badge/Lab%202-8A2BE2?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Fr4GShoW/PAD_UTM_SI-221/tree/main/Lab2)

**Web Proxy: Realizarea Transparenței în Distribuire**

Dezvoltarea unui server proxy web care asigură transparența în distribuirea resurselor. Proxy-ul cachează cererile și optimizează comunicarea între clienți și servere.

**Technologies:** `Python 3`, `HTTP Protocol`, `Caching`, `URL Filtering`

**Key Features:**
- Interceptare și procesare cereri HTTP
- Sistem de caching pentru resurse statice
- Filtrare URL-uri bazată pe reguli
- Logging extensiv al traficului
- Suport pentru conexiuni securizate

---

### [![Lab 3](https://img.shields.io/badge/Lab%203-8A2BE2?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Fr4GShoW/PAD_UTM_SI-221/tree/main/Lab3)

**Aplicație în Nori (Cloud Application)**

Crearea unei aplicații distribuite în cloud folosind servicii Python. Integrare cu API-uri cloud și gestionarea resurselor distribuite.

**Technologies:** `Python 3`, `Flask/FastAPI`, `REST APIs`, `Cloud Storage`, `Microservices`

**Key Features:**
- Arhitectură microservicii
- API RESTful pentru comunicare
- Integrare cu servicii cloud
- Managementul stării distribuite
- Scalare orizontală a serviciilor

---

## ✨ Features

- Scriptare intensivă în Python pentru sisteme distribuite
- Comunicare prin socket-uri TCP/UDP
- Procesare paralelă folosind threading și multiprocessing
- Arhitecturi scalabile și resiliente
- Integrare cu protocoale web (HTTP/HTTPS)
- Gestionarea resurselor în medii distribuite

## 🛠️ Technologies

- **Python 3.8+**
- **Socket Programming**
- **Threading & Multiprocessing**
- **Flask/FastAPI pentru servicii web**
- **Requests pentru HTTP clients**
- **SQLite/PostgreSQL pentru stocare**
- **Unittest pentru teste**

## 🚀 Installation

1. Clonează repository-ul: `git clone https://github.com/Fr4GShoW/PAD_UTM_SI-221.git`
2. Intră în directorul proiectului: `cd PAD_UTM_SI-221`
3. Creează un mediu virtual: `python -m venv venv`
4. Activează mediul virtual:
5.   - Windows: `venv\Scripts\activate`
6.   - Linux/Mac: `source venv/bin/activate`
7. Instalează dependințele: `pip install -r requirements.txt`
8. Rulează aplicațiile individuale din fiecare folder Lab

## 📖 Usage

## 🚀 Cum să rulezi proiectele



### Lab 1 - Agent de Mesagerie

```bash

cd Lab1

python server.py

# În alt terminal:
python listener.py
python gui_sender.py

```



### Lab 2 - Web Proxy

```bash

cd Lab2

python main.py

# Configurează browser-ul să folosească proxy pe localhost:8080

```



### Lab 3 - Aplicație Cloud

```bash

cd Lab3

python cloud_app.py

# Accesează http://localhost:5000 în browser

```

## 📁 Project Structure

```
PAD_UTM_SI-221/
├── Lab1/                  # Agent de Mesagerie
│   ├── src/
│   │   ├── server.py
│   │   ├── listener.py
│   │   ├── schema.json
│   │   ├── schema.xsd
│   │   └── gui_sender.py
│   ├── messages.json
│   ├── messages.xml
│   └── requirements.txt
├── Lab2/                  # Web Proxy
│   ├── src/
│   │   ├── http_proxy.py
│   │   ├── health_check.py
│   │   ├── backend_simulator.py
│   │   ├── main.py
│   └── └── management_API.py
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
└── README.md
```

## 🤝 Contributing


1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'") 
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
    

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

*Generated with ❤️ using Python README Generator*