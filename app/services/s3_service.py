import logging
import uuid
from io import BytesIO
from typing import BinaryIO

import boto3
from botocore.exceptions import ClientError

from app.config import settings

logger = logging.getLogger(__name__)

class S3Service:
    def __init__(self):
        session_kwargs = {"region_name": settings.AWS_REGION}
        
        # Si se definieron credenciales explícitas (desarrollo local), las usamos
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            session_kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
            session_kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
            
        self.s3_client = boto3.client("s3", **session_kwargs)
        self.bucket_name = settings.S3_BUCKET_NAME

    def upload_file(
        self,
        file_obj: BinaryIO | bytes | BytesIO,
        filename: str,
        content_type: str = "image/jpeg",
        folder: str = "products",
    ) -> str:
        """
        Sube un archivo a Amazon S3 con un identificador único (UUID).
        Retorna la URL pública o clave del archivo subido.
        """
        if not self.bucket_name:
            logger.warning("S3_BUCKET_NAME no está configurado. Omitiendo subida a S3.")
            return f"https://placeholder-bucket.s3.amazonaws.com/{folder}/{filename}"

        # Generar nombre único para evitar colisiones
        ext = filename.split(".")[-1] if "." in filename else "jpg"
        unique_key = f"{folder}/{uuid.uuid4().hex}.{ext}"

        try:
            extra_args = {"ContentType": content_type}
            
            if isinstance(file_obj, bytes):
                file_obj = BytesIO(file_obj)

            self.s3_client.upload_fileobj(
                Fileobj=file_obj,
                Bucket=self.bucket_name,
                Key=unique_key,
                ExtraArgs=extra_args,
            )

            file_url = f"https://{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{unique_key}"
            logger.info(f"Archivo subido exitosamente a S3: {file_url}")
            return file_url

        except ClientError as e:
            logger.error(f"Error al subir archivo a S3: {e}")
            raise e

    def delete_file_by_url(self, file_url: str) -> bool:
        """
        Elimina un archivo de S3 a partir de su URL.
        """
        if not self.bucket_name or not file_url or self.bucket_name not in file_url:
            return False

        try:
            # Extraer el key del archivo de la URL
            key = file_url.split(f"{self.bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/")[-1]
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
            logger.info(f"Archivo eliminado de S3: {key}")
            return True
        except ClientError as e:
            logger.error(f"Error al eliminar archivo de S3: {e}")
            return False

s3_service = S3Service()
