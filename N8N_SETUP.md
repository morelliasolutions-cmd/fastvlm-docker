# 📋 Guide de configuration n8n pour FastVLM

## 🔍 URL de l'API FastVLM

**L'URL que vous avez mentionnée** (`http://78.47.97.137:3000/api/compose/deploy/...`) est un endpoint de déploiement Easypanel, **pas l'API FastVLM**.

L'API FastVLM sera accessible sur :
- **Port interne Docker** : `http://fastvlm:8000` (si n8n est sur le même réseau Docker Easypanel)
- **Via domaine** : Si vous configurez un domaine dans Easypanel (onglet "Domaines")
- **Via IP publique** : `http://78.47.97.137:XXXX` (vous devrez configurer le port dans Easypanel)

## ⚡ FastVLM est SYNCHRONE (pas asynchrone)

**Important** : FastVLM est une API **synchrone** - elle attend la réponse avant de retourner le résultat. Le temps de réponse est de **5-15 secondes** sur CPU.

⚠️ **Dans n8n, configurez un timeout suffisant** (30-60 secondes) pour la requête HTTP.

---

## 🚀 Configuration n8n - Workflow complet

### Étape 1 : Récupérer l'image

**Option A : Depuis une URL**
- Ajoutez un nœud **"HTTP Request"**
- Method: `GET`
- URL: L'URL de votre image
- Options → Response Format: `File`

**Option B : Depuis un fichier local**
- Ajoutez un nœud **"Read Binary File"**
- File Path: Le chemin vers votre image

**Option C : Depuis un webhook (image upload)**
- Ajoutez un nœud **"Webhook"**
- Il recevra l'image en binaire

---

### Étape 2 : Convertir l'image en base64

Ajoutez un nœud **"Code"** avec ce code JavaScript :

```javascript
// Récupérer les données binaires de l'image
const binaryData = $input.item.binary.data.data;

// Convertir en base64
const base64 = Buffer.from(binaryData).toString('base64');

// Créer le data URI (format attendu par FastVLM)
const dataUri = `data:image/png;base64,${base64}`;

// Retourner les données pour FastVLM
return {
  json: {
    image: dataUri,
    prompt: "What is in this image? Describe it in detail. Be specific about objects, colors, and actions.",
    max_length: 256  // Réduire pour CPU (plus rapide)
  }
};
```

**Note** : Si vous voulez personnaliser le prompt, remplacez la chaîne dans `prompt:`.

---

### Étape 3 : Appeler l'API FastVLM

Ajoutez un nœud **"HTTP Request"** avec cette configuration :

#### Configuration de base :

- **Method** : `POST`
- **URL** : 
  - Si n8n est sur le même réseau Docker : `http://fastvlm:8000/generate`
  - Si n8n est externe : `http://78.47.97.137:XXXX/generate` (remplacez XXXX par le port configuré dans Easypanel)
  - Si vous avez configuré un domaine : `https://votre-domaine.com/generate`

