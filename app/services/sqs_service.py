import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

import boto3
from botocore.exceptions import ClientError

from app.config import settings

logger = logging.getLogger(__name__)

class SQSService:
    def __init__(self):
        session_kwargs = {"region_name": settings.AWS_REGION}
        
        # Si se definieron credenciales explícitas (desarrollo local), las usamos
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            session_kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
            session_kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY

        self.sqs_client = boto3.client("sqs", **session_kwargs)
        self.queue_url = settings.SQS_QUEUE_URL

    def send_event(self, event_type: str, payload: dict[str, Any]) -> str | None:
        """
        Publica un evento asíncrono en Amazon SQS.
        
        :param event_type: Tipo de evento (ej. "PRODUCT_CREATED", "IMAGE_UPLOADED", "STOCK_LOW")
        :param payload: Diccionario con la información del evento
        :return: MessageId retornado por SQS o None si no se envió
        """
        if not self.queue_url:
            logger.warning(
                f"[SQS Mock] SQS_QUEUE_URL no configurada. Evento '{event_type}' simulado en logs: {payload}"
            )
            return "mock-message-id"

        message_body = {
            "event_id": uuid.uuid4().hex,
            "event_type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": payload,
        }

        try:
            response = self.sqs_client.send_message(
                QueueUrl=self.queue_url,
                MessageBody=json.dumps(message_body),
                MessageAttributes={
                    "EventType": {
                        "DataType": "String",
                        "StringValue": event_type,
                    }
                },
            )
            message_id = response.get("MessageId")
            logger.info(f"Evento '{event_type}' enviado a SQS con MessageId: {message_id}")
            return message_id

        except ClientError as e:
            logger.error(f"Error al enviar mensaje a Amazon SQS: {e}")
            # En un sistema desacoplado, no queremos que la falla de SQS rompa la transacción principal
            return None

sqs_service = SQSService()
