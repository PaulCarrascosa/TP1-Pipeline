# TP1 - Mise en place d'un projet FastAPI structuré en couches

Projet de gestion de bibliothèque utilisant une architecture N-Tiers avec FastAPI.

## Structure du projet

```
library_app/
│
├── src/                    # Code source principal
│   ├── __init__.py
│   ├── main.py             # Point d'entrée de l'application
│   ├── config.py           # Configuration de l'application
│   │
│   ├── api/                # Couche de présentation (API REST)
│   │   ├── __init__.py
│   │   ├── dependencies.py # Dépendances partagées pour les routes
│   │   ├── routes/         # Définition des routes API
│   │   │   ├── __init__.py
│   │   │   ├── books.py    # Routes pour les livres
│   │   │   ├── users.py    # Routes pour les utilisateurs
│   │   │   └── loans.py    # Routes pour les emprunts
│   │   │
│   │   └── schemas/        # Modèles Pydantic pour validation et sérialisation
│   │       ├── __init__.py
│   │       ├── books.py
│   │       ├── users.py
│   │       └── loans.py
│   │
│   ├── services/           # Couche métier
│   │   ├── __init__.py
│   │   ├── books.py        # Logique métier pour les livres
│   │   ├── users.py        # Logique métier pour les utilisateurs
│   │   └── loans.py        # Logique métier pour les emprunts
│   │
│   ├── repositories/       # Couche d'accès aux données
│   │   ├── __init__.py
│   │   ├── base.py         # Repository Pattern de base
│   │   ├── books.py        # Repository pour les livres
│   │   ├── users.py        # Repository pour les utilisateurs
│   │   └── loans.py        # Repository pour les emprunts
│   │
│   ├── models/             # Modèles SQLAlchemy
│   │   ├── __init__.py
│   │   ├── base.py         # Classe de base pour les modèles
│   │   ├── books.py        # Modèle Book
│   │   ├── users.py        # Modèle User
│   │   └── loans.py        # Modèle Loan
│   │
│   ├── db/                 # Configuration de la base de données
│   │   ├── __init__.py
│   │   └── session.py      # Session SQLAlchemy
│   │
│   └── utils/              # Utilitaires et fonctions communes
│       ├── __init__.py
│       └── security.py     # Fonctions de sécurité (JWT, password hashing)
│
├── alembic/                # Migrations de base de données
│   ├── env.py
│   ├── alembic.ini
│   └── versions/
│
├── tests/                  # Tests unitaires et d'intégration
│   ├── __init__.py
│   ├── conftest.py         # Configuration pytest
│   ├── test_api/           # Tests API
│   ├── test_services/      # Tests services
│   └── test_repositories/  # Tests repositories
│
├── requirements.txt        # Dépendances du projet
├── .env.example            # Exemple de variables d'environnement
├── run.py                  # Lanceur de l'application
└── README.md               # Documentation du projet
```

## Installation

### 1. Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Configurer les variables d'environnement

```bash
cp .env.example .env
```

## Utilisation

### Lancer l'application

```bash
python run.py
```

L'application sera accessible à `http://localhost:8000`

### Documentation Swagger

La documentation interactive est disponible à :
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

## Architecture N-Tiers

### 1. Couche de présentation (API)
- Endpoints FastAPI (`src/api/routes/`)
- Validation des requêtes avec Pydantic (`src/api/schemas/`)
- Dépendances FastAPI (`src/api/dependencies.py`)

### 2. Couche métier (Services)
- Logique applicative (`src/services/`)
- Orchestration entre repositories et API

### 3. Couche d'accès aux données (Repositories)
- Repository Pattern pour l'abstraction des données (`src/repositories/`)
- Requêtes SQLAlchemy réutilisables

### 4. Couche données (Models)
- Modèles SQLAlchemy (`src/models/`)
- Gestion de la base de données

### 5. Configuration et Utilitaires
- Configuration centralisée (`src/config.py`)
- Sécurité (JWT, password hashing) (`src/utils/security.py`)

## Endpoints disponibles

### Livres
- `GET /api/v1/books/` - Lister tous les livres
- `POST /api/v1/books/` - Créer un nouveau livre
- `GET /api/v1/books/{id}` - Obtenir un livre par ID

### Utilisateurs
- `GET /api/v1/users/` - Lister tous les utilisateurs
- `POST /api/v1/users/` - Créer un nouvel utilisateur
- `GET /api/v1/users/{id}` - Obtenir un utilisateur par ID

### Emprunts
- `GET /api/v1/loans/` - Lister tous les emprunts
- `POST /api/v1/loans/` - Créer un nouvel emprunt
- `GET /api/v1/loans/{id}` - Obtenir un emprunt par ID

## Tests

