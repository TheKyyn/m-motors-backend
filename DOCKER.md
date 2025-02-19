# M-Motors API - Guide d'installation

Bienvenue ! Ce guide vous aidera à installer l'API M-Motors sur votre ordinateur. Cette API permet de gérer un service de location et vente de véhicules.

## Prérequis

Avant de commencer, assurez-vous d'avoir :

1. Docker installé sur votre ordinateur

   - Pour Windows : Téléchargez "Docker Desktop" sur [docker.com](https://www.docker.com/products/docker-desktop)
   - Pour Mac : Téléchargez "Docker Desktop" sur [docker.com](https://www.docker.com/products/docker-desktop)
   - Pour Linux : Suivez le guide d'installation sur [docs.docker.com](https://docs.docker.com/engine/install/)

2. Les clés AWS de l'équipe
   - AWS_ACCESS_KEY_ID
   - AWS_SECRET_ACCESS_KEY
     Si vous ne les avez pas, demandez-les à l'équipe !

## Installation pas à pas

### Méthode 1 : Installation automatique (Recommandée pour les débutants)

1. Ouvrez votre terminal :

   - Windows : Cherchez "PowerShell" dans le menu démarrer
   - Mac : Cherchez "Terminal" dans Spotlight (Cmd + Espace)
   - Linux : Ctrl + Alt + T

2. Téléchargez notre script d'installation. Copiez et collez cette commande :

```bash
curl -O https://raw.githubusercontent.com/TheKyyn/m-motors-backend/main/install-api.sh
```

3. Rendez le script exécutable. Copiez et collez :

```bash
chmod +x install-api.sh
```

4. Lancez le script :

```bash
./install-api.sh
```

5. Le script va créer un fichier `.env`. Il vous demandera d'y ajouter vos clés AWS.
   - Quand il vous le demande, tapez `nano .env`
   - Remplacez `<votre_aws_key>` par votre AWS_ACCESS_KEY_ID
   - Remplacez `<votre_aws_secret>` par votre AWS_SECRET_ACCESS_KEY
   - Sauvegardez avec Ctrl + X, puis Y, puis Enter

### Méthode 2 : Installation manuelle (Pour les utilisateurs avancés)

1. Créez un fichier nommé `.env` :

   - Windows : `notepad .env`
   - Mac/Linux : `nano .env`

2. Copiez ce contenu dans le fichier :

```bash
# Base de données (Ne modifiez pas cette partie)
DATABASE_URL=postgresql://postgres:LeContinent!@hetic.cd5ufp6fsve3.us-east-1.rds.amazonaws.com:5432/mmotors_groupe13

# Configuration AWS (À modifier)
AWS_ACCESS_KEY_ID=<votre_aws_key>        # ← Remplacez par votre clé
AWS_SECRET_ACCESS_KEY=<votre_aws_secret>  # ← Remplacez par votre clé secrète
AWS_REGION=eu-west-3
S3_BUCKET_NAME=mmotors-files-groupe13
```

3. Lancez l'API avec Docker :

```bash
docker run -d --name mmotors-api -p 8000:8000 --env-file .env wissem95/mmotors-api:latest
```

## Vérifier que tout fonctionne

1. Ouvrez votre navigateur web
2. Allez sur : http://localhost:8000/docs
3. Vous devriez voir la documentation de l'API

Si la page ne s'affiche pas :

1. Vérifiez que Docker est bien lancé
2. Dans le terminal, tapez : `docker logs mmotors-api`
3. Regardez s'il y a des messages d'erreur

## Commandes utiles à connaître

Pour voir si l'API fonctionne :

```bash
docker ps
# Vous devriez voir "mmotors-api" dans la liste
```

Pour voir les logs (messages) de l'API :

```bash
docker logs mmotors-api
```

Pour arrêter l'API :

```bash
docker stop mmotors-api
```

Pour redémarrer l'API :

```bash
docker start mmotors-api
```

## Besoin d'aide ?

Si vous rencontrez des problèmes :

1. **Vérifiez les bases :**

   - Docker est-il bien installé et lancé ?
   - Avez-vous bien remplacé les clés AWS ?
   - Le port 8000 est-il disponible ?

2. **Consultez les logs :**

   ```bash
   docker logs mmotors-api
   ```

3. **Contactez-nous :**
   - Ouvrez une issue sur GitHub : https://github.com/TheKyyn/m-motors-backend
   - Décrivez votre problème en détail
   - Incluez les logs d'erreur si possible

## Fonctionnalités disponibles

Une fois l'API installée, vous pourrez :

- Gérer les véhicules (ajouter, modifier, supprimer)
- Uploader des images vers AWS S3
- Gérer l'authentification avec JWT
- Utiliser la base de données PostgreSQL
- Profiter du cache Redis pour de meilleures performances

## Version

- Latest : Version actuelle de l'API
