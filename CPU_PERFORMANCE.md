# ⚡ Guide de performance CPU - FastVLM 1.5B

## Configuration actuelle

Cette configuration est **optimisée pour CPU uniquement** avec les optimisations suivantes :

✅ PyTorch CPU-only (plus léger, ~500MB au lieu de ~2GB)  
✅ Float32 pour compatibilité CPU  
✅ `low_cpu_mem_usage=True` pour économiser la mémoire  
✅ Beam search désactivé (num_beams=1) pour la vitesse  
✅ Optimisations de génération adaptées au CPU  

## Performances attendues

### Chargement initial
- **Téléchargement du modèle** : 5-10 minutes (première fois, ~3-4GB)
- **Chargement en mémoire** : 30-60 secondes
- **Mémoire utilisée** : ~4-5GB

### Génération de réponses
- **Prompt court** (50 tokens) : 3-8 secondes
- **Prompt moyen** (100 tokens) : 5-12 secondes  
- **Prompt long** (512 tokens max) : 10-20 secondes
- **Max length 256** : 5-10 secondes (recommandé pour CPU)

## Optimisations recommandées

### 1. Réduire max_length
```json
{
  "image": "base64...",
  "prompt": "What is in this image?",
  "max_length": 256  // Au lieu de 512
}
```

### 2. Prompts plus courts et spécifiques
**❌ Évitez:**
```
"Analyze this image in great detail, describe everything you see including colors, objects, people, actions, environment, mood, and provide a comprehensive analysis."
```

**✅ Préférez:**
```
"What objects are in this image?"
"Describe the main subject in this image."
"What is happening in this image?"
```

### 3. Ressources VPS recommandées

**Minimum:**
- 2 CPU cores
- 4GB RAM
- 10GB espace disque

**Recommandé:**
- 4 CPU cores
- 6-8GB RAM
- 15GB espace disque

**Optimal:**
- 8+ CPU cores
- 8-16GB RAM
- 20GB+ espace disque

### 4. Configuration docker-compose.yml

Pour un VPS avec 4 cores et 8GB RAM :

```yaml
deploy:
  resources:
    limits:
      memory: 8G
      cpus: '4.0'
    reservations:
      memory: 6G
      cpus: '2.0'
```

Pour un VPS avec 2 cores et 4GB RAM (minimum) :

```yaml
deploy:
  resources:
    limits:
      memory: 4G
      cpus: '2.0'
    reservations:
      memory: 3G
      cpus: '1.0'
```

## Comparaison des temps de réponse

| Configuration | Max Length | Temps moyen |
|--------------|------------|-------------|
| CPU 2 cores | 256 | 8-12 sec |
| CPU 2 cores | 512 | 15-25 sec |
| CPU 4 cores | 256 | 5-8 sec |
| CPU 4 cores | 512 | 10-15 sec |
| CPU 8 cores | 256 | 3-5 sec |
| CPU 8 cores | 512 | 8-12 sec |

## Monitoring

### Vérifier les ressources utilisées

Dans Easypanel, allez dans l'onglet "Monitor" ou utilisez :

```bash
docker stats fastvlm-1.5b
```

### Logs de performance

Les logs montreront :
- Temps de chargement du modèle
- Device utilisé (devrait être "cpu")
- Utilisation mémoire

## Conseils pour n8n

### Timeout des requêtes HTTP

Dans n8n, configurez un timeout suffisant :
- **Timeout recommandé** : 30-60 secondes
- Pour max_length=256 : 20-30 secondes
- Pour max_length=512 : 30-60 secondes

### Traitement asynchrone

Pour traiter plusieurs images :
1. Utilisez des nœuds "Wait" entre les requêtes
2. Ou implémentez un système de queue (RabbitMQ, Redis)
3. Limitez les requêtes concurrentes à 1-2 maximum

### Cache des résultats

Si vous analysez les mêmes images plusieurs fois :
- Enregistrez les résultats dans une base de données
- Utilisez un hash de l'image comme clé
- Évitez de re-traiter les mêmes images

## Dépannage performance

### Le modèle est trop lent
- ✅ Réduisez `max_length` à 128-256
- ✅ Simplifiez vos prompts
- ✅ Augmentez les CPUs alloués
- ✅ Vérifiez qu'aucun autre processus ne consomme la CPU

### Mémoire insuffisante
- ✅ Réduisez `max_length`
- ✅ Limitez les requêtes concurrentes
- ✅ Redémarrez le conteneur périodiquement
- ✅ Vérifiez avec `docker stats`

### Réponses incomplètes
- ✅ Augmentez `max_length` (mais attention à la vitesse)
- ✅ Utilisez des prompts plus directs
- ✅ Vérifiez que le timeout n8n est suffisant

## Conclusion

FastVLM 1.5B sur CPU est **parfaitement utilisable** pour des workflows automatisés avec n8n. Les temps de réponse de 5-15 secondes sont acceptables pour la plupart des cas d'usage automatisés.

**Astuce finale** : Utilisez `max_length=256` par défaut pour un bon équilibre vitesse/qualité sur CPU.
