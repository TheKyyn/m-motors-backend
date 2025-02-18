# Guide d'Utilisation de l'API M-Motors

## Table des matières

1. [Connexion au serveur Hetic](#connexion-au-serveur-hetic)
2. [Configuration de la base de données](#configuration-de-la-base-de-données)
3. [Création d'un compte administrateur](#création-dun-compte-administrateur)
4. [Connexion](#connexion)
5. [Gestion des véhicules](#gestion-des-véhicules)
   - [Création d'un véhicule](#création-dun-véhicule)
   - [Upload d'images](#upload-dimages)

## Connexion au serveur Hetic

Pour se connecter à la base de données hébergée sur le serveur Hetic, suivez ces étapes :

1. **Prérequis**

   - Avoir PostgreSQL installé sur votre machine

2. **Informations de connexion**

   ```
   Host: hetic.cd5ufp6fsve3.us-east-1.rds.amazonaws.com
   Port: 5432
   Database: mmotors_groupe13
   Username: postgres
   Password: LeContinent!
   ```

3. **Connexion via psql**

   ```bash
   psql "postgresql://postgres:LeContinent!@hetic.cd5ufp6fsve3.us-east-1.rds.amazonaws.com:5432/mmotors_groupe13"
   ```

4. **Connexion via PgAdmin**

   - Ouvrez PgAdmin
   - Cliquez sur "Add New Server"
   - Dans l'onglet "General", mettez exactement comme nom de connexion : `M-Motors Groupe 13`
   - Dans l'onglet "Connection", remplissez les champs avec les informations ci-dessus
   - Cliquez sur "Save"

5. **Test de la connexion**

   ```sql
   -- Une fois connecté, vous pouvez tester avec :
   SELECT current_database(), current_user;
   -- Devrait retourner : mmotors_groupe13, postgres
   ```

6. **En cas de problème de connexion**
   - Vérifiez votre connexion VPN
   - Vérifiez que le port 5432 n'est pas bloqué par votre pare-feu
   - Contactez l'administrateur système si le problème persiste

## Configuration de la base de données

Pour configurer et vous connecter à la base de données PostgreSQL, suivez ces étapes :

1. **Installation de PostgreSQL**

   ```bash
   # Sur MacOS avec Homebrew
   brew install postgresql@15

   # Sur Ubuntu/Debian
   sudo apt-get update
   sudo apt-get install postgresql-15
   ```

2. **Démarrage du service PostgreSQL**

   ```bash
   # Sur MacOS
   brew services start postgresql@15

   # Sur Ubuntu/Debian
   sudo systemctl start postgresql
   ```

3. **Création de la base de données**

   ```bash
   # Se connecter à PostgreSQL
   psql postgres

   # Créer un utilisateur (si nécessaire)
   CREATE USER postgres WITH PASSWORD 'LeContinent!';

   # Créer la base de données
   CREATE DATABASE mmotors_groupe13;

   # Donner les privilèges à l'utilisateur
   GRANT ALL PRIVILEGES ON DATABASE mmotors_groupe13 TO postgres;
   ```

4. **Configuration des variables d'environnement**

   - Créez un fichier `.env` à la racine du projet
   - Ajoutez la ligne suivante :

   ```
   DATABASE_URL=postgresql://postgres:LeContinent!@hetic.cd5ufp6fsve3.us-east-1.rds.amazonaws.com:5432/mmotors_groupe13
   ```

5. **Application des migrations**

   ```bash
   # Installation des dépendances
   pip install -r requirements.txt

   # Exécution des migrations
   alembic upgrade head
   ```

## Création d'un compte administrateur

Pour créer un compte administrateur, envoyez une requête POST à `/users/register` avec les données suivantes :

```bash
curl -X POST http://localhost:8000/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "votre_mot_de_passe",
    "full_name": "Nom Complet",
    "is_admin": true
  }'
```

## Connexion

Pour vous connecter et obtenir un token JWT, utilisez :

```bash
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=votre_mot_de_passe"
```

La réponse contiendra votre token JWT sous la forme :

```json
{
  "access_token": "votre_token_jwt",
  "token_type": "bearer"
}
```

## Gestion des véhicules

### Création d'un véhicule

Pour créer un véhicule, envoyez une requête POST à `/vehicles` avec le token JWT obtenu :

```bash
curl -X POST http://localhost:8000/vehicles \
  -H "Authorization: Bearer votre_token_jwt" \
  -H "Content-Type: application/json" \
  -d '{
    "brand": "BMW",
    "model": "Série 3",
    "year": 2023,
    "mileage": 15000,
    "registration_number": "AA-123-BB",
    "price": 45000,
    "monthly_rental_price": 800,
    "fuel_type": "diesel",
    "transmission": "automatique",
    "engine_size": 2.0,
    "power": 190,
    "doors": 4,
    "seats": 5,
    "color": "noir"
  }'
```

### Upload d'images

Pour ajouter une image à un véhicule, utilisez :

```bash
curl -X POST http://localhost:8000/vehicles/1/images \
  -H "Authorization: Bearer votre_token_jwt" \
  -F "file=@chemin_vers_votre_image.jpg"
```

Note : Remplacez `1` par l'ID du véhicule auquel vous souhaitez ajouter l'image.

## Notes importantes

- Tous les endpoints nécessitant une authentification doivent inclure le header `Authorization: Bearer votre_token_jwt`
- Les tokens JWT expirent après 30 minutes. Il faudra se reconnecter pour obtenir un nouveau token
- Les images doivent être au format JPEG, PNG ou GIF
- La taille maximale des images est limitée à 5 MB

Pour plus d'informations sur l'API, consultez la documentation Swagger à l'adresse : `http://localhost:8000/docs`

## Synchronisation de la base de données

### Base de données partagée RDS

La base de données est hébergée sur AWS RDS et est partagée par toute l'équipe. Cela signifie que :

1. **Une seule base de données** :

   - Tous les membres de l'équipe se connectent à la même base de données
   - URL de connexion : `postgresql://postgres:LeContinent!@hetic.cd5ufp6fsve3.us-east-1.rds.amazonaws.com:5432/mmotors_groupe13`
   - Pas besoin de synchronisation manuelle entre les développeurs

2. **Gestion des migrations** :

   - Les migrations sont gérées avec Alembic
   - Chaque modification de la structure de la base doit passer par une migration
   - Commande pour créer une migration :
     ```bash
     alembic revision --autogenerate -m "description de la modification"
     ```
   - Commande pour appliquer les migrations :
     ```bash
     alembic upgrade head
     ```

3. **Important** :

   - Ne jamais modifier directement la structure de la base sans passer par une migration
   - Toujours créer une migration pour les changements de modèles
   - Communiquer les nouvelles migrations à l'équipe
   - Vérifier que vous êtes à jour avec la commande : `alembic current`

4. **En cas de conflit** :
   - Ne pas essayer de modifier la base manuellement
   - Contacter le responsable de la base de données
   - Créer une nouvelle migration pour corriger le problème

### Base de données locale (pour le développement)

Si vous souhaitez travailler en local :

1. Créez une base locale :

   ```sql
   CREATE DATABASE mmotors_groupe13_local;
   ```

2. Modifiez votre `.env` pour utiliser la base locale :

   ```
   DATABASE_URL=postgresql://postgres:LeContinent!@localhost:5432/mmotors_groupe13_local
   ```

3. Appliquez les migrations :

   ```bash
   alembic upgrade head
   ```

4. Pour revenir sur la base RDS, remettez l'URL RDS dans votre `.env`
