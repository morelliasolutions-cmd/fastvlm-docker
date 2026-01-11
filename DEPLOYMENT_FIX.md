# 🔧 Fix de déploiement - Problème réseau app-net

## Problème courant : Réseau externe non trouvé

Si le déploiement échoue avec l'erreur :
```
network "app-net" not found
```
ou
```
Error response from daemon: network app-net not found
```

## 🔍 Diagnostic

### 1. Vérifier que le réseau existe (via SSH)

```bash
docker network ls | grep app-net
```

Si rien n'apparaît, le réseau n'existe pas.

### 2. Créer le réseau (via SSH)

```bash
docker network create app-net
```

### 3. Vérifier que le réseau existe

```bash
docker network inspect app-net
```

## ✅ Solutions

### Solution 1 : Créer le réseau manuellement (recommandé)

Si vous avez accès SSH au serveur :

1. Connectez-vous en SSH
2. Créez le réseau :
   ```bash
   docker network create app-net
   ```
3. Redéployez FastVLM dans Easypanel

### Solution 2 : Utiliser la version sans réseau externe (temporaire)

Si vous ne pouvez pas créer le réseau ou si Easypanel a des restrictions :

1. Dans Easypanel → Source
2. Utilisez le contenu de `docker-compose.test.yml` (sans `app-net`)
3. Déployez pour tester
4. **Note** : Dans ce cas, vous devrez connecter n8n au réseau interne d'Easypanel ou utiliser une autre méthode

### Solution 3 : Vérifier la configuration Easypanel

Easypanel peut avoir des restrictions sur les réseaux externes. Dans ce cas :
- Vérifiez la documentation Easypanel
- Ou utilisez le réseau interne automatique d'Easypanel (sans section `networks`)

## 📝 Fichiers disponibles

- **docker-compose.yml** : Avec réseau externe `app-net` (nécessite que le réseau existe)
- **docker-compose.test.yml** : Sans réseau externe (pour tester)
- **docker-compose.no-network.yml.example** : Exemple sans réseau

## 🎯 Prochaines étapes

1. **Si vous avez SSH** : Créez le réseau `app-net` avec `docker network create app-net`
2. **Si vous n'avez pas SSH** : Testez avec `docker-compose.test.yml` d'abord
3. **Une fois que FastVLM démarre** : On pourra reconnecter au réseau `app-net` manuellement si nécessaire
