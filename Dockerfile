#Utilisation de l'image Python slim

FROM python:3.11-slim

# Définition du répertoire de travail
WORKDIR /app

# Installation des dépendances système nécessaires à la compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copie du fichier de dépendances Python et installation via pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copie du code applicatif
COPY app ./app
COPY s2c ./s2c

# Copie du bundle de certificats personnalisés
COPY ca-bundle.crt /etc/ssl/certs/ca-bundle.crt

# Variables d'environnement
ENV PYTHONPATH=/app
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-bundle.crt

# Lancement de l'application avec uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]