### Lancer les tests

```bash
pytest tests/ -v
```

### Avec couverture de code

```bash
pytest tests/ -v --cov=src --cov-report=html
```

## Migrations de base de données

### Créer une migration

```bash
alembic revision --autogenerate -m "Description"
```

### Appliquer les migrations

```bash
alembic upgrade head
```

### Revenir à la version précédente

```bash
alembic downgrade -1
```

## Configuration

La configuration se fait via le fichier `.env` basé sur le template `.env.example`.

### Variables d'environnement

- `PROJECT_NAME`: Nom du projet
- `API_V1_STR`: Préfixe de l'API v1 (défaut: `/api/v1`)
- `SECRET_KEY`: Clé secrète pour JWT
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Durée d'expiration des tokens (défaut: 8 jours)
- `DATABASE_URL`: URL de la base de données (défaut: SQLite)
- `BACKEND_CORS_ORIGINS`: Origines CORS autorisées
- `DEBUG`: Mode debug

## Fichiers clés

### `src/config.py`
Configuration centralisée utilisant Pydantic Settings

### `src/main.py`
Application FastAPI avec configuration CORS et routes

### `src/models/base.py`
Classe de base pour tous les modèles SQLAlchemy avec `id`, `created_at`, `updated_at`

### `src/db/session.py`
Configuration de la session SQLAlchemy et dépendances FastAPI

### `src/repositories/base.py`
Repository Pattern générique pour les opérations CRUD

### `src/utils/security.py`
Utilities pour la sécurité : password hashing avec bcrypt, JWT token generation

## Frontend

### Lancer le frontend

Le frontend est une application HTML/JS statique. Il faut le servir via HTTP (ne pas ouvrir le fichier directement dans le navigateur).

Dans un terminal séparé :

```bash
cd frontend
python -m http.server 5000
```

Accède ensuite à `http://localhost:5000`.

> Le backend doit tourner sur le port 8000 en même temps.

---

## Déploiement sur VM Vagrant

### Prérequis

- [Vagrant](https://www.vagrantup.com/)
- [VirtualBox](https://www.virtualbox.org/)

### Lancer la VM

```powershell
vagrant up
vagrant ssh
```

### Lancer le projet dans la VM

```bash
cd /app
source .venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

L'API est accessible sur `http://192.168.50.4:8000`.

### Mettre à jour le projet

```bash
cd /app
git pull origin main
source .venv/bin/activate
pip install -r requirements.txt
```

### Éteindre la VM

```powershell
vagrant halt
```

---

## CI/CD avec Jenkins

### Prérequis Jenkins

- Plugin **SonarQube Scanner** installé
- Plugin **Workspace Cleanup** installé
- `sonar-scanner` installé sur la VM (`/usr/local/bin/sonar-scanner`)

### Configuration Jenkins

1. **Manage Jenkins > Configure System > SonarQube servers**
   - Nom : `SonarQube`
   - URL : `http://localhost:9000`
   - Token : généré depuis SonarQube (My Account > Security > Generate Tokens)

2. Créer un job **Pipeline** et coller le contenu du `Jenkinsfile`

### Pipeline

Le pipeline exécute les étapes suivantes :

| Étape | Description |
|-------|-------------|
| Checkout | Clone le repo GitHub |
| Installer les dépendances | Via Nexus (proxy PyPI) avec fallback PyPI |
| Tests | 26 tests avec couverture de code |
| Analyse SonarQube | Analyse qualité du code |
| Quality Gate | Vérification du seuil qualité |
| Vérification démarrage | Démarre l'API et vérifie qu'elle répond |

---

## SonarQube

### Installation

```bash
wget https://binaries.sonarsource.com/Distribution/sonarqube/sonarqube-10.4.1.88267.zip
sudo unzip sonarqube-10.4.1.88267.zip -d /opt
sudo mv /opt/sonarqube-10.4.1.88267 /opt/sonarqube
sudo useradd -r -s /bin/false sonarqube
sudo chown -R sonarqube:sonarqube /opt/sonarqube
sudo systemctl start sonarqube
```

> Requiert Java 17 (`sudo apt install openjdk-17-jdk`)

### Accès

- URL : `http://localhost:9000`
- Credentials par défaut : `admin` / `admin`

---

## Nexus

### Lancer via Docker

```bash
sudo docker run -d -p 8081:8081 --name nexus sonatype/nexus3
```

### Configuration

1. Accède à `http://localhost:8081`
2. Récupère le mot de passe admin :
   ```bash
   sudo docker exec nexus cat /nexus-data/admin.password
   ```
3. Crée un repo **pypi (proxy)** nommé `pypi-proxy` pointant sur `https://pypi.org/simple/`

---

## Ressources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
