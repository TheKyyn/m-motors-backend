#!/bin/bash

# Couleurs pour les logs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Installation de M-Motors API...${NC}"

# Créer le fichier .env
echo -e "${YELLOW}Création du fichier .env...${NC}"
cat > .env << EOL
# Base de données
DATABASE_URL=postgresql://postgres:LeContinent!@hetic.cd5ufp6fsve3.us-east-1.rds.amazonaws.com:5432/mmotors_groupe13

# AWS Configuration (à remplir)
AWS_ACCESS_KEY_ID=<votre_aws_key>
AWS_SECRET_ACCESS_KEY=<votre_aws_secret>
AWS_REGION=eu-west-3
S3_BUCKET_NAME=mmotors-files-groupe13
EOL

echo -e "${YELLOW}⚠️  IMPORTANT : Modifiez le fichier .env avec vos clés AWS avant de continuer${NC}"
echo -e "Tapez 'nano .env' pour éditer le fichier"
read -p "Appuyez sur Entrée une fois que vous avez configuré vos clés AWS..."

echo -e "${YELLOW}Arrêt de l'ancienne instance si elle existe...${NC}"
docker rm -f mmotors-api 2>/dev/null

echo -e "${YELLOW}Démarrage de l'API...${NC}"
docker run -d --name mmotors-api \
    -p 8000:8000 \
    --env-file .env \
    wissem95/mmotors-api:latest

echo -e "${GREEN}Installation terminée !${NC}"
echo -e "L'API est accessible sur :"
echo -e "- API : http://localhost:8000"
echo -e "- Documentation : http://localhost:8000/docs"
echo -e "\nCommandes utiles :"
echo -e "- Voir les logs : ${YELLOW}docker logs mmotors-api${NC}"
echo -e "- Arrêter l'API : ${YELLOW}docker stop mmotors-api${NC}"
echo -e "- Démarrer l'API : ${YELLOW}docker start mmotors-api${NC}" 