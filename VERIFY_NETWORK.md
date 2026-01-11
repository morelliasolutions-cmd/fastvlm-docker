# 🔍 Vérification du réseau app-net

## Commandes pour vérifier la configuration réseau

### 1. Vérifier que le réseau `app-net` existe

```bash
docker network ls | grep app-net
```

Vous devriez voir quelque chose comme :
```
NETWORK ID     NAME      DRIVER    SCOPE
xxxxxxxxxxxxx  app-net   bridge    local
```

---

### 2. Vérifier que FastVLM est sur `app-net`

**Option A : Voir tous les conteneurs sur app-net**
```bash
docker network inspect app-net
```

Cela affichera tous les conteneurs connectés au réseau, avec leurs noms et IPs.

**Option B : Vérifier spécifiquement FastVLM**
```bash
docker network inspect app-net | grep -A 20 "fastvlm"
```

**Option C : Voir le conteneur FastVLM et ses réseaux**
```bash
docker ps | grep fastvlm
```

Notez le nom/ID du conteneur, puis :
```bash
docker inspect <container_id_ou_nom> | grep -A 10 "Networks"
```

---

### 3. Vérifier que n8n est sur `app-net`

```bash
docker network inspect app-net | grep -A 20 "n8n"
```

Ou pour voir tous les conteneurs :
```bash
docker network inspect app-net --format '{{range .Containers}}{{.Name}} {{end}}'
```

---

### 4. Trouver le nom exact du conteneur FastVLM

```bash
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}" | grep -i fastvlm
```

Cela affichera quelque chose comme :
```
NAMES           IMAGE                    STATUS
fastvlm-xxx     fastvlm-docker_fastvlm   Up X minutes
```

**Le nom du conteneur peut être différent de "fastvlm" !**
- Il peut être : `fastvlm-xxx`, `ollama_fastvlm`, `fastvlm-1.5b`, etc.
- Le nom dépend de la configuration Easypanel

---

### 5. Vérifier le nom du service dans docker-compose

Si vous avez accès au docker-compose.yml, vérifiez le nom du service :
```bash
# Si vous avez accès au fichier
cat docker-compose.yml | grep -A 2 "^services:"
cat docker-compose.yml | grep "^  " | head -5
```

Le nom du service dans `docker-compose.yml` est ce qui sera utilisé comme hostname (ici : `fastvlm`).

---

### 6. Tester la connectivité depuis n8n

**Depuis le conteneur n8n :**
```bash
# Trouver le conteneur n8n
docker ps | grep n8n

# Entrer dans le conteneur n8n
docker exec -it <container_id_n8n> sh

# Tester le ping vers FastVLM
ping fastvlm

# Ou tester avec curl (si disponible)
curl http://fastvlm:8000/health
```

**Depuis le serveur hôte (si FastVLM expose le port) :**
```bash
curl http://localhost:8000/health
```

---

### 7. Voir l'IP de FastVLM sur app-net

```bash
docker network inspect app-net --format '{{range .Containers}}{{.Name}}: {{.IPv4Address}}{{"\n"}}{{end}}' | grep fastvlm
```

Cela affichera l'IP de FastVLM sur le réseau app-net (par exemple : `172.18.0.5/16`).

**Note** : Vous pouvez utiliser cette IP directement, mais ce n'est pas recommandé car l'IP peut changer. Utilisez plutôt le nom du service (`fastvlm`).

---

### 8. Vérifier le nom du service vs nom du conteneur

**Dans Easypanel/Docker Compose :**
- Le **nom du service** (dans docker-compose.yml) est utilisé comme hostname DNS
- Ici : `fastvlm` (défini dans `services: fastvlm:`)
- C'est ce nom que vous utilisez dans l'URL : `http://fastvlm:8000`

**Le nom du conteneur** (visible dans `docker ps`) peut être différent :
- Il peut être préfixé par le projet (ex: `ollama_fastvlm_1`)
- Ou avoir un suffixe (ex: `fastvlm-abc123`)

Mais pour la communication réseau, utilisez toujours le **nom du service** (`fastvlm`).

---

## ✅ Checklist de vérification

1. [ ] Le réseau `app-net` existe : `docker network ls | grep app-net`
2. [ ] FastVLM est démarré : `docker ps | grep fastvlm`
3. [ ] FastVLM est sur `app-net` : `docker network inspect app-net | grep fastvlm`
4. [ ] n8n est sur `app-net` : `docker network inspect app-net | grep n8n`
5. [ ] Le nom du service est `fastvlm` dans docker-compose.yml
6. [ ] Test de ping depuis n8n : `docker exec n8n ping fastvlm` (doit fonctionner)
7. [ ] Test HTTP : `docker exec n8n curl http://fastvlm:8000/health` (doit retourner JSON)

---

## 🎯 Commandes rapides (copier-coller)

```bash
# 1. Vérifier app-net existe
docker network ls | grep app-net

# 2. Voir tous les conteneurs sur app-net
docker network inspect app-net --format '{{range .Containers}}{{.Name}} {{end}}'

# 3. Vérifier FastVLM spécifiquement
docker network inspect app-net | grep -A 5 "fastvlm"

# 4. Vérifier n8n
docker network inspect app-net | grep -A 5 "n8n"

# 5. Tester depuis n8n (remplacez <n8n_container> par le nom réel)
docker exec <n8n_container> ping -c 3 fastvlm

# 6. Tester HTTP (remplacez <n8n_container> par le nom réel)
docker exec <n8n_container> curl http://fastvlm:8000/health
```

---

## 🔧 Si FastVLM n'est pas sur app-net

Si après vérification, FastVLM n'est pas sur `app-net` :

1. **Redéployez FastVLM dans Easypanel** (avec le nouveau docker-compose.yml)
2. **Ou connectez manuellement** (si accès) :
   ```bash
   docker network connect app-net <fastvlm_container_id>
   ```

---

## 📝 Notes importantes

- **Utilisez le nom du service** (`fastvlm`) dans les URLs, pas le nom du conteneur
- Le nom du service est défini dans `docker-compose.yml` sous `services: fastvlm:`
- Si Easypanel a changé le nom, vérifiez dans les logs ou avec `docker network inspect app-net`
- Le port est `8000` (défini dans `docker-compose.yml` et `app.py`)
