"""
Worker consumidor de eventos de Amazon SQS.
Puede ejecutarse como proceso en segundo plano o como función AWS Lambda.
"""

import json
import logging
from typing import Any

from app.config import settings
from app.services.sqs_service import sqs_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def process_event(event_type: str, payload: dict[str, Any]) -> None:
    """
    Despacha y procesa la lógica de negocio según el tipo de evento recibido.
    """
    logger.info(f"Procesando evento de tipo: '{event_type}'")

    if event_type == "PRODUCT_CREATED":
        product_id = payload.get("product_id")
        title = payload.get("title")
        logger.info(f" [PRODUCT_CREATED] Notificando creación del producto ID {product_id}: '{title}'")

    elif event_type == "PRODUCT_IMAGE_UPLOADED":
        product_id = payload.get("product_id")
        image_url = payload.get("image_url")
        logger.info(
            f" [IMAGE_PROCESSING] Iniciando redimensionamiento para el producto {product_id} en {image_url}"
        )

    elif event_type == "LOW_STOCK_ALERT":
        product_id = payload.get("product_id")
        stock = payload.get("current_stock")
        logger.warning(
            f"⚠️ [LOW_STOCK_ALERT] ALERTA: Producto ID {product_id} tiene stock crítico ({stock} unidades)"
        )

    else:
        logger.warning(f"Evento no reconocido: {event_type}")

def lambda_handler(event: dict, context: Any) -> dict:
    """
    Handler oficial para AWS Lambda cuando es invocada por triggers de Amazon SQS.
    """
    records = event.get("Records", [])
    logger.info(f"Lambda invocada con {len(records)} mensajes de SQS.")

    for record in records:
        try:
            body = json.loads(record.get("body", "{}"))
            event_type = body.get("event_type")
            payload = body.get("payload", {})
            process_event(event_type, payload)
        except Exception as e:
            logger.error(f"Error procesando mensaje SQS en Lambda: {e}", exc_info=True)
            raise e

    return {"status": "success", "processed_records": len(records)}

def poll_sqs_worker():
    """
    Bucle de escucha continua (Long Polling) para ejecutar como Worker en contenedor Docker.
    """
    if not settings.SQS_QUEUE_URL:
        logger.warning("SQS_QUEUE_URL no configurada. El worker no puede iniciar polling.")
        return

    logger.info(f"Iniciando Long Polling en SQS: {settings.SQS_QUEUE_URL}")
    sqs_client = sqs_service.sqs_client

    while True:
        try:
            response = sqs_client.receive_message(
                QueueUrl=settings.SQS_QUEUE_URL,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=20, 
                AttributeNames=["All"],
                MessageAttributeNames=["All"],
            )

            messages = response.get("Messages", [])
            for message in messages:
                receipt_handle = message.get("ReceiptHandle")
                body = json.loads(message.get("Body", "{}"))
                
                event_type = body.get("event_type")
                payload = body.get("payload", {})
                
                # Procesar lógica de negocio
                process_event(event_type, payload)

                # Eliminar mensaje de la cola tras procesamiento exitoso
                sqs_client.delete_message(
                    QueueUrl=settings.SQS_QUEUE_URL,
                    ReceiptHandle=receipt_handle,
                )
                logger.info(f"Mensaje {message.get('MessageId')} procesado y eliminado de SQS.")

        except Exception as e:
            logger.error(f"Error en el bucle del worker SQS: {e}", exc_info=True)

if __name__ == "__main__":
    poll_sqs_worker()
