# FastVLM 1.5B Docker Deployment

Déploiement de FastVLM 1.5B avec une API HTTP pour Easypanel et n8n.

## 🚀 Fonctionnalités

- API REST avec FastAPI
- Accepte des images encodées en base64
- **Optimisé pour CPU uniquement** (parfait pour VPS sans GPU)
- Documentation automatique de l'API (Swagger UI)
- Health check endpoint

## 📋 Prérequis

- Docker et Docker Compose installés
- **Au moins 4-6GB de RAM disponible** (CPU uniquement)
- Espace disque: ~5GB pour le modèle et dépendances
- **CPU avec au moins 2 cores recommandés**

## 🐳 Déploiement sur Easypanel

### Option 1: Via Docker Compose (Recommandé)

1. Dans Easypanel, sur la page Source du service:
   - Sélectionnez "docker-compose.yml"
   - Copiez le contenu de `docker-compose.yml` dans le champ prévu
   - OU cliquez sur "Git" et entrez:
     - **URL du répertoire**: URL de votre dépôt Git (si vous poussez ce code sur Git)
     - **Branche**: `main` ou `master`
     - **Chemin de construction**: `/`
     - **Fichier Docker Compose**: `docker-compose.yml`

2. Cliquez sur "Enregistrer" puis "Déployer"

### Option 2: Via Git Repository

1. Créez un dépôt Git avec ce code
2. Dans Easypanel, sélectionnez "Git"
3. Configurez:
   - **URL du répertoire**: `https://github.com/votre-username/fastvlm-docker.git`
   - **Branche**: `main`
   - **Chemin de construction**: `/`
   - **Fichier Docker Compose**: `docker-compose.yml`
4. Si le dépôt est privé, générez une clé SSH dans Easypanel et ajoutez-la à votre dépôt Git

## 🔌 API Endpoints

### Health Check
```http
GET /health
```

### Générer une réponse
```http
POST /generate
Content-Type: application/json

{
  "image": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "prompt": "What is in this image? Describe it in detail.",
  "max_length": 512
}
```

### Chat (alias pour /generate)
```http
POST /chat
Content-Type: application/json

{
  "image": "base64_encoded_image_string",
  "prompt": "What do you see?",
  "max_length": 256
}
```

### Documentation interactive
```
GET /docs
```

## 📝 Utilisation avec n8n

### 1. Configuration HTTP Request

Dans n8n, créez un workflow avec:

1. **Nœud "Read Binary File"** ou **"HTTP Request"** (pour récupérer l'image)
2. **Nœud "Function"** pour convertir en base64:
   ```javascript
   const binaryData = $input.item.binary.data;
   const base64 = binaryData.toString('base64');
   const dataUri = `data:image/png;base64,${base64}`;
   
   return {
     json: {
       image: dataUri,
       prompt: "What is in this image? Describe it in detail.",
       max_length: 512
     }
   };
   ```

3. **Nœud "HTTP Request"** pour appeler FastVLM:
   - **Method**: POST
   - **URL**: `http://fastvlm:8000/generate` (ou l'URL externe si n8n est sur un autre serveur)
   - **Authentication**: None (ou ajoutez une authentification si nécessaire)
   - **Body Content Type**: JSON
   - **Body**: Utilisez la sortie du nœud Function

4. **Nœud "Set"** pour traiter la réponse:
   ```javascript
   return {
     json: {
       description: $json.response
     }
   };
   ```

### 2. Exemple de requête complète

```json
{
  "image": "data:image/png;base64,iVBORw0KGgoAAAANS...",
  "prompt": "Analyze this image and describe what you see. Be specific and detailed.",
  "max_length": 512
}
```

### Réponse attendue:
```json
{
  "response": "I can see a beautiful landscape with mountains...",
  "model": "FastVLM-1.5B"
}
```

## 🔧 Configuration

### Variables d'environnement

- `MODEL_NAME`: Nom du modèle HuggingFace (défaut: `apple/FastVLM-1.5B`)
- `PORT`: Port du serveur (défaut: `8000`)
- `TORCH_DEVICE`: Device PyTorch (défaut: `cpu` - optimisé pour CPU uniquement)

### Configuration CPU uniquement

Cette configuration est **optimisée pour CPU uniquement** par défaut. Le `docker-compose.yml` utilise `Dockerfile.cpu` qui installe PyTorch CPU (plus léger, ~500MB au lieu de ~2GB).

**Performance CPU:**
- Chargement du modèle: ~30-60 secondes
- Génération de réponse: ~5-15 secondes selon la longueur
- Mémoire utilisée: ~4-5GB en fonctionnement

Pour améliorer les performances sur CPU:
- Augmentez `cpus` dans `docker-compose.yml`
- Réduisez `max_length` dans vos requêtes (256 au lieu de 512)

## 🐛 Dépannage

### Le modèle ne charge pas
- Vérifiez les logs: `docker logs fastvlm-1.5b`
- Vérifiez l'espace disque (le modèle fait ~3GB)
- Vérifiez la mémoire disponible (au moins 4GB recommandé)

### Erreur "Out of Memory" (CPU)
- Réduisez `max_length` dans vos requêtes (essayez 256 au lieu de 512)
- Réduisez les limites de mémoire dans `docker-compose.yml` (minimum 4GB requis)
- Assurez-vous qu'aucun autre processus lourd ne tourne sur le VPS

### L'API ne répond pas
- Vérifiez que le port 8000 est exposé
- Vérifiez le health check: `curl http://localhost:8000/health`
- Consultez les logs du conteneur

## 📚 Documentation

- **Guide de performance CPU** : Voir `CPU_PERFORMANCE.md` pour optimiser les performances sur CPU
- [FastVLM sur HuggingFace](https://huggingface.co/apple/FastVLM-1.5B)
- [Documentation FastAPI](https://fastapi.tiangolo.com/)
- [Documentation n8n](https://docs.n8n.io/)

## 📄 Licence

Ce projet est fourni tel quel pour faciliter le déploiement de FastVLM. Le modèle FastVLM est développé par Apple.
