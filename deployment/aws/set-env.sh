#!/bin/bash

# Couleurs pour les logs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}Configuration des variables d'environnement pour M-Motors${NC}"

# Chargement des variables depuis .env
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${YELLOW}Fichier .env non trouvé. Consultez le GUIDE_UTILISATION.md pour la configuration.${NC}"
    exit 1
fi

# AWS Account ID
echo -e "${YELLOW}Récupération de l'AWS Account ID...${NC}"
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS_ACCOUNT_ID=${AWS_ACCOUNT_ID}"

# AWS Configuration
export AWS_REGION=eu-west-3
export AWS_DEFAULT_REGION=eu-west-3
echo "AWS_REGION=${AWS_REGION}"

# Mot de passe de la base de données
echo -e "${YELLOW}Configuration du mot de passe RDS...${NC}"
export DB_PASSWORD="LeContinent!"

# Variables pour l'application
export STACK_NAME="mmotors-stack"
export CLOUDFRONT_STACK_NAME="mmotors-cloudfront"
export S3_BUCKET_NAME="mmotors-files-groupe13"
export ECR_REPOSITORY="mmotors-api"

echo -e "${GREEN}Variables d'environnement configurées avec succès :${NC}"
echo "STACK_NAME=${STACK_NAME}"
echo "CLOUDFRONT_STACK_NAME=${CLOUDFRONT_STACK_NAME}"
echo "S3_BUCKET_NAME=${S3_BUCKET_NAME}"
echo "ECR_REPOSITORY=${ECR_REPOSITORY}"
echo "AWS_REGION=${AWS_REGION}"