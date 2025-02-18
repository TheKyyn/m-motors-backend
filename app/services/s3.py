import boto3
from botocore.exceptions import ClientError
import logging
from ..config import settings
from fastapi import UploadFile
import uuid
from datetime import datetime
from pydantic import SecretStr

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY.get_secret_value() if isinstance(settings.AWS_SECRET_ACCESS_KEY, SecretStr) else settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME

    async def upload_file(self, file: UploadFile, prefix: str) -> str:
        """Upload un fichier vers S3 et retourne son URL"""
        try:
            # Générer un nom de fichier unique
            file_extension = file.filename.split('.')[-1]
            unique_filename = f"{prefix}{uuid.uuid4()}.{file_extension}"
            
            # Upload vers S3
            self.s3_client.upload_fileobj(
                file.file,
                self.bucket_name,
                unique_filename,
                ExtraArgs={
                    'ContentType': file.content_type
                }
            )
            
            # Construire l'URL
            if settings.CLOUDFRONT_DOMAIN:
                url = f"https://{settings.CLOUDFRONT_DOMAIN}/{unique_filename}"
            else:
                url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_filename}"
            
            return url
            
        except ClientError as e:
            logger.error(f"Erreur lors de l'upload vers S3: {str(e)}")
            raise

    async def delete_file(self, file_url: str) -> bool:
        """Supprime un fichier de S3"""
        try:
            # Extraire le nom du fichier de l'URL
            if settings.CLOUDFRONT_DOMAIN:
                key = file_url.split(settings.CLOUDFRONT_DOMAIN + '/')[-1]
            else:
                key = file_url.split(f"{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/")[-1]
            
            # Supprimer de S3
            await self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=key
            )
            return True
            
        except ClientError as e:
            logger.error(f"Erreur lors de la suppression du fichier S3: {str(e)}")
            return False

s3_service = S3Service() 