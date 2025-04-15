# fastapi
fastapi backend for parkigo

# file structure
fastapi/
├── app/
│   ├── __init__.py
│   ├── main.py          # Point d'entrée principal de l'application
│   ├── api/             # Dossier pour les routes de l'API
│   │   ├── __init__.py
│   │   └── endpoints/   # Sous-dossier pour organiser les endpoints
│   │       ├── __init__.py
│   │       └── users.py # Exemple de fichier pour les endpoints liés aux utilisateurs
│   ├── core/            # Configuration et dépendances
│   │   ├── __init__.py
│   │   └── config.py    # Fichier de configuration
│   ├── models/          # Modèles SQLAlchemy
│   │   ├── __init__.py
│   │   └── user.py      # Exemple de modèle utilisateur
│   ├── schemas/         # Schémas Pydantic
│   │   ├── __init__.py
│   │   └── user.py      # Exemple de schéma utilisateur
│   └── crud/            # Opérations CRUD
│       ├── __init__.py
│       └── user.py      # Exemple de fichier CRUD pour les utilisateurs
├── requirements.txt     # Dépendances du projet
└── README.md            # Documentation du projet






    app/api/endpoints/
        users.py : Contient les endpoints liés aux utilisateurs.
        Vous pouvez ajouter d'autres fichiers ici pour les endpoints relatifs aux customers, invoices, et revenue.

    app/core/
        config.py : Contient les configurations de l'application, comme l'URL de la base de données.
        database.py : Gère la connexion à la base de données et la session SQLAlchemy.

    app/crud/
        user.py : Contient les opérations CRUD pour les utilisateurs.
        Vous pouvez ajouter d'autres fichiers ici pour les opérations CRUD des autres modèles.

    app/models/
        customer.py : Modèle SQLAlchemy pour les clients.
        invoice.py : Modèle SQLAlchemy pour les factures.
        revenue.py : Modèle SQLAlchemy pour les revenus.
        user.py : Modèle SQLAlchemy pour les utilisateurs.

    app/schemas/
        customer.py : Schémas Pydantic pour les clients.
        invoice.py : Schémas Pydantic pour les factures.
        revenue.py : Schémas Pydantic pour les revenus.
        user.py : Schémas Pydantic pour les utilisateurs.

    app/main.py
        Point d'entrée principal de l'application FastAPI.
