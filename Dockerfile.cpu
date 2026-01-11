# Dockerfile pour FastVLM 1.5B API Server (CPU uniquement)
# Version optimisée pour les VPS sans GPU
FROM python:3.10-slim

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de requirements
COPY requirements.txt .

# Installer les dépendances Python
# PyTorch CPU version (plus léger que la version avec CUDA)
# Note: On installe PyTorch CPU d'abord, puis les autres dépendances
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch==2.1.0 torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir fastapi==0.104.1 uvicorn[standard]==0.24.0 pillow==10.1.0 transformers==4.35.0 accelerate==0.24.1 sentencepiece==0.1.99 protobuf==4.25.0 pydantic==2.5.0 python-multipart==0.0.6

# Copier le code de l'application
COPY app.py .

# Exposer le port
EXPOSE 8000

# Variable d'environnement pour le modèle
ENV MODEL_NAME=apple/FastVLM-1.5B
ENV PORT=8000

# Commande pour démarrer le serveur
CMD ["python", "app.py"]
