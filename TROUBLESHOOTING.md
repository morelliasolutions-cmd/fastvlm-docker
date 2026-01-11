# 🔧 Dépannage - Communication n8n et FastVLM

## ❌ Erreur : `getaddrinfo ENOTFOUND fastvlm`

Cette erreur signifie que n8n ne peut pas résoudre le nom d'hôte `fastvlm`. Les conteneurs ne sont pas sur le même réseau Docker.

---

## 🔍 Vérifications à faire

### 1. Vérifier que FastVLM est démarré

Dans Easypanel ou via SSH :

```bash
docker ps | grep fastvlm
```

Vous devriez voir le conteneur FastVLM en cours d'exécution.

### 2. Vérifier que le réseau `app-net` existe

```bash
docker network ls | grep app-net
```

Vous devriez voir `app-net` dans la liste.

### 3. Vérifier que FastVLM est sur le réseau `app-net`

```bash
docker inspect <container_id_fastvlm> | grep -A 10 "Networks"
```

Ou :

```bash
docker network inspect app-net
```

Vous devriez voir FastVLM dans la liste des conteneurs connectés au réseau `app-net`.

### 4. Vérifier que n8n est sur le réseau `app-net`

```bash
docker inspect <container_id_n8n> | grep -A 10 "Networks"
```

Ou :

```bash
docker network inspect app-net
```

Vous devriez voir n8n dans la liste des conteneurs connectés au réseau `app-net`.

---

## 🔧 Solutions

### Solution 1 : Vérifier le déploiement FastVLM dans Easypanel

1. Dans Easypanel → Service fastvlm
2. Vérifiez que le service est bien déployé et démarré
3. Vérifiez les logs pour voir s'il y a des erreurs

### Solution 2 : Vérifier que le réseau `app-net` est bien configuré

Assurez-vous que le `docker-compose.yml` de FastVLM contient :

```yaml
services:
  fastvlm:
    # ... autres configurations ...
    networks:
      - app-net

networks:
  app-net:
    external: true
```

### Solution 3 : Reconnecter FastVLM au réseau `app-net` (si déjà déployé)

Si FastVLM est déjà déployé mais pas sur le bon réseau :

**Option A : Via Easypanel**
1. Redéployez le service fastvlm (il devrait utiliser la nouvelle configuration avec `app-net`)

**Option B : Via SSH (si accès)**
```bash
# Arrêter le conteneur FastVLM
docker stop <container_id_fastvlm>

# Retirer du réseau actuel (si nécessaire)
docker network disconnect bridge <container_id_fastvlm>

# Connecter au réseau app-net
docker network connect app-net <container_id_fastvlm>

# Redémarrer
docker start <container_id_fastvlm>
```

**Option C : Redéployer avec docker-compose (si accès SSH)**
```bash
cd /chemin/vers/fastvlm
docker-compose down
docker-compose up -d
```

### Solution 4 : Vérifier que n8n est sur `app-net`

Si n8n n'est pas sur `app-net`, vous devez l'y connecter aussi :

**Si n8n est déployé via Easypanel :**
- Vérifiez la configuration docker-compose de n8n
- Assurez-vous qu'il utilise aussi `app-net` :

```yaml
services:
  n8n:
    # ... autres configurations ...
    networks:
      - app-net

networks:
  app-net:
    external: true
```

**Si n8n est déployé manuellement :**
```bash
docker network connect app-net <container_id_n8n>
```

### Solution 5 : Tester la connexion depuis n8n

Une fois que les deux services sont sur `app-net`, testez depuis n8n :

**Via SSH (si accès) :**
```bash
docker exec <container_id_n8n> ping -c 3 fastvlm
```

**Via n8n :**
- Créez un workflow avec un nœud "HTTP Request"
- Method: `GET`
- URL: `http://fastvlm:8000/health`
- Si ça fonctionne, vous devriez recevoir une réponse JSON

---

## 🎯 Test de connectivité complet

### 1. Test depuis n8n vers FastVLM

Dans n8n, créez un workflow simple :
- Nœud "HTTP Request"
- Method: `GET`
- URL: `http://fastvlm:8000/health`
- Si ça fonctionne, vous devriez voir :
  ```json
  {
    "status": "healthy",
    "model_loaded": true,
    "device": "cpu"
  }
  ```

### 2. Test avec ping (si accès SSH)

Depuis le conteneur n8n :
```bash
docker exec -it <container_id_n8n> ping fastvlm
```

Vous devriez voir des réponses pings. Si `ping: fastvlm: Name or service not known`, les conteneurs ne sont pas sur le même réseau.

---

## 🚨 Problèmes courants

### FastVLM n'est pas démarré

**Symptôme** : `ENOTFOUND` ou timeout

**Solution** : Vérifiez dans Easypanel que FastVLM est bien démarré et qu'il n'y a pas d'erreurs dans les logs.

### Le réseau `app-net` n'existe pas

**Symptôme** : Erreur lors du déploiement ou `network not found`

**Solution** : Créez le réseau :
```bash
docker network create app-net
```

### FastVLM n'est pas sur `app-net`

**Symptôme** : FastVLM tourne mais n8n ne peut pas le joindre

**Solution** : Redéployez FastVLM avec la configuration mise à jour (avec `networks: app-net`).

### n8n n'est pas sur `app-net`

**Symptôme** : n8n ne peut pas résoudre `fastvlm`

**Solution** : Connectez n8n au réseau `app-net` (voir Solution 4 ci-dessus).

### Le nom du service est incorrect

**Symptôme** : `ENOTFOUND` mais le réseau est correct

**Solution** : Vérifiez que le nom du service dans `docker-compose.yml` est bien `fastvlm` (pas `fastvlm-1.5b` ou autre).

---

## ✅ Checklist de vérification

- [ ] FastVLM est démarré (visible dans `docker ps`)
- [ ] Le réseau `app-net` existe (`docker network ls`)
- [ ] FastVLM est connecté à `app-net` (`docker network inspect app-net`)
- [ ] n8n est connecté à `app-net` (`docker network inspect app-net`)
- [ ] Le `docker-compose.yml` de FastVLM contient `networks: app-net`
- [ ] Le `docker-compose.yml` de FastVLM contient la section `networks: app-net: external: true`
- [ ] Test de ping depuis n8n fonctionne (`docker exec n8n ping fastvlm`)
- [ ] Test HTTP depuis n8n fonctionne (`http://fastvlm:8000/health`)

---

## 💡 Alternative : Utiliser l'IP du conteneur

Si vous ne pouvez pas utiliser le réseau `app-net`, vous pouvez utiliser l'IP du conteneur FastVLM (mais ce n'est pas recommandé car l'IP peut changer) :

1. Récupérez l'IP de FastVLM :
   ```bash
   docker inspect <container_id_fastvlm> | grep IPAddress
   ```

2. Utilisez cette IP dans n8n :
   ```
   http://172.x.x.x:8000/generate
   ```

⚠️ **Note** : Cette méthode n'est pas recommandée car l'IP peut changer. Préférez l'utilisation du réseau Docker.

---

## 📞 Si le problème persiste

1. Vérifiez les logs de FastVLM dans Easypanel
2. Vérifiez les logs de n8n
3. Vérifiez que tous les services sont sur le même réseau `app-net`
4. Testez avec `docker exec` depuis les conteneurs
5. Vérifiez que le nom du service est bien `fastvlm` dans docker-compose.yml
