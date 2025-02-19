#!/bin/bash

echo -e "\n2. Démarrer le conteneur :"
echo -e "   docker run -d --name mmotors-api \\"
echo -e "     -e DATABASE_URL=[Demandez l'URL à l'équipe] \\"
echo -e "     -e AWS_ACCESS_KEY_ID=\${AWS_ACCESS_KEY_ID} \\"
echo -e "     -e AWS_SECRET_ACCESS_KEY=\${AWS_SECRET_ACCESS_KEY} \\"
echo -e "     -e AWS_REGION=\${AWS_REGION} \\"
echo -e "     -e S3_BUCKET_NAME=\${S3_BUCKET} \\"
echo -e "     -p 8000:8000 \${DOCKER_USERNAME}/\${DOCKER_IMAGE}:\${DOCKER_TAG}" 