- **Authentication** : `None` (ou ajoutez une authentification si vous l'avez configurée)

- **Send Body** : ✅ Oui

- **Content Type** : `JSON`

- **Body** : Sélectionnez "Specify Body" et utilisez cette structure :

```json
{
  "image": "={{ $json.image }}",
  "prompt": "={{ $json.prompt }}",
  "max_length": "={{ $json.max_length }}"
}
```

#### Options importantes :

Dans **Options** → **Timeout** :
- Définissez **Timeout** : `60000` (60 secondes)
- C'est important car FastVLM prend 5-15 secondes sur CPU !

Dans **Options** → **Response** :
- Response Format : `JSON`

---

### Étape 4 : Extraire la réponse

Ajoutez un nœud **"Set"** pour extraire la réponse :

1. Cliquez sur "Add Value"
2. Nom : `description`
3. Value : `={{ $json.response }}`

Optionnellement, ajoutez aussi :
- Nom : `model`
- Value : `={{ $json.model }}`

---

## 📝 Configuration rapide (Workflow minimal)

Si vous voulez un workflow minimal avec seulement 2 nœuds :

### Nœud 1 : Code (Convertir + Appeler)

```javascript
// 1. Récupérer l'image binaire
const binaryData = $input.item.binary.data.data;
const base64 = Buffer.from(binaryData).toString('base64');
const dataUri = `data:image/png;base64,${base64}`;

// 2. Préparer la requête
const requestBody = {
  image: dataUri,
  prompt: "What is in this image? Describe it in detail.",
  max_length: 256
};

// 3. Appeler FastVLM (nécessite un nœud HTTP Request séparé)
// Retourner les données pour le nœud HTTP Request suivant
return {
  json: requestBody
};
```

### Nœud 2 : HTTP Request

- Method: `POST`
- URL: `http://fastvlm:8000/generate` (ou votre URL)
- Body: JSON avec `={{ $json }}`
- Timeout: 60000

---

## 🔧 URL selon votre configuration

### Si n8n est sur Easypanel (même réseau Docker)

**Option A : Via réseau externe "app-net" (si vous avez créé ce réseau)**
```
http://fastvlm:8000/generate
```
Le `docker-compose.yml` est configuré pour utiliser le réseau externe `app-net` que vous avez créé pour Ollama.

**Option B : Via réseau interne Easypanel (si n8n est aussi sur Easypanel)**
```
http://fastvlm:8000/generate
```
Si n8n est sur Easypanel (même projet ou réseau interne), Easypanel gère automatiquement le réseau Docker. Dans ce cas, retirez la section `networks` du `docker-compose.yml`.

**Note** : Si vous avez créé un réseau externe `app-net` pour Ollama et n8n, utilisez la configuration actuelle (avec `networks: app-net`).

---

### Si n8n est externe (autre serveur/IP)

**Option 1 : Via domaine Easypanel**
1. Dans Easypanel → Service fastvlm → Onglet "Domaines"
2. Ajoutez un domaine (ex: `fastvlm.votredomaine.com`)
3. URL dans n8n : `https://fastvlm.votredomaine.com/generate`

**Option 2 : Via IP + Port**
1. Dans Easypanel, vous devrez configurer l'exposition du port
2. URL dans n8n : `http://78.47.97.137:8000/generate` (si le port 8000 est exposé)

⚠️ **Note** : L'IP `78.47.97.137` semble être votre VPS, mais le port `3000` dans votre URL est pour Easypanel, pas pour FastVLM.

---

## ✅ Test du workflow

### 1. Test de santé (optionnel)

Ajoutez un nœud **"HTTP Request"** au début avec :
- Method: `GET`
- URL: `http://fastvlm:8000/health`

Cela vérifiera que FastVLM est bien démarré.

### 2. Test avec une image simple

1. Utilisez un nœud "HTTP Request" pour télécharger une image
2. Suivez les étapes ci-dessus
3. Vérifiez que vous obtenez une réponse JSON avec `response` et `model`

---

## 📊 Exemple de réponse FastVLM

```json
{
  "response": "I can see a beautiful landscape with mountains in the background, a lake in the foreground, and trees surrounding the area. The sky is blue with white clouds.",
  "model": "FastVLM-1.5B"
}
```

---

## ⚠️ Problèmes courants

### Timeout dans n8n

**Symptôme** : Le workflow timeout avant d'obtenir une réponse

**Solution** :
- Augmentez le timeout dans n8n HTTP Request à 60-90 secondes
- Réduisez `max_length` à 128-256 pour des réponses plus rapides

### Erreur "Connection refused"

**Symptôme** : n8n ne peut pas se connecter à FastVLM

**Solution** :
- Vérifiez que FastVLM est bien démarré (testez `/health`)
- Vérifiez l'URL (utilisez `http://fastvlm:8000` si n8n est sur Easypanel)
- Si n8n est externe, configurez un domaine dans Easypanel

### Erreur "Invalid image"

**Symptôme** : L'API retourne une erreur de décodage d'image

**Solution** :
- Vérifiez que l'image est bien en format binaire avant la conversion base64
- Vérifiez que le data URI commence par `data:image/...`
- Assurez-vous que l'image n'est pas corrompue

### Réponse vide ou incomplète

**Symptôme** : La réponse est vide ou tronquée

**Solution** :
- Augmentez `max_length` à 512 ou plus
- Vérifiez les logs de FastVLM pour voir les erreurs
- Utilisez un prompt plus spécifique

---

## 🚀 Performance CPU

Sur CPU, attendez-vous à :
- **Temps de réponse** : 5-15 secondes
- **Pour `max_length=256`** : ~5-10 secondes
- **Pour `max_length=512`** : ~10-15 secondes

Configurez un timeout suffisant dans n8n (60 secondes recommandé).

---

## 📚 Ressources

- API FastVLM docs : Une fois déployé, visitez `http://fastvlm:8000/docs` pour la documentation interactive
- Health check : `http://fastvlm:8000/health`
- Test : `http://fastvlm:8000/` (page d'accueil avec endpoints)

---

## 💡 Conseils

1. **Cache les résultats** : Si vous analysez les mêmes images plusieurs fois, stockez les résultats dans une base de données
2. **Queue pour plusieurs images** : Pour traiter plusieurs images, utilisez une queue (RabbitMQ, Redis) ou ajoutez des délais entre les requêtes
3. **Prompts spécifiques** : Des prompts plus courts et spécifiques donnent de meilleures réponses et sont plus rapides
4. **Timeout suffisant** : Toujours configurer 60+ secondes de timeout dans n8n
