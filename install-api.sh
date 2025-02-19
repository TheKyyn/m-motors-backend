#!/bin/bash

# Couleurs pour les logs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Fonction pour la mise à jour
update_api() {
    echo -e "${YELLOW}Mise à jour de M-Motors API...${NC}"
    
    # Vérifier si le conteneur existe
    if docker ps -a | grep -q mmotors-api; then
        echo -e "${YELLOW}Arrêt de l'ancienne instance...${NC}"
        docker stop mmotors-api
        docker rm mmotors-api
    fi
    
    # Supprimer l'ancienne image
    echo -e "${YELLOW}Suppression de l'ancienne version...${NC}"
    docker rmi wissem95/mmotors-api:latest 2>/dev/null
    
    # Télécharger la nouvelle image
    echo -e "${YELLOW}Téléchargement de la nouvelle version...${NC}"
    docker pull wissem95/mmotors-api:latest
    
    # Vérifier si le fichier .env existe
    if [ ! -f .env ]; then
        create_env_file
    fi
    
    # Redémarrer l'API
    echo -e "${YELLOW}Démarrage de la nouvelle version...${NC}"
    docker run -d --name mmotors-api \
        -p 8000:8000 \
        --env-file .env \
        wissem95/mmotors-api:latest
        
    echo -e "${GREEN}Mise à jour terminée !${NC}"
}

# Fonction pour créer le fichier .env
create_env_file() {
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
}

# Fonction pour afficher l'aide
show_help() {
    echo -e "${GREEN}M-Motors API - Script d'installation${NC}"
    echo -e "\nUtilisation :"
    echo -e "  ./install-api.sh [option]"
    echo -e "\nOptions :"
    echo -e "  -h, --help     Affiche cette aide"
    echo -e "  -u, --update   Met à jour l'API vers la dernière version"
    echo -e "  (aucune)       Installation normale"
}

# Traitement des arguments
case "$1" in
    -h|--help)
        show_help
        exit 0
        ;;
    -u|--update)
        update_api
        ;;
    "")
        echo -e "${GREEN}Installation de M-Motors API...${NC}"
        if [ ! -f .env ]; then
            create_env_file
        fi
        update_api
        ;;
    *)
        echo -e "${RED}Option invalide : $1${NC}"
        show_help
        exit 1
        ;;
esac

# Afficher les informations finales
echo -e "\n${GREEN}L'API est accessible sur :${NC}"
echo -e "- API : http://localhost:8000"
echo -e "- Documentation : http://localhost:8000/docs"
echo -e "\n${GREEN}Commandes utiles :${NC}"
echo -e "- Voir les logs : ${YELLOW}docker logs mmotors-api${NC}"
echo -e "- Arrêter l'API : ${YELLOW}docker stop mmotors-api${NC}"
echo -e "- Démarrer l'API : ${YELLOW}docker start mmotors-api${NC}"
echo -e "- Mettre à jour l'API : ${YELLOW}./install-api.sh --update${NC}" 