# M-Motors API

API backend pour l'application M-Motors, un service de location et vente de véhicules.

## Installation automatique (Recommandé)

1. Téléchargez le script d'installation :

```bash
curl -O https://raw.githubusercontent.com/TheKyyn/m-motors-backend/main/install-api.sh
```

2. Rendez-le exécutable :

```bash
chmod +x install-api.sh
```

3. Modifiez les clés AWS dans le script :

```bash
nano install-api.sh
# Remplacez AWS_ACCESS_KEY_ID et AWS_SECRET_ACCESS_KEY par vos clés
```

4. Lancez l'installation :

```bash
./install-api.sh
```

C'est tout ! L'API démarre automatiquement.

## Installation manuelle (Alternative)

Si vous préférez l'installation manuelle :

1. Créez un fichier `.env` avec ce contenu :

```bash
# Base de données
DATABASE_URL=postgresql://postgres:LeContinent!@hetic.cd5ufp6fsve3.us-east-1.rds.amazonaws.com:5432/mmotors_groupe13

# AWS Configuration
AWS_ACCESS_KEY_ID=<votre_aws_key>
AWS_SECRET_ACCESS_KEY=<votre_aws_secret>
AWS_REGION=eu-west-3
S3_BUCKET_NAME=mmotors-files-groupe13
```

2. Lancez l'API :

```bash
docker run -d --name mmotors-api -p 8000:8000 --env-file .env wissem95/mmotors-api:latest
```

## Accès à l'API

L'API sera accessible sur :

- http://localhost:8000
- Documentation Swagger : http://localhost:8000/docs

## Commandes utiles

Voir les logs :

```bash
docker logs mmotors-api
```

Arrêter l'API :

```bash
docker stop mmotors-api
```

Redémarrer l'API :

```bash
docker start mmotors-api
```

## Endpoints principaux

- `POST /auth/token` : Obtenir un token JWT
- `GET /vehicles` : Liste des véhicules
- `POST /vehicles` : Ajouter un véhicule
- `POST /vehicles/{id}/images` : Ajouter une image à un véhicule
- `GET /users/me` : Informations de l'utilisateur connecté

## Support

En cas de problème :

1. Vérifiez que Docker est bien installé et en cours d'exécution
2. Vérifiez que le port 8000 est disponible
3. Consultez les logs avec `docker logs mmotors-api`
4. Contactez l'équipe sur GitHub : https://github.com/TheKyyn/m-motors-backend

## Version

- Latest : Version actuelle de l'API
