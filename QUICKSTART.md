# 🚀 Démarrage rapide - FastVLM 1.5B sur Easypanel

## Étapes rapides (5 minutes)

### 1. Créer un dépôt Git (Option recommandée)

1. Créez un nouveau dépôt sur GitHub/GitLab
2. Poussez tous les fichiers de ce projet dans le dépôt
3. Notez l'URL de votre dépôt (ex: `https://github.com/votre-username/fastvlm-docker.git`)

### 2. Configurer dans Easypanel

1. Dans Easypanel → Projet "Ollama" → Service "fastvlm"
2. Onglet **"Source"** (<> Source dans le menu)
3. Sélectionnez **"Git"**
4. Remplissez :
   - **URL du répertoire** : Votre URL Git
   - **Branche** : `main`
   - **Chemin de construction** : `/`
   - **Fichier Docker Compose** : `docker-compose.yml`
5. Si dépôt privé : Cliquez "Générer une clé SSH" et ajoutez-la à votre dépôt
6. Cliquez **"Enregistrer"**

### 3. Déployer

1. Cliquez sur **"Déployer"** (bouton vert)
2. Attendez 5-10 minutes (téléchargement du modèle ~3-4GB)
3. Vérifiez les logs pour voir le progrès

### 4. Tester l'API

Une fois déployé, testez avec :

```bash
curl http://votre-serveur:8000/health
```

Ou visitez `http://votre-serveur:8000/docs` pour la documentation interactive de l'API.

## 📝 Utilisation avec n8n

Dans n8n, créez un workflow avec un nœud "HTTP Request" :

- **Method**: POST
- **URL**: 
  - `http://fastvlm:8000/generate` (si n8n est sur le même réseau Docker Easypanel)
  - OU utilisez le domaine configuré dans Easypanel (onglet "Domaines")
  - OU utilisez le réseau interne Docker d'Easypanel
- **Body** (JSON):
  ```json
  {
    "image": "data:image/png;base64,iVBORw0KG...",
    "prompt": "What is in this image? Describe it in detail.",
    "max_length": 512
  }
  ```

Voir `n8n_example.json` pour un workflow complet.

## ⚙️ Configuration rapide

### ⚡ Configuration CPU uniquement (Déjà configuré!)

Cette configuration est **déjà optimisée pour CPU uniquement**. Le `docker-compose.yml` utilise automatiquement `Dockerfile.cpu` qui est plus léger et optimisé pour les VPS sans GPU.

### Ajuster les ressources CPU/Mémoire

Dans `docker-compose.yml`, modifiez selon les ressources de votre VPS :

```yaml
deploy:
  resources:
    limits:
      memory: 6G  # Minimum 4G, recommandé 6G pour CPU
      cpus: '2.0'  # Ajustez selon vos CPUs disponibles
    reservations:
      memory: 4G
      cpus: '1.0'
```

**Recommandations CPU:**
- Minimum: 2 cores, 4GB RAM
- Recommandé: 4 cores, 6-8GB RAM pour de meilleures performances

## 🐛 Problèmes courants

**Le modèle ne charge pas ?**
- Vérifiez l'espace disque (besoin de ~5GB)
- Vérifiez les logs dans Easypanel
- Attendez 10 minutes pour le premier téléchargement

**Erreur "Out of Memory" ?**
- Utilisez `Dockerfile.cpu` (plus léger)
- Réduisez la mémoire allouée dans docker-compose.yml
- Réduisez `max_length` dans vos requêtes

**L'API ne répond pas ?**
- Vérifiez que le port 8000 est exposé
- Vérifiez le healthcheck : `curl http://localhost:8000/health`
- Le modèle prend ~30-60 secondes à charger après le démarrage du conteneur (CPU)
- Le premier téléchargement du modèle (~3-4GB) peut prendre 5-10 minutes selon votre connexion

**Performance lente sur CPU ?**
- C'est normal ! Sur CPU, une génération prend 5-15 secondes
- Réduisez `max_length` à 256 pour des réponses plus rapides
- Utilisez des prompts plus courts et spécifiques

## 📚 Documentation complète

- Voir `README.md` pour la documentation complète
- Voir `EASYPANEL_DEPLOY.md` pour le guide détaillé de déploiement
- API docs : `http://votre-serveur:8000/docs`

## ✅ Checklist

- [ ] Dépôt Git créé et fichiers poussés
- [ ] Service configuré dans Easypanel
- [ ] Déploiement lancé
- [ ] Health check réussi (`/health`)
- [ ] API testée avec curl ou n8n
- [ ] Workflow n8n configuré

**C'est tout ! Votre FastVLM 1.5B est prêt à analyser des images via n8n 🎉**
