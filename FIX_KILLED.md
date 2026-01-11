# 🔧 Fix "Killed" - Problème de mémoire

## ❌ Erreur : "Killed"

Cette erreur signifie que le conteneur a été tué par le système (OOM Killer - Out of Memory). Votre VPS n'a pas assez de mémoire disponible.

---

## 🔍 Causes possibles

1. **Mémoire insuffisante** : Le conteneur demande trop de RAM (6G dans la config actuelle)
2. **Build trop lourd** : Le build Docker consomme beaucoup de mémoire
3. **Modèle qui charge** : Le modèle FastVLM 1.5B nécessite ~4-5GB de RAM en fonctionnement

---

## ✅ Solutions

### Solution 1 : Réduire les limites de mémoire (RECOMMANDÉ)

J'ai créé `docker-compose.minimal.yml` avec des ressources réduites :

- Mémoire max : **4G** (au lieu de 6G)
- CPU max : **1.0** (au lieu de 2.0)
- Mémoire réservée : **2G** (au lieu de 4G)

**Utilisez cette version dans Easypanel** :

1. Dans Easypanel → Service fastvlm → Source
2. Copiez le contenu de `docker-compose.minimal.yml`
3. Remplacez le contenu actuel
4. Cliquez "Enregistrer" puis "Déployer"

### Solution 2 : Vérifier les ressources de votre VPS

**Vérifiez la RAM disponible** (si accès SSH) :

```bash
free -h
```

**Vérifiez la RAM utilisée** :

```bash
docker stats --no-stream
```

**Ressources minimales requises** :
- RAM : Au moins **4-5GB disponibles** (le modèle en a besoin)
- Swap : Recommandé d'avoir du swap activé

### Solution 3 : Activer/étendre le swap (si possible)

Si votre VPS a peu de RAM, activez le swap (si accès root) :

```bash
# Vérifier le swap actuel
swapon --show

# Créer un fichier swap de 4GB (si pas de swap)
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Rendre permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

⚠️ **Note** : Le swap ralentit les performances, mais permet d'éviter les "Killed".

### Solution 4 : Fermer d'autres services (temporaire)

Si vous avez d'autres conteneurs/services qui consomment beaucoup de RAM :
- Arrêtez-les temporairement pendant le build/déploiement
- Redémarrez-les après

### Solution 5 : Configurer des limites encore plus basses

Si 4G est encore trop, ajustez dans `docker-compose.yml` :

```yaml
deploy:
  resources:
    limits:
      memory: 3G  # Encore plus bas
      cpus: '1.0'
    reservations:
      memory: 2G
      cpus: '0.5'
```

⚠️ **Attention** : Le modèle FastVLM 1.5B nécessite au minimum **3-4GB de RAM** pour fonctionner. En dessous, il risque de ne pas démarrer correctement.

---

## 📊 Ressources recommandées

### Minimum absolu
- **RAM** : 4GB
- **Swap** : 2-4GB (recommandé)
- **CPU** : 1 core

### Recommandé
- **RAM** : 6-8GB
- **Swap** : 2-4GB
- **CPU** : 2-4 cores

### Optimal
- **RAM** : 8-16GB
- **Swap** : 4GB
- **CPU** : 4+ cores

---

## 🔍 Diagnostic

### Vérifier la mémoire disponible

```bash
# RAM totale et utilisée
free -h

# RAM utilisée par Docker
docker stats --no-stream

# Processus consommant le plus de RAM
ps aux --sort=-%mem | head -10
```

### Vérifier les logs du conteneur

Dans Easypanel, regardez les logs pour voir :
- À quel moment il a été tué
- S'il y a des messages d'erreur avant le "Killed"
- Si c'est pendant le build ou le runtime

---

## 💡 Conseils

1. **Build d'abord** : Le build peut consommer beaucoup de RAM temporairement
2. **Ensuite runtime** : Une fois construit, le runtime nécessite ~4-5GB
3. **Swap activé** : Aide pendant le chargement du modèle
4. **Limites progressives** : Commencez avec 4G, augmentez si ça fonctionne

---

## 🎯 Prochaines étapes

1. **Utilisez `docker-compose.minimal.yml`** (ressources réduites)
2. **Vérifiez les ressources de votre VPS** (`free -h`)
3. **Activez le swap si nécessaire**
4. **Redéployez avec les nouvelles limites**
5. **Si ça ne fonctionne toujours pas** : Vérifiez qu'il reste au moins 4GB de RAM disponible

---

## ⚠️ Si le problème persiste

Si même avec 4G de RAM le conteneur est tué :
- Vérifiez qu'il y a bien 4GB+ de RAM disponible sur le VPS
- Vérifiez qu'aucun autre processus ne consomme trop de RAM
- Activez le swap (aide temporairement)
- Considérez augmenter la RAM du VPS
