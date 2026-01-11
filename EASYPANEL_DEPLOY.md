# Guide de déploiement sur Easypanel

Ce guide vous explique comment déployer FastVLM 1.5B sur votre VPS via Easypanel.

## 📋 Prérequis

- Un VPS avec au moins 4-8GB de RAM
- Au moins 5GB d'espace disque libre
- Docker et Docker Compose installés sur le VPS (généralement déjà inclus avec Easypanel)

## 🚀 Option 1: Déploiement via Git Repository (Recommandé)

### Étape 1: Créer un dépôt Git

1. Créez un nouveau dépôt sur GitHub/GitLab (ou votre plateforme Git préférée)
2. Poussez tous les fichiers de ce projet dans le dépôt
3. Notez l'URL du dépôt (ex: `https://github.com/votre-username/fastvlm-docker.git`)

### Étape 2: Configurer dans Easypanel

1. Dans Easypanel, allez dans votre projet "Ollama"
2. Cliquez sur le service "fastvlm" (ou créez un nouveau service)
3. Allez dans l'onglet "Source" (<> Source)
4. Sélectionnez **"Git"**
5. Remplissez les champs :
   - **URL du répertoire** : `https://github.com/votre-username/fastvlm-docker.git`
   - **Branche** : `main` (ou `master` selon votre dépôt)
   - **Chemin de construction** : `/`
   - **Fichier Docker Compose** : `docker-compose.yml`
6. Si votre dépôt est **privé** :
   - Cliquez sur "Générer une clé SSH"
   - Copiez la clé publique générée
   - Ajoutez cette clé comme "Deploy Key" dans les paramètres de votre dépôt Git
7. Cliquez sur **"Enregistrer"**

### Étape 3: Déployer

1. Cliquez sur le bouton vert **"Déployer"**
2. Attendez que le build se termine (peut prendre 5-10 minutes pour télécharger le modèle)
3. Vérifiez les logs pour voir le progrès

## 🔧 Option 2: Déploiement via Docker Compose direct

Si vous préférez ne pas utiliser Git :

### Étape 1: Copier le contenu

1. Dans Easypanel, allez dans "Source"
2. Sélectionnez **"docker-compose.yml"**
3. Copiez tout le contenu du fichier `docker-compose.yml` de ce projet
4. Collez-le dans le champ prévu dans Easypanel
5. Cliquez sur **"Enregistrer"**

⚠️ **Note**: Avec cette méthode, vous devrez uploader manuellement les fichiers (Dockerfile, app.py, requirements.txt) via SSH ou une autre méthode.

## ⚙️ Configuration avancée

### Modifier la mémoire allouée

Dans `docker-compose.yml`, ajustez les limites de mémoire :

```yaml
deploy:
  resources:
    limits:
      memory: 8G  # Augmentez si vous avez plus de RAM
    reservations:
      memory: 4G  # RAM minimale requise
```

### Utiliser la version CPU uniquement

Si vous n'avez pas de GPU ou voulez réduire la taille de l'image :

1. Renommez `Dockerfile.cpu` en `Dockerfile`
2. Ou modifiez `docker-compose.yml` pour utiliser `Dockerfile.cpu` :

```yaml
build:
  context: .
  dockerfile: Dockerfile.cpu
```

### Variables d'environnement personnalisées

Dans Easypanel, vous pouvez ajouter des variables d'environnement :

- `MODEL_NAME` : Nom du modèle HuggingFace (défaut: `apple/FastVLM-1.5B`)
- `PORT` : Port du serveur (défaut: `8000`)

## 🔍 Vérification après déploiement

### 1. Vérifier les logs

Dans Easypanel, allez dans l'onglet "Logs" du service pour voir :
- Le téléchargement du modèle
- Le chargement du modèle en mémoire
- Le démarrage du serveur API

### 2. Tester l'API

Depuis n8n ou avec curl :

```bash
curl http://votre-serveur:8000/health
```

Vous devriez voir :
```json
{
  "status": "healthy",
  "model_loaded": true,
  "device": "cpu"
}
```

### 3. Tester la génération

```bash
curl -X POST http://votre-serveur:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "image": "data:image/png;base64,iVBORw0KG...",
    "prompt": "What is in this image?",
    "max_length": 256
  }'
```

## 🐛 Résolution de problèmes

### Le modèle ne charge pas

**Symptômes**: Logs montrent des erreurs lors du téléchargement du modèle

**Solutions**:
- Vérifiez l'espace disque (le modèle fait ~3-4GB)
- Vérifiez la connexion internet du VPS
- Augmentez le `start_period` du healthcheck dans docker-compose.yml

### Erreur "Out of Memory"

**Symptômes**: Le conteneur crash ou ne démarre pas

**Solutions**:
- Réduisez les limites de mémoire dans docker-compose.yml
- Utilisez la version CPU uniquement (Dockerfile.cpu)
- Réduisez `max_length` dans vos requêtes

### L'API ne répond pas

**Symptômes**: Timeout ou erreur 503

**Solutions**:
- Vérifiez que le port 8000 est bien exposé
- Vérifiez les logs du conteneur
- Augmentez le `start_period` du healthcheck (le modèle prend du temps à charger)

### Le modèle prend trop de temps à charger

**C'est normal!** Le modèle FastVLM-1.5B fait ~3-4GB et peut prendre 5-10 minutes à télécharger et charger la première fois. Les déploiements suivants seront plus rapides si le cache HuggingFace est préservé.

## 🔗 Intégration avec n8n

Une fois déployé, vous pouvez utiliser l'API depuis n8n :

1. Dans n8n, créez un workflow
2. Ajoutez un nœud "HTTP Request"
3. Configurez :
   - **Method**: POST
   - **URL**: `http://fastvlm:8000/generate` (si n8n est sur le même réseau Docker)
   - **URL externe**: `http://votre-ip-vps:8000/generate` (si n8n est ailleurs)
   - **Body**: JSON avec `image` (base64), `prompt`, et `max_length`

Voir `n8n_example.json` pour un exemple complet de workflow.

## 📚 Ressources

- [Documentation Easypanel](https://easypanel.io/docs)
- [Documentation FastVLM](https://huggingface.co/apple/FastVLM-1.5B)
- [Documentation n8n](https://docs.n8n.io/)
